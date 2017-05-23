# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Enums import SliderMode


class Slider(QSlider):
    def __init__(self):
        super(self.__class__, self).__init__(Qt.Horizontal)
        self.setRange(0, 50)
        self.setSingleStep(1)
        self.setPageStep(5)
        self.setTickInterval(1)
        self.setFixedHeight(60)
        self.mode = SliderMode.Forward
        self.last_mode = None
        self.set_paused()

    def paintEvent(self, e):
        st = self.style()
        p = QPainter(self)
        v = 0
        slider = QStyleOptionSlider()
        slider.initFrom(self)
        available = st.pixelMetric(QStyle.PM_SliderSpaceAvailable, slider, self)
        length = st.pixelMetric(QStyle.PM_SliderLength, slider, self) / 2.
        p.drawText(self.rect(), Qt.TextDontPrint, "9999")
        font = QFont()
        metrics = QFontMetrics(font)
        l = metrics.width("0x")
        slider_pos = st.sliderPositionFromValue(self.minimum(), self.maximum(), v, available) + length - (l / 3.)
        pos = QPoint(slider_pos, self.rect().bottom())
        p.drawText(pos, "0x")
        v = self.maximum()
        l = metrics.width("50x")
        slider_pos = st.sliderPositionFromValue(self.minimum(), self.maximum(), v, available) + length - l
        pos = QPoint(slider_pos, self.rect().bottom())
        p.drawText(pos, "50x")
        super(self.__class__, self).paintEvent(e)

    def mouseReleaseEvent(self, _QMouseEvent):
        ctrl = _QMouseEvent.modifiers() == Qt.ControlModifier
        if _QMouseEvent.button() == Qt.RightButton:
            if ctrl:
                self.ctrl_click()
            else:
                self.set_paused()
        else:
            super(self.__class__, self).mouseReleaseEvent(_QMouseEvent)

    def ctrl_click(self):
        if self.mode == SliderMode.Pause:
            self.last_mode = SliderMode.Forward if self.last_mode == SliderMode.Backward else SliderMode.Backward
        else:
            self.mode = SliderMode.Forward if self.mode == SliderMode.Backward else SliderMode.Backward
        self.update_style()
        self.valueChanged.emit(self.value())

    def set_paused(self):
        if self.mode == SliderMode.Pause:
            self.mode = self.last_mode
        else:
            self.last_mode = self.mode
            self.mode = SliderMode.Pause
        self.update_style()
        self.valueChanged.emit(self.value())

    def update_style(self):
        if self.mode == SliderMode.Forward:
            temp = """QSlider::groove:horizontal {
                          border: 1px solid #999999;
                          height: 20px;
                          background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #050DFF, stop:1 #757AFF);
                          margin: 2px 0;
                      }
                      QSlider::handle:horizontal {
                          background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #000000, stop:1 #8f8f8f);
                          border: 1px solid #5c5c5c;
                          width: 15px;
                          margin: -2px 0px;
                      }"""
        elif self.mode == SliderMode.Backward:
            temp = """QSlider::groove:horizontal {
                          border: 1px solid #999999;
                          height: 20px;
                          background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #D10232, stop:1 #FF6B8E);
                          margin: 2px 0;
                      }
                      QSlider::handle:horizontal {
                          background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #000000, stop:1 #8f8f8f);
                          border: 1px solid #5c5c5c;
                          width: 15px;
                          margin: -2px 0px;
                      } """
        else:
            temp = """QSlider::groove:horizontal {
                          border: 1px solid #999999;
                          height: 20px;
                          background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #969696, stop:1 #595959);
                          margin: 2px 0;
                      }
                      QSlider::handle:horizontal {
                          background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #000000, stop:1 #8f8f8f);
                          border: 1px solid #5c5c5c;
                          width: 15px;
                          margin: -2px 0px;
                      } """
        self.setStyleSheet(temp)

    def reset(self):
        self.mode = SliderMode.Forward
        self.set_paused()
        self.update_style()
        self.setValue(0)
