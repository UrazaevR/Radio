# -*- coding: cp1251 -*-
from PyQt5.QtWinExtras import QtWin

try:
    myappid = 'mycompany.myproduct.Radio.2.0.0'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QDockWidget, QTabWidget, QAction
import sys, os
from PyQt5.QtCore import Qt
from FOR_INI import read_set, save_conf, Settings
from AuthorWin import Author
from Playlist import MainPlaylistWidget, Searcher, create_bd
from Schedule import Scheduler
from Player import MyPlayer
from Video import VideoSettings
from Globals import *
from log import log


if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


# os.environ['QT_MULTIMEDIA_PREFERRED_PLUGINS'] = 'windowsmediafoundation'
os.environ['QT_MULTIMEDIA_PREFERRED_PLUGINS'] = 'directshow'


class Radio(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabPosition(Qt.LeftDockWidgetArea, QTabWidget.East)
        self.setTabPosition(Qt.RightDockWidgetArea, QTabWidget.West)
        self.setTabPosition(Qt.TopDockWidgetArea, QTabWidget.North)
        self.setTabPosition(Qt.BottomDockWidgetArea, QTabWidget.North)
        self.setWindowTitle('Radio')
        icon = QIcon()
        icon.addPixmap(QPixmap('ICONS/icon.ico'))
        self.setWindowIcon(icon)
        self.player = MyPlayer()
        self.searcher = Searcher()
        self.playlist_wid = MainPlaylistWidget()
        self.schedule = Scheduler()
        self.video_wid = VideoSettings()
        self.settings = Settings()
        self.author_win = Author()
        self.setCentralWidget(self.player)
        self.centralWidget().setContextMenuPolicy(Qt.ActionsContextMenu)

        self.small = False
        self.current_type = ''

        self.settings_show = QAction('Settings')
        self.pllst_sh_hd = QAction('Hide playlist')
        self.sched_sh_hd = QAction('Hide scheduler')
        self.search_sh_hd = QAction('Hide searcher')
        self.video_sh_hd = QAction('Hide video_panel')
        self.author_sh_hd = QAction('Show author')

        self.dock_playlist = QDockWidget('Playlists')
        self.dock_playlist.setWidget(self.playlist_wid)

        self.dock_searcher = QDockWidget('Searcher')
        self.dock_searcher.setWidget(self.searcher)

        self.dock_schedule = QDockWidget('Schedule settings')
        self.dock_schedule.setWidget(self.schedule)

        self.dock_video_panel = QDockWidget('Video settings')
        self.dock_video_panel.setWidget(self.video_wid)

        self.init_gui()
        self.load_style()
        self.load_language(read_set('language'))
        log('Программа запущена')

    def init_gui(self):
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_searcher)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_playlist)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_schedule)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_video_panel)

        self.centralWidget().addActions([self.settings_show, self.pllst_sh_hd, self.sched_sh_hd,
                                         self.search_sh_hd, self.video_sh_hd, self.author_sh_hd])

        self.dock_schedule.visibilityChanged.connect(self.sh_hd_fun)
        self.dock_searcher.visibilityChanged.connect(self.sh_hd_fun)
        self.dock_playlist.visibilityChanged.connect(self.sh_hd_fun)
        self.dock_video_panel.visibilityChanged.connect(self.sh_hd_fun)

        self.settings_show.triggered.connect(self.settings.show)
        self.pllst_sh_hd.triggered.connect(self.show_hide_playlist)
        self.search_sh_hd.triggered.connect(self.show_hide_searcher)
        self.sched_sh_hd.triggered.connect(self.show_hide_schedule)
        self.video_sh_hd.triggered.connect(self.show_hide_video)
        self.author_sh_hd.triggered.connect(self.show_hide_author)

        self.player.NextButton.setEnabled(True)
        self.player.NextButton.clicked.connect(self.next)
        self.player.PreButton.setEnabled(True)
        self.player.PreButton.clicked.connect(self.previous)
        self.player.PlayButton.clicked.connect(self.play)
        self.player.player.setVideoOutput(self.video_wid.video_win.video)
        self.player.connect_playlist(self.playlist_wid.playlist)
        self.player.set_double_player(self.video_wid.player)
        
        self.player.MyStop = self.MyStop
        
        self.settings.apply_but.clicked.connect(self.apply_settings)
        self.settings.save_but.clicked.connect(self.save_settings)
        
        self.playlist_wid.Enter_pressed.connect(self.play)

        self.schedule.bell_before.connect(self.bell_before)
        self.schedule.bell_after.connect(self.bell_after)
        
        self.load_ini()
        
    def load_ini(self) -> None:
        self.player.change_volume(int(read_set('volume')))
        mode = read_set('mode')
        if mode == 'single':
            mode = self.player.Single
        elif mode == 'contract':
            mode = self.player.Contract
        elif mode == 'schedule':
            mode = self.player.Schedule
        self.player.set_mode(mode)
        self.playlist_wid.setCurrentPlaylist(read_set('playlist'))
        self.schedule.delay.setValue(int(read_set('delay')))
        self.schedule.bells.setChecked(read_set('bells') == 'True')
        
        if read_set('search', 'Visible') == '0':
            self.dock_searcher.hide()
        if read_set('video_wid', 'Visible') == '0':
            self.dock_video_panel.hide()
        if read_set('schedule', 'Visible') == '0':
            self.dock_schedule.hide()
        if read_set('playlist', 'Visible') == '0':
            self.dock_playlist.hide()
            
    def load_language(self, lang: str) -> None:
        self.settings_show.setText(dictionary['Settings'][lang])
        if self.dock_schedule.isVisible():
            self.sched_sh_hd.setText(dictionary['Hide scheduler'][lang])
        else:
            self.sched_sh_hd.setText(dictionary['Show scheduler'][lang])
        if self.dock_searcher.isVisible():
            self.search_sh_hd.setText(dictionary['Hide searcher'][lang])
        else:
            self.search_sh_hd.setText(dictionary['Show searcher'][lang])
        if self.dock_playlist.isVisible():
            self.pllst_sh_hd.setText(dictionary['Hide playlist'][lang])
        else:
            self.pllst_sh_hd.setText(dictionary['Show playlist'][lang])
        if self.dock_video_panel.isVisible():
            self.video_sh_hd.setText(dictionary['Hide video_panel'][lang])
        else:
            self.video_sh_hd.setText(dictionary['Show video_panel'][lang])
        if self.author_win.isVisible():
            self.author_sh_hd.setText(dictionary['Hide author'][lang])
        else:
            self.author_sh_hd.setText(dictionary['Show author'][lang])

        self.dock_playlist.setWindowTitle(dictionary['Playlists'][lang])
        self.dock_searcher.setWindowTitle(dictionary['Searcher'][lang])
        self.dock_schedule.setWindowTitle(dictionary['Schedule settings'][lang])
        self.dock_video_panel.setWindowTitle(dictionary['Video settings'][lang])
        
        self.player.load_language(lang)
        self.video_wid.load_language(lang)
        self.searcher.load_language(lang)
        self.playlist_wid.load_language(lang)
        self.schedule.load_language(lang)

    def apply_settings(self) -> None:
        self.settings.save_set()
        self.load_language(read_set('language'))
        
    def save_settings(self) -> None:
        self.apply_settings()
        self.settings.hide()
    
    def load_style(self) -> None:
        if os.path.exists('style.css') and os.path.getsize('style.css') != 0:
            with open('style.css', 'r') as file:
                style = ''.join(file.readlines())
                self.setStyleSheet(style)

    def show_hide_playlist(self):
        if self.dock_playlist.isVisible():
            self.dock_playlist.hide()
        else:
            self.dock_playlist.show()

    def show_hide_schedule(self):
        if self.dock_schedule.isVisible():
            self.dock_schedule.hide()
        else:
            self.dock_schedule.show()

    def show_hide_searcher(self):
        if self.dock_searcher.isVisible():
            self.dock_searcher.hide()
        else:
            self.dock_searcher.show()

    def show_hide_video(self):
        if self.dock_video_panel.isVisible():
            self.dock_video_panel.hide()
        else:
            self.dock_video_panel.show()

    def show_hide_author(self):
        if self.author_win.isVisible():
            self.author_win.hide()
        else:
            self.author_win.show()

    def sh_hd_fun(self, fl: bool):
        if self.dock_schedule.isVisible():
            self.sched_sh_hd.setText('Hide scheduler')
        else:
            self.sched_sh_hd.setText('Show scheduler')
        if self.dock_searcher.isVisible():
            self.search_sh_hd.setText('Hide searcher')
        else:
            self.search_sh_hd.setText('Show searcher')
        if self.dock_playlist.isVisible():
            self.pllst_sh_hd.setText('Hide playlist')
        else:
            self.pllst_sh_hd.setText('Show playlist')
        if self.dock_video_panel.isVisible():
            self.video_sh_hd.setText('Hide video_panel')
        else:
            self.video_sh_hd.setText('Show video_panel')
        if self.author_win.isVisible():
            self.author_sh_hd.setText('Hide author')
        else:
            self.author_sh_hd.setText('Show author')
        self.load_language(read_set('language'))

    def bell_before(self):
        try:
            if self.player.mode == self.player.Schedule:
                self.player.MyStop()
            log('Звонок на урок, песня остановлена')
        except Exception as ex:
            log('Ошибка: ' + ex)

    def bell_after(self):
        try:
            if self.player.mode == self.player.Schedule:
                self.play()
                self.next()
            log('Звонок с урока, песня запущена')
        except Exception as ex:
            log('Ошибка: ' + ex)

    def play(self, path=None):
        print(path)
        if not path: path = self.playlist_wid.playlist.currentItem().getpath()
        if path.split('.')[-1] in mus_extensions or path.split('.')[-1] in video_extensions:
            self.player.set_song(path)
            self.player.MyPlay()
            if path.split('.')[-1] in mus_extensions:
                self.current_type = 'mus'
            else:
                self.current_type = 'vid'
                self.video_wid.video_win.video.show()
                self.video_wid.video_win.curtain.hide()
        else:
            self.video_wid.set_curtain(path)
            self.player.MyStop()
            self.player.name.setText(path.split('/')[-1].split('.')[0])
            if self.current_type == 'vid':
                self.video_wid.hide_video_but.click()
            self.video_wid.show_curtain_but.click()
            self.current_type = 'img'

    def MyStop(self):
        MyPlayer.MyStop(self.player)
        if self.current_type == 'vid':
            self.video_wid.hide_video_but.click()
            self.video_wid.show_curtain_but.click()
    
    def en_dis_bells(self):
         self.schedule.flag_bell = (self.player.mode == self.player.Schedule)

    def next(self):
        self.playlist_wid.playlist.setCurrentRow(self.playlist_wid.playlist.currentRow() + 1)

    def previous(self):
        self.playlist_wid.playlist.setCurrentRow(self.playlist_wid.playlist.currentRow() - 1)

    def mouseDoubleClickEvent(self, e) -> None:
        if not self.small:
            self.close_geometry = self.geometry()
            self.dock_playlist.hide()
            self.dock_searcher.hide()
            self.dock_schedule.hide()
            self.dock_video_panel.hide()
            self.resize(546, 142)
            x = QApplication.desktop().availableGeometry().width() - 546
            y = QApplication.desktop().availableGeometry().height() - 142
            self.move(x, y)
            self.small = True
        else:
            self.setGeometry(self.close_geometry)
            self.dock_playlist.show()
            self.dock_searcher.show()
            self.dock_schedule.show()
            self.dock_video_panel.show()
            self.small = False

    def closeEvent(self, a0) -> None:
        save_conf('delay', str(self.schedule.delay.value()))
        save_conf('playlist', self.playlist_wid.current_playlist())
        save_conf('volume', str(self.player.VolumeSlider.value()))
        
        if self.schedule.bells.isChecked():
            save_conf('bells', 'True')
        else:
            save_conf('bells', 'False')
        
        if self.player.mode == self.player.Single:
            save_conf('mode', 'single')
        elif self.player.mode == self.player.Contract:
            save_conf('mode', 'Contract')
        elif self.player.mode == self.player.Schedule:
            save_conf('mode', 'Schedule')
            
        if self.dock_searcher.isVisible():
            save_conf('search', '1', 'Visible')
        else:
            save_conf('search', '0', 'Visible')
        if self.dock_video_panel.isVisible():
            save_conf('video_wid', '1', 'Visible')
        else:
            save_conf('video_wid', '0', 'Visible')
        if self.dock_schedule.isVisible():
            save_conf('schedule', '1', 'Visible')
        else:
            save_conf('schedule', '0', 'Visible')
        if self.dock_playlist.isVisible():
            save_conf('playlist', '1', 'Visible')
        else:
            save_conf('playlist', '0', 'Visible')
        self.video_wid.video_win.hide()
        self.settings.hide()
        
        if self.playlist_wid.closeEvent(a0):
            log('Завершение работы')
            return super().closeEvent(a0)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    create_bd()
    app = QApplication(sys.argv)
    form = Radio()
    form.show()
    sys.exit(app.exec())
