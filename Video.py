from PyQt5 import Qt, QtGui
from PyQt5.QtGui import QPixmap, QResizeEvent
from PyQt5.QtCore import QEvent, QObject, QSize, Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel, QPushButton, QWidget, QGridLayout
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from Globals import *


class VideoWin(QWidget):
    wallpaper_hidden = pyqtSignal()
    wallpaper_showed = pyqtSignal()
    curtain_hidden = pyqtSignal()
    curtain_showed = pyqtSignal()
    video_hidden = pyqtSignal()
    video_showed = pyqtSignal()
    
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Видео экран')
        
        self.video = QVideoWidget(self)
        self.curtain = QLabel(self)
        self.wallpaper = QLabel(self)
        
        self.curtain.setAlignment(Qt.AlignCenter)
        self.wallpaper.setAlignment(Qt.AlignCenter)

        self.setFixedSize(512, 288)
        self.old_pos = None
        self.big = False

        self.wallpaper_path = None
        self.curtain_path = None

        self.setStyleSheet('QWidget{background-color: rgb(0, 0, 0);}')

        self.wallpaper.setStyleSheet('QLabel{background-color: rgb(0, 0, 0);}')
        self.curtain.setStyleSheet('QLabel{background-color: rgb(0, 0, 0);}')
        icon = QPixmap()
        icon.loadFromData(wallpaper)
        self.wallpaper.setPixmap(icon.scaled(self.size()))

        self.video.installEventFilter(self)
        self.curtain.installEventFilter(self)
        self.wallpaper.installEventFilter(self)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.big:
            self.showNormal()
            self.setFixedSize(512, 288)
            self.big = False
        else:
            self.showFullScreen()
            self.big = True

    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        if a0 == self.wallpaper:
            if a1.type() == QEvent.Show:
                self.wallpaper_showed.emit()
            elif a1.type() == QEvent.Hide:
                self.wallpaper_hidden.emit()
        elif a0 == self.curtain:
            if a1.type() == QEvent.Show:
                self.curtain_showed.emit()
            elif a1.type() == QEvent.Hide:
                self.curtain_hidden.emit()
        elif a0 == self.video:
            if a1.type() == QEvent.Show:
                self.video_showed.emit()
            elif a1.type() == QEvent.Hide:
                self.video_hidden.emit()
        return super().eventFilter(a0, a1)

    def resizeEvent(self, event) -> None:
        self.resize_all()
        return super().resizeEvent(event)
    
    def resize_all(self) -> None:
        self.video.resize(self.size())
        self.wallpaper.resize(self.size())
        if self.wallpaper_path is None:
            icon = QPixmap()
            icon.loadFromData(wallpaper)
            self.wallpaper.setPixmap(icon.scaled(self.size()))
        else:
            self.wallpaper.setPixmap(QPixmap(self.wallpaper_path).scaled(self.size(), Qt.KeepAspectRatio))
        self.curtain.resize(self.size())
        if self.curtain_path:
            self.curtain.setPixmap(QPixmap(self.curtain_path).scaled(self.size(), Qt.KeepAspectRatio))
            
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None

    def mouseMoveEvent(self, event):
        if not self.old_pos:
            return
        delta = event.pos() - self.old_pos
        self.move(self.pos() + delta)


class VideoSettings(QWidget):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.wallpaper_data = wallpaper
        self.curtain_data = None

        self.small_wallpaper = QLabel(self)
        self.small_wallpaper.setStyleSheet('QLabel{background-color: rgb(0, 0, 0);}')
        self.small_video = QVideoWidget(self)
        self.small_video.setStyleSheet('QVideoWidget{background-color: rgb(0, 0, 0);}')
        self.small_curtain = QLabel(self)
        self.small_curtain.setStyleSheet('QLabel{background-color: rgb(0, 0, 0);}')
        
        self.small_curtain.setAlignment(Qt.AlignCenter)
        self.small_wallpaper.setAlignment(Qt.AlignCenter)

        self.player = QMediaPlayer(self)
        self.player.setVolume(0)
        self.player.setVideoOutput(self.small_video)

        self.video_win = VideoWin()

        self.main_box = QGridLayout()

        self.show_window = QPushButton('Показать окно', self)
        self.show_window.clicked.connect(lambda: self.video_win.show())
        self.hide_window = QPushButton('Скрыть окно', self)
        self.hide_window.clicked.connect(lambda: self.video_win.hide())
        self.show_video_but = QPushButton('Показать видео', self)
        self.show_video_but.clicked.connect(self.video_win.video.show)
        self.hide_video_but = QPushButton('Скрыть видео', self)
        self.hide_video_but.clicked.connect(self.video_win.video.hide)
        self.show_curtain_but = QPushButton('Показать заставку', self)
        self.show_curtain_but.clicked.connect(self.video_win.curtain.show)
        self.hide_curtain_but = QPushButton('Скрыть заставку', self)
        self.hide_curtain_but.clicked.connect(self.video_win.curtain.hide)
        self.show_wallpaper_but = QPushButton('Показать занавес', self)
        self.show_wallpaper_but.clicked.connect(self.video_win.wallpaper.show)
        self.hide_wallpaper_but = QPushButton('Скрыть занавес', self)
        self.hide_wallpaper_but.clicked.connect(self.video_win.wallpaper.hide)
        
        self.main_box.addWidget(self.show_window, 0, 0)
        self.main_box.addWidget(self.hide_window, 0, 1)
        self.main_box.addWidget(self.small_video, 1, 0, 2, 1)
        self.main_box.addWidget(self.show_video_but, 1, 1)
        self.main_box.addWidget(self.hide_video_but, 2, 1)

        self.main_box.addWidget(self.small_curtain, 3, 0, 2, 1)
        self.main_box.addWidget(self.show_curtain_but, 3, 1)
        self.main_box.addWidget(self.hide_curtain_but, 4, 1)

        self.main_box.addWidget(self.small_wallpaper, 5, 0, 2, 1)
        self.main_box.addWidget(self.show_wallpaper_but, 5, 1)
        self.main_box.addWidget(self.hide_wallpaper_but, 6, 1)

        self.video_win.video_hidden.connect(self.check_vis)
        self.video_win.video_showed.connect(self.check_vis)
        self.video_win.wallpaper_hidden.connect(self.check_vis)
        self.video_win.wallpaper_showed.connect(self.check_vis)
        self.video_win.curtain_hidden.connect(self.check_vis)
        self.video_win.curtain_showed.connect(self.check_vis)

        self.check_vis()
        self.setLayout(self.main_box)

    def check_vis(self):
        self.hide_video_but.setEnabled(not self.video_win.video.isHidden())
        self.show_video_but.setEnabled(self.video_win.video.isHidden())
        self.hide_curtain_but.setEnabled(not self.video_win.curtain.isHidden())
        self.show_curtain_but.setEnabled(self.video_win.curtain.isHidden())
        self.hide_wallpaper_but.setEnabled(not self.video_win.wallpaper.isHidden())
        self.show_wallpaper_but.setEnabled(self.video_win.wallpaper.isHidden())
        
    def set_curtain(self, path: str) -> None:
        self.small_curtain.setPixmap(QPixmap(path).scaled(self.small_curtain.size(), Qt.KeepAspectRatio))
        self.video_win.curtain.setPixmap(QPixmap(path).scaled(self.video_win.curtain.size(), Qt.KeepAspectRatio))
        self.video_win.curtain_path = path
        
    def set_wallpaper(self, path: str) -> None:
        self.small_wallpaper.setPixmap(QPixmap(path).scaled(self.small_wallpaper.size(), Qt.KeepAspectRatio))
        self.video_win.wallpaper.setPixmap(QPixmap(path).scaled(self.video_win.wallpaper.size(), Qt.KeepAspectRatio))
        self.video_win.wallpaper_path = path
        
    def load_language(self, lang: str) -> None:
        self.show_window.setText(dictionary['Show the window'][lang])
        self.hide_window.setText(dictionary['Hide the window'][lang])
        self.show_video_but.setText(dictionary['Show the video'][lang])
        self.hide_video_but.setText(dictionary['Hide the video'][lang])
        self.show_curtain_but.setText(dictionary['Show the curtain'][lang])
        self.hide_curtain_but.setText(dictionary['Hide the curtain'][lang])
        self.show_wallpaper_but.setText(dictionary['Show the wallpaper'][lang])
        self.hide_wallpaper_but.setText(dictionary['Hide the wallpaper'][lang])
        
    def resizeEvent(self, a0) -> None:
        self.small_wallpaper.setMaximumHeight((self.size().height() - 150) // 4)
        self.small_curtain.setMaximumHeight((self.size().height() - 150) // 4)
        self.small_video.setMaximumHeight((self.size().height() - 150) // 4)

        temp = QPixmap()
        temp.loadFromData(self.wallpaper_data)
        self.small_wallpaper.setPixmap(temp.scaledToHeight(self.small_wallpaper.size().height()))
        temp = QPixmap(self.video_win.curtain_path)
        self.small_curtain.setPixmap(temp.scaledToHeight(self.small_curtain.size().height()))
        return super().resizeEvent(a0)
