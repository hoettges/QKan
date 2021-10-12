rem @echo off
rem Root OSGEO4W home dir to the same directory this script exists in
pushd C:\Program Files\QGIS 3.20.1

call "bin\o4w_env.bat"
popd
"C:\Program Files\QGIS 3.20.1\apps\Python39\Scripts\pyrcc5.exe" -o resources.py resources.qrc

