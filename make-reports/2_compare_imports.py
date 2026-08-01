import os
from pathlib import Path

def load_set(path):
    with open(path) as f:
        return set(line.strip() for line in f if line.strip())

path_for_os = "make-reports/windows" if os.name == "nt" else "make-reports/linux"

runtime = load_set(Path(f"{path_for_os}/runtime_imports.txt"))


nuitka = load_set(Path(f"{path_for_os}/report_all_imports_clean.txt"))

unused = nuitka - runtime
includ_imports = ["fnmatch","multiprocessing","pathlib"]

with open(Path(f"{path_for_os}/nofollow_suggestions.txt"), "w") as f:
    for m in sorted(unused):
        skip = False

        for i in includ_imports:
            if i in m:
                print(f"--> Ignoring {i} import: {m}")
                skip = True
                break

        if skip:
            continue

        f.write(f"--nofollow-import-to={m}\n")

print("fertig → nofollow_suggestions.txt")