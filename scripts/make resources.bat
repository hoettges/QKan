@echo off
call "C:\Program Files\QGIS 3.40\bin\o4w_env.bat"

@echo on
"C:\Program Files\QGIS 3.40\apps\Python312\Scripts\pyrcc5.exe" -o resources.py resources.qrc