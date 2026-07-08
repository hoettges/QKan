from qgis.PyQt.QtWidgets import QDialog
from qkan.tools.vlc_error import VlcLoadError
from qkan.utils import get_logger
from qgis.utils import iface
from qgis.core import Qgis

import os
from qkan import QKan
from qkan.database.dbfunc import DBConnection
from qkan.tools.videoplayer import Videoplayer
from qkan.tools.qkan_utils import get_database_QKan
import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

logger = get_logger("QKan.tools.zeige_video")

class ShowVideo(QDialog):
    """Zeigt Haltungsschäden an"""
    def __init__(self, name: str, untersuchtag, video_offset, time_code, art, bild_ordner):
        super(ShowVideo, self).__init__()

        self.name = name
        self.untersuchtag = untersuchtag
        self.art = art
        self.bild_ordner = bild_ordner
        if video_offset in ['', None, 'NULL']:
            self.video_offset = 0
        else:
            self.video_offset = float(video_offset)

        if time_code in ['', None, 'NULL']:
            self.time_code = 0
        else:
            self.time_code = float(time_code)

        #self.show()

    def show(self):
        """Aktualisiert die Schadensliste"""
        self.showschaedencolumns = 100
        #self.showlist()

        ordner = QKan.config.videoRootPath
        get_database_QKan()
        with DBConnection(dbname=QKan.config.database.qkan) as db_qkan:

            try:
                name = self.name
                datum = self.untersuchtag
                sql = f"""select datei from videos where name= '{name}' and untersuchtag = '{datum}' and objekt = '{self.art}'"""

                db_qkan.sql(sql)
                data = db_qkan.fetchone()
                if data is None:
                    iface.messageBar().pushMessage(
                        f'Kein Video für Haltung {name} und Datum {datum} gefunden',
                        level=Qgis.Warning, duration=5)
                else:
                    datei = data[0]
                    datei = datei.lstrip("\\/")

                video = os.path.normpath(os.path.join(ordner, datei))
                video = video.lower()
                time_h = 0
                timecode = self.time_code
                if timecode > 0:
                    time_h = int(timecode / 1000000) if timecode > 1000000 else 0
                time_m = (int(timecode / 10000) if timecode > 10000 else 0) - (time_h * 100)
                time_s = (int(timecode / 100) if timecode > 100 else 0) - (time_h * 10000) - (time_m * 100)

                video_offset = self.video_offset
                time = float(time_h / 3600 + time_m / 60 + time_s + video_offset)

                try:
                    window = Videoplayer(video=video, time=time)
                except VlcLoadError:
                    logger.error_user("Could not open/find VLC. Is it installed?")
                else:
                    window.show()
                    window.open_file()
                    window.exec_()

            except ImportError:
                raise Exception(
                    "The QKan main plugin has to be installed for this to work."
                )

    def show_panoramo(self):

        ordner = QKan.config.videoRootPath

        get_database_QKan()
        with DBConnection(dbname=QKan.config.database.qkan) as db_qkan:

            name = self.name
            datum = self.untersuchtag
            sql = f"""select datei from videos where name= '{name}' and untersuchtag = '{datum}' and objekt = '{self.art}'"""

            db_qkan.sql(sql)
            data = db_qkan.fetchone()
            if data is None:
                iface.messageBar().pushMessage(
                    f'Kein Video für Haltung {name} und Datum {datum} gefunden',
                    level=Qgis.Warning, duration=5)
            else:
                datei = data[0]
                datei = datei.lstrip("\\/")
            video = os.path.normpath(os.path.join(ordner, datei))
            video = video.lower()
            system = sys.platform

            if system == "Windows":
                os.startfile(video)  # Windows öffnet die Datei mit Standardprogramm
            elif system == "Darwin":  # macOS
                os.system(f"open '{video}'")
            else:  # Linux
                os.system(f"xdg-open '{video}'")

    def show_bild(self):
        ordner = QKan.config.fotoRootPath

        # Bild laden
        bild = self.bild_ordner
        if bild != '':
            bild_path = os.path.normpath(os.path.join(ordner, bild))
            bild_path = bild_path.lower()
            bild_path = mpimg.imread(bild_path)

            # Bild anzeigen
            plt.imshow(bild_path)
            plt.axis("off")
            plt.show()
