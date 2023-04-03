# coding utf-8
__author__ = 'Jörg Höttges, FH Aachen'

# Prüft in allen *.rst-Dateien die Einträge hinter ".. image::" auf Existenz

import os

with open('liste_fehlende_png.log', 'w') as ergdatei:
    ergdatei.write('Kontrolle der image-Einträge\n\n')
    for file in os.scandir():
        if file.is_file() and file.name.endswith('.rst'):
            with open(file) as rstfile:
                for zeile in rstfile:
                    if '.. image' in zeile:
                        file = zeile.replace('.. image:: ', '').strip()
                        if not os.path.exists(file):
                            ergdatei.write(f'Bilddatei {file} fehlt.\n')
