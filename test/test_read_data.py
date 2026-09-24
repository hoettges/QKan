from .base_test import BASE_DATA, BASE_WORK, QgisTest
from zipfile import ZipFile
from qgis.core import QgsApplication

# noinspection PyUnresolvedReferences
from qgis.testing import unittest

# sys.path.append(os.path.join(os.path.split(__file__)[0], ".."))

from qkan import QKan
from qkan.database.dbfunc import DBConnection

from qkan.tools.dialogs.read_data import ReadData

# Fuer einen Test mit PyCharm Workingdir auf C:\Users\...\default\python\plugins einstellen (d. h. "\test" löschen)
class TestReadData(QgisTest):
    """Test des Moduls Plausi"""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # Extract files
        with ZipFile(BASE_DATA / "test_readdata.zip") as z:
            z.extractall(BASE_WORK)

    def test_clip(self) -> None:

        QKan.config.database.qkan = str(BASE_WORK / "test.sqlite")
        QKan.config.project.file = str(BASE_WORK / "plan.qgs")
        QKan.config.epsg = 25832

        dbname = QKan.config.database.qkan
        task = ReadData()
        task.layer_name = 'Haltungen'
        task.epsg = 25832
        task.geom = 'geom'
        task.table_name = 'haltungen'
        task.db_qkan = DBConnection(dbname)
        clip = ('wkt_geom\tHaltungNr\tentwart\tschoben\tschunten\tSohleOben\tSohleUnten\tMaterial\tProfilart\t'
                'Profilhoehe\tProfilbreite\nLineString (522732.38790000043809414 5385018.17970000021159649, '
                '522736.21980000007897615 5385002.34989999979734421)\tK6058\tFreispiegelabfluss im geschlossenen '
                'Profil, Mischwassersystem\tK6058\tK6059\t285,553\t283,518\tStahlbeton\tKreisprofil\t300\t300\n'
                'LineString (522837.43680000025779009 5385004.18190000019967556, 522842.76630000025033951 '
                '5384992.55819999985396862)\tK6029\tFreispiegelabfluss im geschlossenen Profil, Mischwassersystem\t'
                'K6029\tK6030\t279,349\t279,045\tStahlbeton\tKreisprofil\t400\t400\nLineString '
                '(522861.17129999957978725 5384950.22760000079870224, 522864.44290000014007092 '
                '5384946.81709999963641167)\tK6032\tFreispiegelabfluss im geschlossenen Profil, Mischwassersystem\t'
                'K6032\tK6033\t276,717\t276,601\tStahlbeton\tKreisprofil\t500\t500\nLineString '
                '(522880.15089999977499247 5385164.12680000066757202, 522875.63760000001639128 '
                '5385164.09520000033080578)\tK6079\tFreispiegelabfluss im geschlossenen Profil, Mischwassersystem\t'
                'K6079\tK6078\t300,211\t300,151\tStahlbeton\tKreisprofil\t200\t200\n')
        QgsApplication.clipboard().setText(clip)
        task.read_clipboard()
        del task
        # self.assertTrue(False, "Fehlernachricht")

if __name__ == "__main__":
    unittest.main()
