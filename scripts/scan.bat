rem Link-Datei "Scan.bat #" auf u.g. Verzeichnis "C:\FHAC\hoettges\Kanalprogramme\k_qkan\security" ausführen

mkdir C:\FHAC\hoettges\Kanalprogramme\k_qkan\security\aktuell
"C:\Program Files\Python311\Scripts\bandit" -r qkan >C:\FHAC\hoettges\Kanalprogramme\k_qkan\security\aktuell\erg_bandit.txt
"C:\Program Files\Python311\Scripts\detect-secrets" scan qkan >C:\FHAC\hoettges\Kanalprogramme\k_qkan\security\aktuell\erg_detect.txt
"C:\Program Files\Python311\Scripts\flake8" qkan >C:\FHAC\hoettges\Kanalprogramme\k_qkan\security\aktuell\erg_flake8.txt

rem Verzeichnis "aktuell" umbenennen zu aktuellem Datum
rem jh, 04.07.2026
