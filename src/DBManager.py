from peewee import ForeignKeyField, fn
import numpy as np
import json
from peewee import SqliteDatabase,Model,CharField,BlobField,TextField,IntegerField,FloatField,BooleanField,CompositeKey

# ======================
# 1. TABELLEN DEFINIEREN (VOR DER KLASSE!)
# ======================
class Image(Model):
    file_name = CharField(unique=True)
    scanned = BooleanField(default=False)
    
    class Meta:
        database = None  # Wird später gesetzt

class Face(Model):
    image = ForeignKeyField(Image, backref='faces')
    embedding = BlobField()  # numpy array als Bytes
    bbox = TextField(null=True)  # JSON-String
    age = IntegerField(null=True)
    gender = CharField(null=True)
    
    class Meta:
        database = None

class Person(Model):
    name = CharField(unique=True)
    haupt_face = ForeignKeyField(Face, null=True, backref='hauptperson')  # Neues Feld
    
    class Meta:
        database = None

class FacePerson(Model):
    face = ForeignKeyField(Face)
    person = ForeignKeyField(Person)
    confidence = FloatField(null=True)
    
    class Meta:
        database = None
        primary_key = CompositeKey('face', 'person')

# ======================
# 2. FACEDB KLASSE
# ======================
class FaceDB:
    def __init__(self, db_path="faces.db"):
        self.db = SqliteDatabase(db_path)
        
        # Modelle mit Datenbank verbinden
        for model in [Image, Face, Person, FacePerson]:
            model._meta.database = self.db
        
        self.db.connect()
        self.db.create_tables([Image, Face, Person, FacePerson])
        self._ensure_image_scanned_column()
    
    def _column_exists(self, model, column_name):
        cursor = self.db.execute_sql(f"PRAGMA table_info({model._meta.table_name})")
        return any(row[1] == column_name for row in cursor.fetchall())

    def _ensure_image_scanned_column(self):
        if not self._column_exists(Image, "scanned"):
            self.db.execute_sql(
                f"ALTER TABLE {Image._meta.table_name} ADD COLUMN scanned INTEGER DEFAULT 0"
            )

    def is_image_scanned(self, image_id):
        image = Image.get_or_none(Image.id == image_id)
        return bool(image and image.scanned)

    # -------------------------
    # IMAGE
    # -------------------------
    def add_image(self, file_name):
        image, _ = Image.get_or_create(
            file_name=file_name
        )
        return image
    
    # -------------------------
    # FACE (mehrere Gesichter speichern)
    # -------------------------
    def add_faces(self, image, faces_list):
        """Speichert mehrere Gesichter zu einem Bild"""
        image_model = Image.get_by_id(image["image_id"])
        saved_face_ids = []
        for face_data in faces_list:
            face, _ = Face.get_or_create(
                image=image_model,
                embedding=face_data['embedding'].tobytes(),
                bbox=json.dumps(face_data['bbox']),
                age=face_data.get('age'),
                gender=face_data.get('gender')
            )
            saved_face_ids.append(face.id)

        if image_model:
            image_model.scanned = True
            image_model.save()

        return saved_face_ids
    
    def get_faces_by_image(self, file_name):
        image = Image.get(Image.file_name == file_name)

        return [
            self._face_to_dto(face)
            for face in image.faces
        ]

    def get_all_faces(self):
        return [
            self._face_to_dto(face)
            for face in Face.select()
        ]

    def get_unassigned_faces(self):
        query = (
            Face
            .select()
            .where(~Face.id.in_(
                FacePerson.select(FacePerson.face)
            ))
        )

        return [self._face_to_dto(face) for face in query]
    
    # -------------------------
    # PERSON
    # -------------------------
    def merge_persons(self, source_name, target_name):

        source = Person.get_or_none(Person.name == source_name)
        target = Person.get_or_none(Person.name == target_name)

        if not source or not target:
            return {"success": False}

        with self.db.atomic():

            (FacePerson
            .update(person=target)
            .where(FacePerson.person == source)
            .execute())

            if source.haupt_face and not target.haupt_face:
                target.haupt_face = source.haupt_face
                target.save()

            source.delete_instance()

        return {"success": True}

    def rename_person(self, old_name: str, new_name: str):
        # alte Person holen
        person = Person.get_or_none(Person.name == old_name)

        if person is None:
            return {
                "success": False,
                "error": "Person nicht gefunden"
            }

        # prüfen ob neuer Name schon existiert
        exists = Person.get_or_none(Person.name == new_name)
        if exists:
            return {
                "success": False,
                "error": "Name bereits vergeben"
            }

        # update
        person.name = new_name
        person.save()

        return {
            "success": True,
            "old_name": old_name,
            "new_name": new_name
        }

    def get_faces_by_person(self, person_name):
        person = Person.get_or_none(name=person_name)
        if not person:
            return []
        return [fp.face.id for fp in FacePerson.select().where(FacePerson.person == person)]

    def get_face_embedding(self, face_id):
        face = Face.get_by_id(face_id)
        if isinstance(face.embedding, bytes):
            # Direkt von Bytes zu numpy array
            return np.frombuffer(face.embedding, dtype=np.float32)
        return face.embedding
    
    def create_person(self, name):
        person, _ = Person.get_or_create(name=name)
        return person
    
    def assign_face_to_person(self, face_id, person_name, confidence=None):
        person = self.create_person(person_name)
        FacePerson.insert(
            face=face_id,
            person=person.id,
            confidence=confidence
        ).on_conflict_ignore().execute()

    def get_all_person_names(self):
        return [person.name for person in Person.select()]

    def get_person_hauptbild_data(self, person_name):
        person = Person.get_or_none(Person.name == person_name)

        if not person or not person.haupt_face:
            return []

        face = person.haupt_face

        return self._face_to_dto(face, person_name)

    def set_haupt_bild_zu_person(self, person_name, image_path: str = ""):
        """Setzt Hauptbild einer Person. Ohne image_path wird das Gesicht mit der höchsten Confidence gewählt."""
        person = Person.get_or_none(Person.name == person_name)
        if person is None:
            return {
                "success": False,
                "error": "Person nicht gefunden"
            }

        if image_path == "":
            # Erstes zugeordnetes Gesicht nach höchster Confidence nehmen
            face_person = (
                FacePerson
                .select()
                .where(FacePerson.person == person)
                .order_by(FacePerson.confidence.desc())
                .first()
            )
            if face_person:
                person.haupt_face = face_person.face
                person.save()
                return {"success": True}
            return {"success": False, "error": "Keine Gesichter für Person gefunden"}

        face = (
            Face
            .select()
            .join(Image)
            .switch(Face)
            .join(FacePerson)
            .join(Person)
            .where(
                (Image.file_name == image_path) &
                (Person.name == person_name)
            )
            .get()
        )

        person.haupt_face = face
        person.save()
        return {"success": True}

    def delete_person_by_name(self, person_name):
        """Löscht eine Person und alle Zuordnungen, aber nicht die Bilder oder Gesichter"""
        person = Person.get_or_none(Person.name == person_name)
        if not person:
            return {"success": False, "error": "Person nicht gefunden"}

        with self.db.atomic():
            FacePerson.delete().where(FacePerson.person == person).execute()
            person.delete_instance()

        return {"success": True}
    
    def get_images_by_persons(
        self,
        person_names_included: list[str],
        person_names_excluded: list[str] = [],
        max_other_persons: int = 0
    ) -> list[str]:

        if not person_names_included:
            return []

        required_count = len(person_names_included)

        # ------------------------------------------------------------------
        # Bilder finden, die ALLE gewünschten Personen enthalten
        # ------------------------------------------------------------------
        query = (
            Image
            .select(Image)
            .join(Face)
            .join(FacePerson)
            .join(Person)
            .where(Person.name.in_(person_names_included))
            .group_by(Image.id)
            .having(fn.COUNT(fn.DISTINCT(Person.id)) == required_count)
        )

        if person_names_excluded:
            excluded_images = (
                Image
                .select(Image.id)
                .join(Face)
                .join(FacePerson)
                .join(Person)
                .where(Person.name.in_(person_names_excluded))
            )
            query = query.where(Image.id.not_in(excluded_images))

        matching_images = []

        # ------------------------------------------------------------------
        # Prüfen wie viele Personen insgesamt auf dem Bild sind
        # ------------------------------------------------------------------
        for image in query:
            all_persons_query = (
                Person
                .select(Person.id)
                .join(FacePerson)
                .join(Face)
                .where(Face.image == image)
                .distinct()
            )

            total_persons = all_persons_query.count()
            other_persons = total_persons - required_count

            if other_persons <= max_other_persons:
                matching_images.append(image)

        return [img.file_name for img in matching_images]
    
    # -------------------------
    # IMAGE QUERIES
    # -------------------------
    def get_all_persons_images(self, person_name):
        """Gibt alle ORIGINAL-Bilder einer Person zurück"""
        person = Person.get_or_none(Person.name == person_name)
        if person is None:
            return []
        return list(Image
                    .select()
                    .join(Face)
                    .join(FacePerson)
                    .join(Person)
                    .where(Person.name == person_name))
    
    def get_all_persons_faces(self, person_name):
        person = Person.get_or_none(Person.name == person_name)
        if person is None:
            return []

        query = (
            Face
            .select(Face, Image)
            .join(Image)
            .switch(Face)
            .join(FacePerson)
            .join(Person)
            .where(Person.name == person_name)
        )

        return [
            self._face_to_dto(face, person_name)
            for face in query
        ]
        

    
    def get_all_images(self):
        """Gibt alle Bilder als DTO zurück"""

        result = []

        for image in Image.select():
            result.append({
                "image_id": image.id,
                "image_path": image.file_name,
                "bbox" : None
            })

        return result
    
    def get_person_image_count(self, person_name):
        """Gibt die Anzahl der Bilder zurück"""
        person = Person.get_or_none(Person.name == person_name)
        if person is None:
            return 0
        return (Image
                .select()
                .join(Face)
                .join(FacePerson)
                .join(Person)
                .where(Person.name == person_name)
                .count())
    
    def get_person_face_count(self, person_name):
        """Gibt die Anzahl der Gesichter einer Person zurück"""
        person = Person.get_or_none(Person.name == person_name)
        if person is None:
            return 0
        return (Face
                .select()
                .join(FacePerson)
                .join(Person)
                .where(Person.name == person_name)
                .count())

    def _face_to_dto(self, face, person_name=None):
        return {
            "face_id": face.id,
            "image_path": face.image.file_name,
            "bbox": json.loads(face.bbox) if face.bbox else None,
            "embedding": face.embedding,
            "person_name": person_name
        }