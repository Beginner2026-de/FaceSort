import numpy as np
import json
from peewee import *

# ======================
# 1. TABELLEN DEFINIEREN (VOR DER KLASSE!)
# ======================
class Image(Model):
    file_name = CharField(unique=True)
    
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
        for face_data in faces_list:
            Face.get_or_create(
                image=image,
                embedding=face_data['embedding'].tobytes(),
                bbox=json.dumps(face_data['bbox']),
                age=face_data.get('age'),
                gender=face_data.get('gender')
            )
        return 
    
    def get_faces_by_image(self, file_name):
        image = Image.get(Image.file_name == file_name)
        faces = []
        for face in image.faces:
            # Embedding zurückkonvertieren
            embedding = np.frombuffer(face.embedding, dtype=np.float32)
            bbox = json.loads(face.bbox) if face.bbox else None
            faces.append({
                'id': face.id,
                'embedding': embedding,
                'bbox': bbox,
                'age': face.age,
                'gender': face.gender
            })
        return faces
    
    # -------------------------
    # PERSON
    # -------------------------
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
    
    # -------------------------
    # SEARCH
    # -------------------------
    def get_images_by_person(self, name):
        return (Image
                .select()
                .join(Face)
                .join(FacePerson)
                .join(Person)
                .where(Person.name == name))

    def get_all_images(self):
        return(Image.select())