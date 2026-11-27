from typing import List

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.core import Qgis

from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.tools.qkan_utils import checknames, fortschritt
from qkan.linkflaechen.updatelinks import updatelinkfl
from qkan.utils import get_logger
from qkan.datacheck.application import Plausi

logger = get_logger("QKan.he8.export")

# noinspection SqlNoDataSourceInspection, SqlResolve
class ExportTask:
    def __init__(self, db_qkan: DBConnection):

        self.db_qkan = db_qkan

        self.append = QKan.config.check_export.append
        self.update = QKan.config.check_export.update

        self.nextid = 0

    def run(self) -> bool:
        """
        Export der Kanaldaten aus einer QKan-SpatiaLite-Datenbank und Schreiben in
        eine HE_SpatiaLite-Datenbank
        """
        iface = QKan.instance.iface

        # Create progress bar
        self.progress_bar = QProgressBar(iface.messageBar())
        self.progress_bar.setRange(0, 100)

        status_message = iface.messageBar().createMessage(
            "", "Export in Arbeit. Bitte warten..."
        )
        status_message.layout().addWidget(self.progress_bar)
        iface.messageBar().pushWidget(status_message, Qgis.MessageLevel.Info, 10)

        # --------------------------------------------------------------------------------------------
        # Besonderes Gimmick des ITWH-Programmiers: Die IDs der Tabellen muessen sequentiell
        # vergeben werden!!! Ein Grund ist, dass (u.a.?) die Tabelle "tabelleninhalte" mit verschiedenen
        # Tabellen verknuepft ist und dieser ID eindeutig sein muss.

        self.db_qkan.loadmodule('he8porter')

        if not self._check_complete():
            logger.warning("Die Daten sind noch nicht vollständig (siehe Fehlerliste). Export nicht möglich!")

        self.db_qkan.sqlyml('he8_get_id', 'id der HE-idbm-Datenbank lesen')
        data = self.db_qkan.fetchone()
        if not data:
            logger.error(
                "he8porter._export.run: Abfrageergebnis ist leer: {data}"
            )
        self.nextid = int(data[0]) + 1
        he_db_version = data[1].split(".")
        logger.debug(f"HE IDBF-Version {he_db_version}")

        # Export
        result = all(
            [
                # self._profile(),
                self._bodenklassen(),
                self._abflussparameter(),
                self._schaechte(),              # 30%
                self._auslaesse(),
                self._speicher(),
                self._haltungen(),              # 60%
                self._wehre(),
                self._pumpen(),
                self._drosseln(),
                self._schieber(),
                self._qregler(),
                self._hregler(),
                self._grundseitenauslaesse(),
                self._flaechen(),               # 95%
                # self._einleitdirekt(),
                # self._aussengebiete(),
                # self._einzugsgebiet(),
                self._tezg(),                   # 100%
            ]
        )

        self.progress_bar.setValue(100)
        status_message.setText("Datenexport abgeschlossen.")

        return result

        # fortschritt("Ende...", 1)
        # self.progress_bar.setValue(100)
        # status_message.setText("Datenexport abgeschlossen.")
        # status_message.setLevel(Qgis.MessageLevel.Success)

    def _schaechte(self) -> bool:
        """Export Schächte"""

        if QKan.config.check_export.schaechte:
            # Nur Daten fuer ausgewaehlte Teilgebiete, gilt nur für
            # schaechte, auslaesse, speicher

            if self.update:
                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_update_sel_schaechte'
                else:
                    sqlnam = 'he8_update_schaechte_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_schaechte (1)"
                ):
                    logger.error_data('Export Update Schächte ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")

            if self.append:
                # Feststellen der Anzahl Schächte in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: export_to_he8.export_schaechte (2)"
                ):
                    logger.error_data('Abfrage Anzahl Schächte in HE8-Datenbank ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_sel_schaechte'
                else:
                    sqlnam = 'he8_append_schaechte_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_schaechte (3)",
                    parameters={'nr0': nr0}
                ):
                    logger.error_data('Einfügen Schächte in HE8-Datenbank ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")

                if not self.db_qkan.sqlyml(
                    'he8_count_he_schaechte',
                    "db_qkan: Gesamtzahl Schächte nach Einfügen"
                ):
                    logger.error_data('Gesamtzahl Schächte nach Einfügen ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Schächte eingefügt", 0.30)
                self.progress_bar.setValue(30)
        return True

    def _speicher(self) -> bool:
        """Export Speicherbauwerke"""

        if QKan.config.check_export.speicher:
            # Nur Daten fuer ausgewaehlte Teilgebiete, gilt nur für
            # schaechte, auslaesse, speicher

            if self.update:
                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_update_speicher_sel'
                else:
                    sqlnam = 'he8_update_speicher_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_speicher (1)"
                ):
                    logger.error_data('Export Update Speicher ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")

            if self.append:
                # Feststellen der Anzahl Speicherschächte in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_speicher',
                    "db_qkan: export_to_he8.export_speicherschaechte (1)"
                ):
                    logger.error_data('Abfrage Anzahl Speicher in HE8-Datenbank ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_speicher_sel'
                else:
                    sqlnam = 'he8_append_speicher_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_speicher (1)",
                    parameters={'nr0': nr0}
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_speicher',
                    "db_qkan: export_to_he8.export_speicherschaechte (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Speicherschächte eingefügt", 0.34)
                self.progress_bar.setValue(34)
        return True

    def _auslaesse(self) -> bool:
        """Export Auslässe"""

        if QKan.config.check_export.auslaesse:
            # Nur Daten fuer ausgewaehlte Teilgebiete, gilt nur für
            # schaechte, auslaesse, speicher

            if self.update:
                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_update_auslaesse_sel'
                else:
                    sqlnam = 'he8_update_auslaesse_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_auslaesse (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Auslässe in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_auslaesse',
                    "db_qkan: export_to_he8.export_auslaesse (1)"
                ):
                    logger.error_data('Abfrage Anzahl Auslässe in HE8-Datenbank ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_auslaesse_sel'
                else:
                    sqlnam = 'he8_append_auslaesse_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_auslaesse (2)",
                    parameters={'nr0': nr0}
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_auslaesse',
                    "db_qkan: export_to_he8.export_auslaesse (2)"
                ):
                    logger.error_data('Gesamtzahl Auslässe nach Einfügen ist fehlgeschlagen')
                    raise Exception(f"{self.__class__.__name__}")
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Auslässe eingefügt", 0.32)
                self.progress_bar.setValue(32)
        return True

    def _haltungen(self) -> bool:
        """Export Haltungen"""

        if QKan.config.check_export.haltungen:
            if self.update:
                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_update_sel_haltungen'
                else:
                    sqlnam = 'he8_update_haltungen_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_haltungen (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Haltungen in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_haltungen',
                    "db_qkan: export_to_he8.export_haltungen (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_sel_haltungen'
                else:
                    sqlnam = 'he8_append_haltungen_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_haltungen (3)",
                    parameters={'nr0': nr0}
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_haltungen',
                    "db_qkan: export_to_he8.export_haltungen (4)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Haltungen eingefügt", 0.70)
                self.progress_bar.setValue(70)
        return True

    def _flaechen(self) -> bool:
        """Export Flächenobjekte"""

        if QKan.config.check_export.flaechen:

            mindestflaeche = QKan.config.mindestflaeche
            autokorrektur = QKan.config.autokorrektur
            fangradius = QKan.config.fangradius
            mit_verschneidung = QKan.config.mit_verschneidung

            nr0 = None  # Für Fortschrittsmeldung

            # Vorbereitung flaechen: Falls flnam leer ist, plausibel ergänzen:
            if not checknames(self.db_qkan, "flaechen", "flnam", "f_", autokorrektur):
                return False

            if not updatelinkfl(self.db_qkan, fangradius):
                logger.error_code(
                    "Fehler beim Update der Flächen-Verknüpfungen\n"
                    "Der logische Cache konnte nicht aktualisiert werden."
                )
                raise Exception(f"{self.__class__.__name__}")

            self.db_qkan.loadmodule('he8porter')              # zusätzlich in application_dialog.py
            if self.update:
                # aus Performancegründen wird die Auswahl der zu bearbeitenden Flächen in eine
                # temporäre Tabelle flupdate geschrieben

                if not self.db_qkan.sqlyml(
                    'he8_createtable_flupdate',
                    "db_qkan: export_to_he8.export_flaechen (1)",
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_resettable_flupdate',
                    "db_qkan: export_to_he8.export_flaechen (1)",
                ):
                    return False

                if QKan.config.selections.selectedObjects:
                    if mit_verschneidung:
                        sqlnam = 'he8_flupdate_mitversch_sel'
                    else:
                        sqlnam = 'he8_flupdate_ohneversch_sel'
                else:
                    if mit_verschneidung:
                        sqlnam = 'he8_flupdate_mitversch_all'
                    else:
                        sqlnam = 'he8_flupdate_ohneversch_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_flaechen (2)",
                ):
                    return False


                if QKan.config.selections.selectedObjects:
                    if mit_verschneidung:
                        sqlnam = 'he8_update_flaechen_mitversch_sel'
                    else:
                        sqlnam = 'he8_update_flaechen_ohneversch_sel'
                else:
                    if mit_verschneidung:
                        sqlnam = 'he8_update_flaechen_mitversch_all'
                    else:
                        sqlnam = 'he8_update_flaechen_ohneversch_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_flaechen (2)",
                    parameters=(mindestflaeche,),
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Flächen in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_flaechen',
                    "db_qkan: export_to_he8.export_flaechen (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                if QKan.config.selections.selectedObjects:
                    if mit_verschneidung:
                        sqlnam = 'he8_append_flaechen_mitversch_sel'
                    else:
                        sqlnam = 'he8_append_flaechen_ohneversch_sel'
                else:
                    if mit_verschneidung:
                        sqlnam = 'he8_append_flaechen_mitversch_all'
                    else:
                        sqlnam = 'he8_append_flaechen_ohneversch_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_flaechen (3)",
                    parameters={'nr0': nr0, 'mindestflaeche': mindestflaeche}
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_flaechen',
                    "db_qkan: export_to_he8.export_flaechen (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Flächen eingefügt", 0.95)
                self.progress_bar.setValue(95)

        return True

    def _tezg(self) -> bool:

        if QKan.config.check_export.tezg_hf:
            """Export Haltungsflächen als befestigte und unbefestigte Flächen"""

            # Sicherstellen, dass Abflussparameter für befestigte und unbefestigte Flächen vorhanden sind.
            sqlnam = "he8_check_tezghf_parameters"
            if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_tezg (0)",
            ):
                return False

            if self.append:
                # Feststellen der Anzahl Haltungsflaechen in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_flaechen',
                    "db_qkan: export_to_he8.export_tezg (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                mindestflaeche = QKan.config.mindestflaeche

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_tezghf_sel'
                else:
                    sqlnam = 'he8_append_tezghf_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_tezg (2)",
                    parameters={'nr0': nr0, 'mindestflaeche': mindestflaeche}
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_flaechen',
                    "db_qkan: export_to_he8.export_tezg (3)"
                ):
                    return False

                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Haltungsflaechen eingefügt", 1.00)
                self.progress_bar.setValue(100)
        elif QKan.config.check_export.tezg:
            """Export Haltungsflächen in HE-Tabelle 'GeipEinzugsflaeche'. 
               Diese haben für Berechnungen in HE8 keine direkte Funktion!"""
            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                if not self.db_qkan.sqlyml(
                    'he8_count_he_tezg',
                    "db_qkan: export_to_he8.export_tezg (4)"
                ):
                    return False

                data = self.db_qkan.fetchone()
                if len(data) == 2:
                    idmin, idmax = data
                    logger.debug(f"idmin = {idmin}\nidmax = {idmax}\n")
                else:
                    logger.error_code(
                        "Fehler (7) in QKan_Export\n"
                        f"Feststellung min, max zu rowid fehlgeschlagen: {data}"
                    )
                    raise Exception(f"{self.__class__.__name__}")

                if idmin is None:
                    logger.warning(
                        "Einfügen tezg als GIPS-TEZG\nKeine Haltungsflächen vorhanden"
                    )
                    return True

                nr0 = self.nextid
                id0 = self.nextid - idmin

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_tezg_sel'
                else:
                    sqlnam = 'he8_append_tezg_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_tezg (5)",
                    parameters={'id0': id0}
                ):
                    return False

                self.nextid += idmax - idmin + 1
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )

                fortschritt("{} Haltungsflaechen eingefuegt".format(self.nextid - nr0), 0.90)
                self.progress_bar.setValue(90)

        self.db_qkan.commit()

        return True

    def _pumpen(self) -> bool:
        """Export Pumpen"""

        if QKan.config.check_export.pumpen:
            if self.update:
                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_update_pumpen_sel'
                else:
                    sqlnam = 'he8_update_pumpen_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_pumpen (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Pumpen in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_pumpen',
                    "db_qkan: export_to_he8.export_pumpen (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_pumpen_sel'
                else:
                    sqlnam = 'he8_append_pumpen_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_pumpen (3)",
                    parameters={'nr0': nr0}
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_pumpen',
                    "db_qkan: export_to_he8.export_pumpen (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Pumpen eingefügt", 0.64)
                self.progress_bar.setValue(64)
        return True

    def _wehre(self) -> bool:
        """Export Wehre"""

        if QKan.config.check_export.wehre:
            if self.update:
                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_update_wehre_sel'
                else:
                    sqlnam = 'he8_update_wehre_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_wehre (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Wehre in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_wehre',
                    "db_qkan: export_to_he8.export_wehre (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_wehre_sel'
                else:
                    sqlnam = 'he8_append_wehre_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_wehre (3)",
                    parameters={'nr0': nr0}
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_wehre',
                    "db_qkan: export_to_he8.export_wehre (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Wehre eingefügt", 0.62)
                self.progress_bar.setValue(62)
        return True

    def _drosseln(self) -> bool:
        """Export Drosseln"""

        if QKan.config.check_export.drosseln:
            if self.update:
                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_update_drosseln_sel'
                else:
                    sqlnam = 'he8_update_drosseln_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_drosseln (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Drosseln in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_drossel',
                    "db_qkan: export_to_he8.export_drosseln (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_drosseln_sel'
                else:
                    sqlnam = 'he8_append_drosseln_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_drosseln (3)",
                    parameters={'nr0': nr0}
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_drossel',
                    "db_qkan: export_to_he8.export_drosseln (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Drosseln eingefügt", 0.66)
                self.progress_bar.setValue(66)
        return True

    def _schieber(self) -> bool:
        """Export Drosseln"""

        if QKan.config.check_export.schieber:
            if self.update:
                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_update_schieber_sel'
                else:
                    sqlnam = 'he8_update_schieber_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_schieber (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Schieber in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_schieber',
                    "db_qkan: export_to_he8.export_schieber (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_schieber_sel'
                else:
                    sqlnam = 'he8_append_schieber_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_schieber (3)",
                    parameters={'nr0': nr0}
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_schieber',
                    "db_qkan: export_to_he8.export_schieber (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Schieber eingefügt", 0.68)
                self.progress_bar.setValue(68)
        return True

    def _grundseitenauslaesse(self) -> bool:
        """Export Grund- und Seitenauslässe"""

        if QKan.config.check_export.grundseitenauslaesse:
            if self.update:
                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_update_grundseitenauslaesse_sel'
                else:
                    sqlnam = 'he8_update_grundseitenauslaesse_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_grundseitenauslaesse (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Grund-/Seitenauslässe in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_grundseitenauslass',
                    "db_qkan: export_to_he8.export_grundseitenauslaesse (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_grundseitenauslaesse_sel'
                else:
                    sqlnam = 'he8_append_grundseitenauslaesse_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_grundseitenauslaesse (3)",
                    parameters={'nr0': nr0}
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_grundseitenauslass',
                    "db_qkan: export_to_he8.export_grundseitenauslaesse (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Grund-/Seitenauslässe eingefügt", 0.74)
                self.progress_bar.setValue(74)
        return True

    def _qregler(self) -> bool:
        """Export Q-Regler"""

        if QKan.config.check_export.qregler:
            if self.update:
                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_update_qregler_sel'
                else:
                    sqlnam = 'he8_update_qregler_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_qregler (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl Q-Regler in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_qregler',
                    "db_qkan: export_to_he8.export_qregler (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_qregler_sel'
                else:
                    sqlnam = 'he8_append_qregler_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_qregler (3)",
                    parameters={'nr0': nr0}
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_qregler',
                    "db_qkan: export_to_he8.export_qregler (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} Q-Regler eingefügt", 0.70)
                self.progress_bar.setValue(70)
        return True

    def _hregler(self) -> bool:
        """Export H-Regler"""

        if QKan.config.check_export.hregler:
            if self.update:
                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_update_hregler_sel'
                else:
                    sqlnam = 'he8_update_hregler_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_hregler (1)"
                ):
                    return False

            if self.append:
                # Feststellen der Anzahl H-Regler in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_hregler',
                    "db_qkan: export_to_he8.export_h_regler (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                if QKan.config.selections.selectedObjects:
                    sqlnam = 'he8_append_hregler_sel'
                else:
                    sqlnam = 'he8_append_hregler_all'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_hregler (3)",
                    parameters={'nr0': nr0}
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_hregler',
                    "db_qkan: export_to_he8.export_h_regler (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt(f"{anzn - anzv} H-Regler eingefügt", 0.72)
                self.progress_bar.setValue(72)
        return True

    def _abflussparameter(self) -> bool:
        """Export Abflussparameter"""

        if QKan.config.check_export.abflussparameter:
            if self.append:
                # Feststellen der vorkommenden Werte von rowid fuer korrekte Werte von nextid in der ITWH-Datenbank
                if not self.db_qkan.sqlyml(
                    'he8_count_he_abflussparameter',
                    "db_qkan: export_to_he8.export_Abflussparameter (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                sqlnam = 'he8_append_abflussparameter'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_abflussparameter (2)",
                    parameters={'nr0': nr0}
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_abflussparameter',
                    "db_qkan: export_to_he8.export_Abflussparameter (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )

                self.db_qkan.commit()

                fortschritt("{} Abflussparameter eingefuegt".format(anzn - anzv), 0.04)
                self.progress_bar.setValue(4)


        return True

    def _bodenklassen(self) -> bool:
        """Export der Bodenklassen"""

        if QKan.config.check_export.bodenklassen:
            if self.append:
                # Feststellen der Anzahl Bodenklassen in ITWH-Datenbank fuer korrekte Werte von nextid
                if not self.db_qkan.sqlyml(
                    'he8_count_he_bodenklasse',
                    "db_qkan: export_to_he8.export_Bodenklassen (1)"
                ):
                    return False
                anzv = self.db_qkan.fetchone()[0]

                nr0 = self.nextid

                sqlnam = 'he8_append_bodenklassen'

                if not self.db_qkan.sqlyml(
                    sqlnam,
                    "db_qkan: export_to_he8.export_abflussparameter (2)",
                    parameters={'nr0': nr0}
                ):
                    return False

                if not self.db_qkan.sqlyml(
                    'he8_count_he_bodenklasse',
                    "db_qkan: export_to_he8.export_Bodenklassen (2)"
                ):
                    return False
                anzn = self.db_qkan.fetchone()[0]
                self.nextid += anzn - anzv
                self.db_qkan.sqlyml(
                    'he8_nextid',
                    parameters=(self.nextid,),
                )
                self.db_qkan.commit()

                fortschritt("{} Abflussparameter eingefuegt".format(anzn - anzv), 0.02)
                self.progress_bar.setValue(2)

        return True

    def _check_complete(self):
        """Prüft Vollständigkeit der Daten für den Export"""
        QKan.config.plausi.themen = ["HYSTEM-EXTRAN"]
        QKan.config.plausi.keepdata = False
        QKan.config.plausi.limitdata = True

        iface = QKan.instance.iface
        test = Plausi(iface)
        test._prepareplausi(self.db_qkan)
        test._doplausi(self.db_qkan, is_test=True)

        sql = """SELECT count() FROM pruefliste"""
        self.db_qkan.sql(sql, f'{self.__class__.__name__}._reftables()')
        data = self.db_qkan.fetchone()
        logger.debug(f'_check_complete: {data=}')
        complete = (data[0] == 0)

        return complete
