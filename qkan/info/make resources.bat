@echo off
call "C:\Program Files\QGIS 3.22.7\bin\o4w_env.bat"
call "C:\Program Files\QGIS 3.22.7\bin\qt5_env.bat"
call "C:\Program Files\QGIS 3.22.7\bin\py3_env.bat"

@echo on
"C:\Program Files\QGIS 3.22.7\apps\Python39\Scripts\pyrcc5.exe" -o resources.py resources.qrc