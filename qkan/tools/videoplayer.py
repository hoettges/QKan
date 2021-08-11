import os.path

from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog, QMainWindow

from qkan.external.vlc import vlc


class Videoplayer(QMainWindow):
    def __init__(self, video, foto_path):
        QMainWindow.__init__(self)
        uic.loadUi("fenster.ui", self)

        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()

        self.pushButton.clicked.connect(self.PlayPause)
        self.pushButton_3.clicked.connect(self.Foto)
        self.isPaused = False

        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.updateUI)

        self.video = video
        self.foto_path = foto_path

    def PlayPause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.pushButton.setText("Play")
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.OpenFile()
                return
            self.mediaplayer.play()
            self.pushButton.setText("Pause")
            self.timer.start()
            self.isPaused = False

    def Foto(self):
        """Screenshot"""
        foto_path = self.foto_path
        self.mediaplayer.video_take_snapshot(0, foto_path, 640, 360)

    def OpenFile(self, filename=None):
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
        self.mediaplayer.set_hwnd(self.frame_2.winId())
        self.PlayPause()

    def setPosition(self, position):
        """Set the position"""
        # setting the position to where the slider was dragged
        self.mediaplayer.set_position(position / 1000.0)

    def updateUI(self):
        """updates the user interface"""
        # setting the slider to the desired position
        self.horizontalSlider.setValue(int(self.mediaplayer.get_position() * 1000))

        if not self.mediaplayer.is_playing():
            self.timer.stop()
            if not self.isPaused:
                self.Stop()
