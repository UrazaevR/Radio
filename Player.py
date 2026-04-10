# -*- coding: cp1251 -*-
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QWidget, QLabel, QLCDNumber, QSlider, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, \
    QButtonGroup, QRadioButton, QBoxLayout, QGridLayout
from PyQt5.QtCore import Qt, QUrl, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from Playlist import Songlist
from FOR_INI import read_set
from Globals import *


class MyPlayer(QWidget):
    Play = 1
    Pause = 2
    Stop = 3
    Schedule = 4
    Single = 5
    Contract = 6
    mode_changed_signal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #Переменные
        self.song = None
        self.status = self.Stop
        self.playlist = None
        self.double_player = None

        # Виджеты
        self.player = QMediaPlayer()
        self.player.durationChanged.connect(self.duration_view)
        self.player.positionChanged.connect(self.update_position)

        self.name = QLabel("Here's name of the song!")
        self.name.setMinimumWidth(30)
        self.time_viewer = QLCDNumber()
        self.time_viewer.display('00:00')
        self.duration_viewer = QLCDNumber()
        self.duration_viewer.display('00:00')
        self.slash = QLabel('/')
        self.slash.setObjectName("time_slash")
        self.slash.adjustSize()
        self.slash.setMaximumSize(self.slash.size())

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setSingleStep(5000)
        self.slider.valueChanged.connect(self.change_position)

        self.VolumeSlider = QSlider(Qt.Vertical)
        #self.VolumeSlider.setTickPosition(QSlider.TickPosition.TicksRight)
        self.VolumeSlider.setMaximum(100)
        self.VolumeSlider.setSingleStep(5)
        self.VolumeSlider.valueChanged.connect(self.change_volume)

        self.mode_label = QLabel('Player mode:')
        self.schedule_mode = QCheckBox('Schedule mode')
        self.single_but = QRadioButton('Single mode')
        self.contract_but = QRadioButton('Contract mode')
        self.mode = self.Single
        self.single_but.setChecked(True)
        self.but_group = QButtonGroup()
        self.but_group.addButton(self.single_but)
        self.but_group.addButton(self.contract_but)

        temp_icon = QPixmap()
        temp_icon.loadFromData(icon_play)
        self.PlayButton = QPushButton(icon=QIcon(temp_icon))
        self.PlayButton.setObjectName("PlayButton")
        self.PlayButton.setFixedSize(110, 60)
        self.PlayButton.setIconSize(QSize(40, 30))
        temp_icon.loadFromData(icon_stop)
        self.StopButton = QPushButton(icon=QIcon(temp_icon))
        self.StopButton.setObjectName("StopButton")
        self.StopButton.setFixedSize(100, 50)
        self.StopButton.setIconSize(QSize(30, 20))
        temp_icon.loadFromData(icon_pause)
        self.PauseButton = QPushButton(icon=QIcon(temp_icon))
        self.PauseButton.setObjectName("PauseButton")
        self.PauseButton.setFixedSize(100, 50)
        self.PauseButton.setIconSize(QSize(30, 20))
        temp_icon.loadFromData(icon_next)
        self.NextButton = QPushButton(icon=QIcon(temp_icon))
        self.NextButton.setObjectName("NextButton")
        self.NextButton.setFixedSize(90, 40)
        self.NextButton.setIconSize(QSize(20, 20))
        self.NextButton.setEnabled(False)
        temp_icon.loadFromData(icon_back)
        self.PreButton = QPushButton(icon=QIcon(temp_icon))
        self.PreButton.setObjectName("BackButton")
        self.PreButton.setFixedSize(90, 40)
        self.PreButton.setIconSize(QSize(20, 20))
        self.PreButton.setEnabled(False)

        # Layouts
        self.timeBox = QHBoxLayout()
        self.timeBox.addWidget(self.time_viewer)
        self.timeBox.addWidget(self.slash)
        self.timeBox.addWidget(self.duration_viewer)

        self.ButtonLayout = QHBoxLayout()
        self.ButtonLayout.addWidget(self.PreButton)
        self.ButtonLayout.addWidget(self.StopButton)
        self.ButtonLayout.addWidget(self.PlayButton)
        self.ButtonLayout.addWidget(self.PauseButton)
        self.ButtonLayout.addWidget(self.NextButton)

        self.DurLayout = QHBoxLayout()
        self.DurLayout.addWidget(self.slider, 3)
        self.DurLayout.addLayout(self.timeBox, 1)

        self.MainBox = QVBoxLayout()
        self.MainBox.addWidget(self.name)
        self.MainBox.addLayout(self.DurLayout)
        self.MainBox.addLayout(self.ButtonLayout)

        self.player_type_box = QVBoxLayout()
        self.player_type_box.addWidget(self.mode_label)
        self.player_type_box.addWidget(self.schedule_mode)
        self.player_type_box.addWidget(self.single_but)
        self.player_type_box.addWidget(self.contract_but)

        self.BigBox = QHBoxLayout()
        self.BigBox.addLayout(self.MainBox)
        self.BigBox.addWidget(self.VolumeSlider)
        self.BigBox.addLayout(self.player_type_box)
        self.setLayout(self.BigBox)

        #Вспомогательные функции
        self.Connection()
        self.VolumeSlider.setValue(50)

    def Connection(self):
        #self.PlayButton.clicked.connect(self.MyPlay)
        self.PauseButton.clicked.connect(self.MyPause)
        self.StopButton.clicked.connect(self.MyStop)

        self.schedule_mode.clicked.connect(self.mode_changed)
        self.but_group.buttonClicked.connect(self.mode_changed)

        self.name.resizeEvent = self.change_label_size
        
    def set_double_player(self, player: QMediaPlayer) -> None:
        self.double_player = player
        
    def load_language(self, lang: str) -> None:
        #self.PlayButton.setText(dictionary['Play'][lang])
        #self.StopButton.setText(dictionary['Stop'][lang])
        #self.PauseButton.setText(dictionary['Pause'][lang])
        self.mode_label.setText(dictionary['Player mode:'][lang])
        self.schedule_mode.setText(dictionary['Schedule mode'][lang])
        self.single_but.setText(dictionary['Single mode'][lang])
        self.contract_but.setText(dictionary['Contract mode'][lang])
        if self.status == self.Stop: self.name.setText(dictionary["Nothing is playing yet"][lang])
        

    def set_mode(self, mode: int) -> None:
        if mode == self.Schedule:
            self.schedule_mode.setChecked(True)
        elif mode == self.Single:
            self.single_but.setChecked(True)
            self.schedule_mode.setChecked(False)
        else:
            self.contract_but.setChecked(True)
            self.schedule_mode.setChecked(False)
        self.mode_changed()

    def mode_changed(self, *args):
        if self.schedule_mode.isChecked():
            self.mode = self.Schedule
            self.single_but.hide()
            self.contract_but.hide()
        else:
            self.single_but.show()
            self.contract_but.show()
            if self.single_but.isChecked():
                self.mode = self.Single
            if self.contract_but.isChecked():
                self.mode = self.Contract
        self.mode_changed_signal.emit()

    def connect_playlist(self, playlist: Songlist) -> None:
        self.playlist = playlist

    def change_label_size(self, e):
        QLabel.resizeEvent(self.name, e)
        font = self.name.font()
        font.setPixelSize(self.name.size().height() // 2)
        self.name.setFont(font)

    def change_volume(self, volume: int):
        self.player.setVolume(volume)
        self.VolumeSlider.setValue(volume)
        self.VolumeSlider.setToolTip(str(volume))

    def duration_view(self, duration: int):
        #if duration < 0: duration = 0
        print(duration)
        self.slider.setMaximum(duration)
        self.duration_viewer.display(self.hhmmss(duration))

    def update_position(self, position):
        if position > 0:
            if self.playlist and position != 0 and position == self.player.duration():
                if self.playlist.currentItem().getCickle():
                    self.MyPlay(self.song)
                elif self.mode == self.Schedule or self.mode == self.Single:
                    self.MyStop()
                elif self.mode == self.Contract:
                    self.NextButton.click()
                    self.parent().play()
            self.slider.blockSignals(True)
            self.slider.setSliderPosition(position)
            self.slider.blockSignals(False)
            self.time_viewer.display(self.hhmmss(position))

    def change_position(self, position):
        self.player.setPosition(position)
        if self.double_player: self.double_player.setPosition(position)

    def hhmmss(self, ms: int):
        h, r = divmod(ms, 3600000)
        m, r = divmod(r, 60000)
        s, _ = divmod(r, 1000)
        return ("%02d:%02d:%02d" % (h, m, s)) if h else ("%02d:%02d" % (m, s))

    def set_song(self, path: str):
        self.song = path

    def MyPlay(self, name=None):
        print('Play')
        if self.status == self.Pause:
            self.player.play()
            if self.double_player: self.double_player.play()
            self.status = self.Play
            return
        if name:
            self.song = name
        if self.song:
            if self.status == self.Play:
                self.player.stop()
                if self.double_player: self.double_player.stop()
            if self.song.split('.')[-1] in mus_extensions or self.song.split('.')[-1] in video_extensions:
                print(self.song)
                
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.song)))
                if self.double_player: self.double_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.song)))
                
                self.player.setPosition(0)
                if self.double_player: self.double_player.setPosition(0)
                
                self.player.play()
                if self.double_player: self.double_player.play()
            else:
                self.parent().play()
            self.name.setText(self.song.split('/')[-1].split('.')[0])
            self.status = self.Play

    def MyPause(self):
        if self.status == self.Play:
            self.player.pause()
            if self.double_player: self.double_player.pause()
            self.status = self.Pause

    def MyStop(self):
        print('Stop!')
        self.player.stop()
        if self.double_player: self.double_player.stop()
        self.name.setText(dictionary['Nothing is playing yet'][read_set('language')])
        self.duration_viewer.display('00:00')
        self.time_viewer.display('00:00')
        self.status = self.Stop

    def keyPressEvent(self, event)-> None:
        if event.key() == Qt.Key_Space:
            if self.status == self.Play:
                self.MyPause()
            elif self.status == self.Pause:
                self.MyPlay()
        elif event.key() == Qt.Key_Up:
            self.PreButton.click()
        elif event.key() == Qt.Key_Down:
            self.NextButton().click()
        return super().keyPressEvent(event)