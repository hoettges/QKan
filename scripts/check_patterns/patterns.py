# Prüfung der Tabellen und Attribute für die Clipboard-Funktion

import os
import sys
import re
import logging
import argparse
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

QKAN_PATH = Path.cwd() / '..' / '..' / 'qkan'
# QKAN_PATH = Path('C:/FHAC/hoettges/Kanalprogramme/QKan/qkan')

import re

def attribute_aus_datainsert_table(sql: str):
    """
    Liest aus einer INSERT-INTO-TABLE-Anweisung die
    Namen der Spalten aus.

    Rückgabe:
        attributliste

    Tabellen-Constraints wie PRIMARY KEY (...), FOREIGN KEY (...),
    UNIQUE (...), CHECK (...) und CONSTRAINT ... werden ignoriert.
    """

    # SQL-Kommentare im Format /* ... */ entfernen
    sql_ohne_kommentare = re.sub(
        r"/\*.*?\*/",
        "",
        sql,
        flags=re.DOTALL
    )

    # Tabellennamen nach INSERT INTO ermitteln.
    # Namen können unquotiert, "..."-, `...`-
    # oder [...]-notiert sein.
    treffer_tabelle = re.search(
        r"""
        \bINSERT\s+INTO\s+
        (
            "(?:[^"]|"")*"      |
            `(?:[^`]|``)*`      |
            \[(?:[^\]]|\]\])*\] |
            [^\s(]+
        )
        """,
        sql_ohne_kommentare,
        flags=re.IGNORECASE | re.VERBOSE
    )

    if not treffer_tabelle:
        raise ValueError("Tabellenname in der INSERT-INTO-Anweisung nicht gefunden.")

    tabellenname = _sql_identifier_entquoten(treffer_tabelle.group(1))

    # Bereich der Spaltendefinitionen bestimmen
    start = sql_ohne_kommentare.find("(", treffer_tabelle.end())
    ende = sql_ohne_kommentare.find(")")

    if start == -1 or ende == -1 or ende <= start:
        raise ValueError("Keine gültige Liste von Spaltendefinitionen gefunden.")

    definitionen = sql_ohne_kommentare[start + 1:ende]

    # An Kommata auf oberster Klammer-Ebene teilen
    teile = _sql_teile_auf_oberster_ebene(definitionen)

    return teile

def tabellenname_und_attribute_aus_create_table(sql: str) -> tuple[str, list[str]]:
    """
    Liest aus einer CREATE-TABLE-Anweisung den Tabellennamen sowie die
    Namen der Spalten aus.

    Rückgabe:
        (tabellenname, attributliste)

    Tabellen-Constraints wie PRIMARY KEY (...), FOREIGN KEY (...),
    UNIQUE (...), CHECK (...) und CONSTRAINT ... werden ignoriert.
    """

    # SQL-Kommentare im Format /* ... */ entfernen
    sql_ohne_kommentare = re.sub(
        r"/\*.*?\*/",
        "",
        sql,
        flags=re.DOTALL
    )

    # Tabellennamen nach CREATE TABLE ermitteln.
    # IF NOT EXISTS ist optional; Namen können unquotiert, "..."-, `...`-
    # oder [...]-notiert sein.
    treffer_tabelle = re.search(
        r"""
        \bCREATE\s+TABLE\s+
        (?:IF\s+NOT\s+EXISTS\s+)?
        (
            "(?:[^"]|"")*"      |
            `(?:[^`]|``)*`      |
            \[(?:[^\]]|\]\])*\] |
            [^\s(]+
        )
        """,
        sql_ohne_kommentare,
        flags=re.IGNORECASE | re.VERBOSE
    )

    if not treffer_tabelle:
        raise ValueError("Tabellenname in der CREATE-TABLE-Anweisung nicht gefunden.")

    tabellenname = _sql_identifier_entquoten(treffer_tabelle.group(1))

    # Bereich der Spaltendefinitionen bestimmen
    start = sql_ohne_kommentare.find("(", treffer_tabelle.end())
    ende = sql_ohne_kommentare.rfind(")")

    if start == -1 or ende == -1 or ende <= start:
        raise ValueError("Keine gültige Liste von Spaltendefinitionen gefunden.")

    definitionen = sql_ohne_kommentare[start + 1:ende]

    # An Kommata auf oberster Klammer-Ebene teilen
    teile = _sql_teile_auf_oberster_ebene(definitionen)

    # Schlüsselwörter, mit denen Tabellen-Constraints beginnen
    constraint_starter = {
        "PRIMARY",
        "FOREIGN",
        "UNIQUE",
        "CHECK",
        "CONSTRAINT",
        "EXCLUDE",
    }

    attribute = []

    for definition in teile:
        if not definition:
            continue

        erstes_wort = definition.split(maxsplit=1)[0].upper()

        # Kein Attribut, sondern z. B. PRIMARY KEY (pk)
        if erstes_wort in constraint_starter:
            continue

        treffer_attribut = re.match(
            r"""
            \s*
            (
                "(?:[^"]|"")*"      |
                `(?:[^`]|``)*`      |
                \[(?:[^\]]|\]\])*\] |
                [^\s]+
            )
            """,
            definition,
            flags=re.VERBOSE
        )

        if not treffer_attribut:
            raise ValueError(
                f"Spaltendefinition konnte nicht gelesen werden: {definition!r}"
            )

        attribute.append(_sql_identifier_entquoten(treffer_attribut.group(1)))

    return tabellenname, attribute


def _sql_identifier_entquoten(name: str) -> str:
    """Entfernt optionale SQL-Begrenzer von einem Bezeichner."""

    if name.startswith('"') and name.endswith('"'):
        return name[1:-1].replace('""', '"')

    if name.startswith("`") and name.endswith("`"):
        return name[1:-1].replace("``", "`")

    if name.startswith("[") and name.endswith("]"):
        return name[1:-1].replace("]]", "]")

    return name


def _sql_teile_auf_oberster_ebene(text: str) -> list[str]:
    """
    Teilt eine SQL-Spaltendefinitionsliste an Kommata, jedoch nicht
    innerhalb von Klammern oder Zeichenketten.
    """

    teile = []
    aktueller_teil = []
    klammertiefe = 0
    quote = None
    i = 0

    while i < len(text):
        zeichen = text[i]

        if quote is not None:
            aktueller_teil.append(zeichen)

            if zeichen == quote:
                # SQL-Escaping: '' bzw. "" und `` innerhalb quotierter Werte
                if i + 1 < len(text) and text[i + 1] == quote:
                    aktueller_teil.append(text[i + 1])
                    i += 1
                else:
                    quote = None

        elif zeichen in ("'", '"', "`"):
            quote = zeichen
            aktueller_teil.append(zeichen)

        elif zeichen == "[":
            quote = "]"
            aktueller_teil.append(zeichen)

        elif zeichen == "(":
            klammertiefe += 1
            aktueller_teil.append(zeichen)

        elif zeichen == ")":
            klammertiefe -= 1
            aktueller_teil.append(zeichen)

        elif zeichen == "," and klammertiefe == 0:
            teile.append("".join(aktueller_teil).strip())
            aktueller_teil = []

        else:
            aktueller_teil.append(zeichen)

        i += 1

    letzter_teil = "".join(aktueller_teil).strip()
    if letzter_teil:
        teile.append(letzter_teil)

    return teile

def main(filepatterns: Path, filesql: Path):

    with open('check_patterns.log', 'w') as ferg:
        with open(filepatterns) as fpat:
            patternDict = yaml.safe_load(fpat.read())
            with open(filesql) as fsql:
                sqlDict = yaml.safe_load(fsql.read())

                # 1. Patterns auf Vollständigkeit prüfen
                ferg.write(f'Prüfung der Patterns in der Datei {filepatterns}\n\n')
                akttab = None           # Für die Ausgabe: Einmalig Tabellenname ausgeben
                for key in sqlDict:
                    sql = sqlDict[key]
                    if sql.strip().startswith("CREATE TABLE "):
                        tablename, attributes = tabellenname_und_attribute_aus_create_table(sql)
                        pattrs = patternDict.get(tablename)
                        if pattrs is None:
                            ferg.write(f'{tablename:53} - Tabelle fehlt\n')
                            continue
                        for attr in attributes:
                            # pk und Geo-Attribute nicht prüfen
                            if attr == "pk" or \
                                attr.startswith("geo") or \
                                attr.startswith("gli") or \
                                attr.startswith("gbuf"):
                                continue
                            if attr not in pattrs:
                                if akttab != tablename:
                                    akttab = tablename
                                    ferg.write(f'{tablename}\n')
                                ferg.write(f' - {attr:50} - fehlt\n')

                # 2. insert_data-Anweisungen auf Vollständigkeit prüfen
                ferg.write(f'\n\nPrüfung der insert_data-Anweisungen in der Datei {filesql}\n\n')
                akttab = None           # Für die Ausgabe: Einmalig Tabellenname ausgeben
                for key in sqlDict:
                    sql = sqlDict[key]
                    if sql.strip().startswith("CREATE TABLE "):
                        tablename, attributes = tabellenname_und_attribute_aus_create_table(sql)
                        sqlins = sqlDict.get(f'database_insertdata_{tablename}')
                        if sqlins is None:
                            ferg.write(f'database_insertdata_{tablename:33} - SQL-Anweisung fehlt\n')
                            continue
                        insattrs = attribute_aus_datainsert_table(sqlins)
                        for attr in attributes:
                            # pk und Geo-Attribute nicht prüfen
                            if attr == "pk" or \
                                attr.startswith("geo") or \
                                attr.startswith("gli") or \
                                attr.startswith("gbuf"):
                                continue
                            if attr not in insattrs:
                                if akttab != tablename:
                                    akttab = tablename
                                    ferg.write(f'database_insertdata_{tablename:33}\n')
                                ferg.write(f' - {attr:50} - fehlt\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="CheckPatterns",
        description="Prüft Tabellenattribute der Clipboard-Funktion gegen die CREATE-Anweisungen des Moduls qkan.database in der Datei sqlite.yml.",
        epilog="Das Programm wird für jedes QKan-Release benötigt"
    )

    parser.add_argument(
        "-o", "--ordner",
        type=Path,
        default=QKAN_PATH,
        required=False,
        help="Verzeichnis des QKan-Plugins (Standard: ORDNER/{QKAN_PATH}).",
    )

    args = parser.parse_args()

    basis = args.ordner.expanduser().resolve()

    if not basis.is_dir():
        print(f"FEHLER: Kein existierender Ordner: {basis}", file=sys.stderr)

    filesql = basis / 'database\sqlite.yml'
    filepatterns =      basis / 'patterns.yml'

    logger.info(f'Vergleiche {filepatterns} und {filesql}')

    main(filepatterns, filesql)
