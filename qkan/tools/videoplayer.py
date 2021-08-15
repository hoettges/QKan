import os.path

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QFrame, QPushButton, QSlider

try:
    from qkan.external.vlc import vlc
except OSError:
    import traceback

    traceback.print_exc()
    raise Exception("Could not open/find VLC. Is it installed?")

FORM_CLASS_videoplayer, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "res", "videoplayer.ui")
)


class Videoplayer(QDialog, FORM_CLASS_videoplayer):
    playpause: QPushButton
    screenshot: QPushButton
    frame: QFrame
    horizontalSlider: QSlider

    def __init__(
        self, video, foto_path=None, parent=None
    ):  # TODO: Remove None from foto_path
        super().__init__(parent=parent)

        self.setupUi(self)

        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()

        self.playpause.clicked.connect(self.play_pause)
        self.screenshot.clicked.connect(self.take_screenshot)
        self.horizontalSlider.sliderMoved.connect(self.set_position)
        self.isPaused = False

        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_ui)

        self.video = video
        self.foto_path = foto_path

    def play_pause(self):
        """ """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playpause.setText("Play")
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return
            self.mediaplayer.play()
            self.playpause.setText("Pause")
            self.timer.start()
            self.isPaused = False

    def take_screenshot(self):
        """Screenshot"""
        # TODO: Save screenshot to specified folder
        # foto_path = self.foto_path
        # self.mediaplayer.video_take_snapshot(0, foto_path, 640, 360)

    def open_file(self, filename=None):
        """Open a media file in a MediaPlayer"""
        filename = self.video
        if filename is None:
            filename = QFileDialog.getOpenFileName(
                self, "Open File", os.path.expanduser("~")
            )[0]
        if not filename:
            return

        # create the media
        self.media = self.instance.media_new(filename)
        # put the media in the media player
        self.mediaplayer.set_media(self.media)

        # parse the metadata of the file
        self.media.parse()
        # hier wird die Startzeit eingegeben in sekunden!
        self.media.add_option("start-time=00.0")
        # set the title of the track as window title
        self.setWindowTitle(self.media.get_meta(0))
        self.mediaplayer.set_hwnd(self.frame.winId())
        self.play_pause()

    def set_position(self, position):
        """Set the position when slider is dragged"""
        # setting the position to where the slider was dragged
        self.mediaplayer.set_position(position / 100)

    def update_ui(self):
        """updates the user interface"""
        # setting the slider to the desired position
        self.horizontalSlider.setValue(int(self.mediaplayer.get_position() * 100))

        if not self.mediaplayer.is_playing():
            self.timer.stop()
            if not self.isPaused:
                pass
                # self.Stop()  # TODO: Missing?

    @staticmethod
    def open_video(video: str):
        folder_path = QgsProject.instance().readPath("./")
        window = Videoplayer(video=os.path.join(folder_path, video))
        window.open_file()
        window.show()
        window.exec_()
