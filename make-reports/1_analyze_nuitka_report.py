import lxml.etree as etree
from collections import Counter
import os
from pathlib import Path


def parse_report(path):
    parser = etree.XMLParser(recover=True, encoding="utf-8")

    tree = etree.parse(path, parser)
    root = tree.getroot()

    modules = []

    for node in root.iter():
        # lxml gibt tag ggf. als bytes oder mit namespace → absichern
        tag = node.tag

        if isinstance(tag, bytes):
            tag = tag.decode()

        if "module_usage" in tag:
            name = node.attrib.get("name")
            if name:
                modules.append(name)

    return Counter(modules)


def save_top_modules(report, out):
    c = parse_report(report)

    with open(out, "w", encoding="utf-8") as f:
        for mod, count in c.most_common(300):
            f.write(f"{mod}\n")


if __name__ == "__main__":
    #go in folder make-reports/windows or linux
    path_for_os = "make-reports/windows" if os.name == "nt" else "make-reports/linux"
    save_top_modules(Path(f"{path_for_os}/report_all_imports.xml"), Path(f"{path_for_os}/report_all_imports_clean.txt"))