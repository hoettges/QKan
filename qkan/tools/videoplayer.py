import os.path
import sys
from PyQt5 import uic
from PyQt5.QtCore import QTimer, QTime
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QFrame, QPushButton, QSlider,QApplication

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
    geschw: QSlider
    frame: QFrame
    horizontalSlider: QSlider

    def __init__(
        self, video, time, parent=None
    ):
        super().__init__(parent=parent)

        self.setupUi(self)

        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()

        self.playpause.clicked.connect(self.play_pause)
        self.geschw.sliderMoved.connect(self.geschwingigkeit)
        #self.playpause.clicked.connect(self.update_time)
        self.screenshot.clicked.connect(self.take_screenshot)
        self.horizontalSlider.setMaximum(1000)
        self.horizontalSlider.sliderMoved.connect(self.set_position)
        self.horizontalSlider.sliderMoved.connect(self.update_time)
        self.timelabel.setText("00:00:00")
        self.isPaused = False

        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_ui2)
        self.timer.timeout.connect(self.update_time)
        self.video = video
        self.time = time

    #def Stop(self):
     #   """Stop player
      #  """
       # self.mediaplayer.stop()

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

    def geschwingigkeit(self):
        #aktuelle geschwindigkeit
        #value = self.media_player.get_rate()

        if self.geschw.value() == 0:
            self.mediaplayer.set_rate(0.25)

        if self.geschw.value() == 1:
            self.mediaplayer.set_rate(0.5)

        if self.geschw.value() == 2:
            self.mediaplayer.set_rate(1)

        if self.geschw.value() == 3:
            self.mediaplayer.set_rate(2)

        if self.geschw.value() == 4:
            self.mediaplayer.set_rate(4)


    def take_screenshot(self):
        """Screenshot"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Zu erstellender Screenshot"),
            "*.jpg",
        )
        if filename:
            foto_path = filename
            self.mediaplayer.video_take_snapshot(0, foto_path, 640, 360)

    def open_file(self):
        """Open a media file in a MediaPlayer"""
        filename = self.video
        time = self.time
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
        self.media.add_option("start-time={}".format(time))
        # set the title of the track as window title
        self.setWindowTitle(self.media.get_meta(0))
        self.mediaplayer.set_hwnd(self.frame.winId())
        #mediplayer starten ohne das video dirket abspielt !!!
        events = self.mediaplayer.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerPositionChanged, self.update_ui)
        self.play_pause()
        #self.mediaplayer.pause()
        #self.playpause.setText("Play")
        #self.isPaused = True


    def Stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("Play")


    def set_position(self):
        """Set the position when slider is dragged"""
        # setting the position to where the slider was dragged
        pos = self.horizontalSlider.value()
        self.mediaplayer.set_position(pos * .001)

    #def update_ui(self):
    def update_ui(self,event):
        """updates the user interface"""
        # setting the slider to the desired position
        #self.horizontalSlider.setValue(int(self.mediaplayer.get_position() * 1000))
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.horizontalSlider.setValue(media_pos)

        if media_pos >= 0 and self.mediaplayer.is_playing():
            self.update_time()

        if not self.mediaplayer.is_playing():
            self.timer.stop()
            if not self.isPaused:
                pass
                #self.Stop()

    def update_ui2(self):
        """updates the user interface"""
        # setting the slider to the desired position
        #self.horizontalSlider.setValue(int(self.mediaplayer.get_position() * 1000))
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.horizontalSlider.setValue(media_pos)

        if media_pos >= 0 and self.mediaplayer.is_playing():
            self.update_time()

        if not self.mediaplayer.is_playing():
            self.timer.stop()
            if not self.isPaused:
                pass
                # self.Stop()


    def update_time(self):
        mtime = QTime(0, 0, 0, 0)
        self.time = mtime.addMSecs(self.mediaplayer.get_time())
        self.timelabel.setText(self.time.toString())

    @staticmethod
    def open_video(video: str, time: float):
        #folder_path = QgsProject.instance().readPath("./")
        window = Videoplayer(video=video, time=time)
        window.show()
        window.open_file()
        window.exec_()



