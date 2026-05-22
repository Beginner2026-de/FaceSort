
good pc
python -m nuitka --standalone --onefile --mingw64 --windows-console-mode=disable --enable-plugin=pyside6 --lto=yes  --output-dir=dist .\Start-Ui.py

low mem
python -m nuitka --standalone --onefile --mingw64 --windows-console-mode=disable --enable-plugin=pyside6 --lto=yes --low-memory --jobs=6 --output-dir=dist .\Start-Ui.py


autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive .                                    #

windows 
pyinstaller --onedir --windowed --clean --noconfirm Start-Ui.py