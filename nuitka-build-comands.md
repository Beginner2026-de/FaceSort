python -m nuitka --standalone --enable-plugin=pyside6 --windows-console-mode=disable .\Start-Ui.pyyes
python -m nuitka --standalone  --enable-plugin=pyside6 --onefile --lto=no --disable-ccache .\Start-Ui.py
python -m nuitka --standalone --onefile --mingw64 --windows-console-mode=disable --enable-plugin=pyside6 --lto=yes --output-dir=dist .\Start-Ui.py