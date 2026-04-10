# -*- coding: cp1251 -*-
import os
import random
import sqlite3
from turtle import clear
from FOR_INI import save_conf, read_set
from Globals import *


def create_bd():
    if not os.path.exists('Songs.db') or os.path.getsize('Songs.db') == 0:
        with open('Songs.db', 'w') as _: pass
        con = sqlite3.connect('Songs.db')
        cur = con.cursor()
        cur.execute('''
        CREATE TABLE Playlists (
            Name       STRING  UNIQUE
                            NOT NULL,
            SongsId    STRING,
            CurrentNum INTEGER DEFAULT (0) 
        );
        ''')
        cur.execute('''
        CREATE TABLE Songs (
            Id       INTEGER PRIMARY KEY ASC ON CONFLICT ROLLBACK AUTOINCREMENT
                            UNIQUE
                            NOT NULL,
            Filepath STRING  UNIQUE
                            NOT NULL
        );
        ''')
        con.commit()


def cursor():
    con = sqlite3.connect('./Songs.db')
    return con.cursor()


def getPlaylists() -> list:
    cur = cursor()
    ans = cur.execute('SELECT Name FROM Playlists').fetchall()
    if ans is None:
        return []
    return list(map(lambda x: str(x[0]), ans))


def get_song_id(path: str) -> int:
    cur = cursor()
    ans = cur.execute('SELECT Id FROM Songs WHERE Filepath = ?', (path,)).fetchone()
    if ans is None:
        return -1
    return ans[0]


def get_song_like(name: str) -> list:
    cur = cursor()
    s = f"SELECT id FROM Songs WHERE Filepath LIKE '%{name}%'"
    ans = cur.execute(s).fetchall()
    if not ans: ans = []
    return list(map(lambda x: int(x[0]), ans))


def search_song_in_playlist(id: int) -> list:
    cur = cursor()
    s = f"SELECT Name FROM Playlists WHERE SongsID LIKE '({id},'"
    ans = cur.execute(s).fetchall()
    if not ans: ans = []
    return ans


def get_song(id: int) -> str:
    cur = cursor()
    ans = cur.execute('SELECT Filepath FROM Songs WHERE Id = ?', (id,)).fetchone()
    if ans is not None:
        return ans[0]
    return ''


def add_song(path: str):
    if get_song_id(path) == -1:
        cur = cursor()
        cur.execute('INSERT INTO Songs(Filepath) VALUES(?)', (path,))
        cur.connection.commit()


def add_playlist(name: str) -> bool:
    if name not in getPlaylists():
        cur = cursor()
        cur.execute('INSERT Into PLaylists(Name) VALUES(?)', (name,))
        cur.connection.commit()
        return True
    return False


def delete_playlist(name: str) -> bool:
    if name in getPlaylists():
        cur = cursor()
        cur.execute('DELETE FROM Playlists WHERE Name = ?', (name,))
        cur.connection.commit()
        return True
    return False


def rename_playlist(name: str, new_name: str) -> bool:
    if name in getPlaylists() and new_name not in getPlaylists():
        cur = cursor()
        cur.execute('UPDATE Playlists SET Name = ? WHERE Name = ?', (new_name, name, ))
        cur.connection.commit()
        return True
    return False


def save_playlist(playlist, songs: list or tuple, current_num: int=0):
    if str(playlist) in getPlaylists():
        cur = cursor()
        for elem in songs:
            add_song(elem[0])
        ans = ''
        for elem in list(map(lambda x: (get_song_id(x[0]), int(x[-1])), songs)):
            ans += str(elem) + ','
        cur.execute('UPDATE Playlists SET SongsId = ?, CurrentNum = ? WHERE Name = ?', (ans, current_num, playlist, ))
        cur.connection.commit()


def get_songs(playlist: str):
    if playlist in getPlaylists():
        cur = cursor()
        ans = cur.execute('SELECT SongsId FROM Playlists WHERE Name = ?', (playlist,)).fetchone()[0]
        id = cur.execute('SELECT CurrentNum FROM Playlists WHERE Name = ?', (playlist,)).fetchone()[0]
        if not ans:
            return []
        ans = ans.strip(',').strip('(').strip(')').split('),(')
        for i in range(len(ans)):
            ans[i] = ans[i].split(',')
            ans[i] = (get_song(int(ans[i][0])), int(ans[i][-1]))
        return [id, ans]
    return ''


def get_current(playlist: str) -> int:
    if playlist in getPlaylists():
        cur = cursor()
        return int(cur.execute('SELECT CurrentNum From Playlists WHERE Name = ?', (playlist,)).fetchone()[0])
    return -1


from PyQt5.QtWidgets import QApplication, QListWidget, QListWidgetItem, QAbstractItemView, QWidget,\
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QComboBox, QInputDialog, QMessageBox,\
    QProgressDialog, QLineEdit
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QSize
from PyQt5.QtGui import QKeyEvent, QPixmap, QColor, QIcon
import eyed3


class SongItem(QListWidgetItem):
    def __init__(self, path='', cickle=False, item_size=QSize(0, 20)):
        super().__init__()
        self.setCickle(cickle)
        self.setPath(path)
        self.setSizeHint(item_size)

    def setCickle(self, fl: bool=True):
        self.cickle = bool(fl)
        if self.cickle:
            self.setBackground(QColor(200, 200, 200))
        else:
            self.setBackground(QColor(255, 255, 255))

    def setPath(self, path):
        self.path = path
        try:
            aud = eyed3.load(path)
            if aud.tag:
                title = aud.tag.title
                artist = aud.tag.artist
                if title is None:
                    title = ''
                if artist is None:
                    artist = ''
                self.setText(str(self.path.split('/')[-1]).strip() + ' ' + title + ' ' + artist)
            else:
                self.setText(self.path.split('/')[-1])
        except Exception as _:
            self.setText(self.path.split('/')[-1])
        if not os.path.exists(path):
            self.setBackground(QColor('red'))
        self.load_icon()

    def load_icon(self):
        if self.getpath().split('.')[-1] in mus_extensions:
            icon = QPixmap()
            icon.loadFromData(mus_icon)
            self.setIcon(QIcon(icon))
        elif self.getpath().split('.')[-1] in video_extensions:
            icon = QPixmap()
            icon.loadFromData(video_icon)
            self.setIcon(QIcon(icon))
        elif self.getpath().split('.')[-1] in img_extensions:
            icon = QPixmap()
            icon.loadFromData(photo_icon)
            self.setIcon(QIcon(icon))

    def getCickle(self) -> bool:
        return self.cickle

    def getpath(self):
        return self.path

    def setSizeHint(self, size: QSize) -> None:
        if size.height() > 10:
            QListWidgetItem.setSizeHint(self, size)
            new_font = self.font()
            new_font.setPixelSize(self.sizeHint().height() - 8)
            self.setFont(new_font)


class Songlist(QListWidget, QObject):
    drop_signal = pyqtSignal()

    def __init__(self, parent=None, songs=None):
        super(Songlist, self).__init__(parent)
        if songs is not None:
            self.addItems(songs)
        self.setSortingEnabled(False)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        
        self.item_size = QSize(0, 20)

    def currentRow(self) -> int:
        if QListWidget.currentRow(self) is None:
            self.setCurrentRow(0)
        return QListWidget.currentRow(self)

    def setCurrentRow(self, row: int) -> None:
        if row > self.count() - 1:
            row = 0
        if row < 0:
            row += self.count()
        QListWidget.setCurrentRow(self, row)

    def addItem(self, path: str, cickle: bool=False):
        QListWidget.addItem(self, SongItem(path, cickle, self.item_size))

    def addItems(self, items):
        for item in sorted(items):
            self.addItem(item)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        sp = []
        sp.extend(mus_extensions)
        sp.extend(img_extensions)
        sp.extend(video_extensions)
        md = event.mimeData()
        newelems = []
        if md.hasUrls():
            for url in md.urls():
                if os.path.isfile(url.toLocalFile()):
                    print(os.path.splitext(url.toLocalFile())[-1])
                    if os.path.splitext(url.toLocalFile())[-1][1:] in sp:
                        newelems.append(url.toLocalFile())
                else:
                    for root, dirs, files in os.walk(url.toLocalFile()):
                        for file in files:
                            s = ''
                            for b in os.path.join(root, file):
                                if b == '\\':
                                    b = '/'
                                s += b
                            if os.path.splitext(s)[-1][1:] in sp:
                                newelems.append(s)
                                self.drop_signal.emit()
            self.addItems(sorted(newelems))
        else:
            if event.source() == self:
                self.drop_signal.emit()
                event.setDropAction(Qt.MoveAction)
                QListWidget.dropEvent(self, event)
                event.acceptProposedAction()
            elif type(event.source()) == type(self):
                self.drop_signal.emit()
                self.addItem(event.source().currentItem().getpath())
            else:
                self.drop_signal.emit()
                event.accept()


    def wheelEvent(self, event) -> None:
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.item_size = QSize(0, self.item(0).sizeHint().height() + 10)
            elif event.angleDelta().y() < 0:
                self.item_size = QSize(0, self.item(0).sizeHint().height() - 10)
            for i in range(len(self)):
                self.item(i).setSizeHint(self.item_size)
            self.setIconSize(QSize(self.item(0).sizeHint().height() - 4, self.item(0).sizeHint().height() - 4))
        else:
            QListWidget.wheelEvent(self, event)


class MainPlaylistWidget(QWidget):
    Enter_pressed = pyqtSignal()

    def __init__(self):
        super(MainPlaylistWidget, self).__init__()

        self.main_box = QVBoxLayout()
        self.playlists = QComboBox(self)

        self.create_but = QPushButton('Create playlist', self)
        self.create_but.clicked.connect(self.add_playlist)
        self.rename_but = QPushButton('Rename playlist', self)
        self.rename_but.clicked.connect(self.rename_playlist)
        self.delete_but = QPushButton('Delete playlist', self)
        self.delete_but.clicked.connect(self.delete_playlist)

        self.horB = QHBoxLayout()
        self.horB.addWidget(self.playlists, 2)
        self.horB.addWidget(self.create_but, 1)
        self.horB.addWidget(self.rename_but, 1)
        self.horB.addWidget(self.delete_but, 1)

        self.load_playlists()
        self.playlist = Songlist(self)
        self.buttonBox = QVBoxLayout()
        self.playlist_box = QHBoxLayout()

        self.saved = True
        self.name = ''

        self.randomize_but = QPushButton('Randomize')
        self.randomize_but.clicked.connect(self.randomize)
        self.save_but = QPushButton('Save')
        self.save_but.clicked.connect(self.save)
        self.load_but = QPushButton('Load')
        self.load_but.clicked.connect(self.load)
        self.del_but = QPushButton('Delete')
        self.del_but.clicked.connect(self.delete)
        self.clear_but = QPushButton('Clear')
        self.clear_but.clicked.connect(self.clear)        

        self.buttonBox.addWidget(self.randomize_but)
        self.buttonBox.addWidget(self.save_but)
        self.buttonBox.addWidget(self.load_but)
        self.buttonBox.addWidget(self.del_but)
        self.buttonBox.addWidget(self.clear_but)

        self.playlist_box.addWidget(self.playlist)
        self.playlist_box.addLayout(self.buttonBox)

        self.playlist.drop_signal.connect(lambda: self.setSaved(False))
        self.playlist.itemDoubleClicked.connect(lambda x: x.setCickle(not x.getCickle()))
        self.playlists.currentTextChanged.connect(self.setCurrentPlaylist)
        self.setCurrentPlaylist(self.current_playlist())

        self.main_box.addLayout(self.horB)
        self.main_box.addLayout(self.playlist_box)
        self.setLayout(self.main_box)
        self.setSaved()
        
    def load_language(self, lang: str) -> None:
        self.create_but.setText(dictionary['Create playlist'][lang])
        self.rename_but.setText(dictionary['Rename playlist'][lang])
        self.delete_but.setText(dictionary['Delete playlist'][lang])
        self.randomize_but.setText(dictionary['Randomize'][lang])
        self.save_but.setText(dictionary['Save'][lang])
        self.load_but.setText(dictionary['Load'][lang])
        self.del_but.setText(dictionary['Delete'][lang])
        self.clear_but.setText(dictionary['Clear'][lang])
        

    def setSaved(self, fl: bool = True):
        self.saved = fl
        
    def randomize(self) -> None:
        sp = []
        for i in range(len(self.playlist)):
            elem = (self.playlist.item(i).getpath(), self.playlist.item(i).getCickle())
            sp.append(elem)
        sp = random.sample(sp, len(self.playlist))
        self.playlist.clear()
        for item in sp:
            self.playlist.addItem(*item)
        self.setSaved(False)

    def save(self):
        sp = []
        for i in range(len(self.playlist)):
            sp.append((self.playlist.item(i).getpath(), self.playlist.item(i).getCickle()))
        save_playlist(self.name, sp, self.playlist.currentRow())
        self.setSaved()

    def load(self):
        self.clear()
        songs = get_songs(self.name)
        if songs:
            num, songs = songs
            for elem in songs:
                self.playlist.addItem(*elem)
            self.playlist.setCurrentRow(num)
        self.playlists.setCurrentText(self.name)
        self.setSaved()

    def delete(self):
        self.playlist.takeItem(self.playlist.row(self.playlist.selectedItems()[0]))
        self.setSaved(False)

    def clear(self):
        self.playlist.clear()
        self.setSaved(False)

    def setCurrentPlaylist(self, name: str) -> None:
        if name in getPlaylists():
            if name != self.name:
                if not self.saved:
                    dialog = QMessageBox
                    ok = dialog.question(None, '', dictionary['Save changes in current playlist?'][read_set('language')], dialog.Yes | dialog.No | dialog.Cancel)
                    if ok == dialog.Yes:
                        self.save()
                    elif ok == dialog.Cancel:
                        self.playlists.setCurrentText(self.name)
                        return
                self.name = name
                self.load()
        else:
            save_conf('playlist', '')

    def current_playlist(self) -> str:
        return self.playlists.currentText()

    def load_playlists(self):
        self.playlists.clear()
        for pl in sorted(getPlaylists()):
            self.playlists.addItem(pl)

    def add_playlist(self):
        dialog = QInputDialog()
        dialog.setOkButtonText(dictionary['Create'][read_set('language')])
        name, ok = dialog.getText(None, dictionary['New playlist'][read_set('language')], dictionary['Please, write playlist name'][read_set('language')])
        if ok:
            if add_playlist(name):
                self.load_playlists()
                self.playlists.setCurrentText(name)
            else:
                message = QMessageBox(None)
                message.setText('Ops! Something wrong!')
                message.show()

    def rename_playlist(self):
        dialog = QInputDialog()
        dialog.setOkButtonText(dictionary['Rename'][read_set('language')])
        new_name, ok = dialog.getText(None, 'Rename playlist', 'Write new playlist name')
        if ok:
            if rename_playlist(self.current_playlist(), new_name):
                self.load_playlists()
                self.playlists.setCurrentText(new_name)
            else:
                message = QMessageBox(None)
                message.setText(dictionary['Ops! Something wrong!'][read_set('language')])
                message.show()

    def delete_playlist(self):
        dialog = QMessageBox
        ok = dialog.question(None, '', dictionary['Delete playlist'][read_set('language')] + '?', dialog.Yes | dialog.No)
        if ok == dialog.Yes:
            if delete_playlist(self.current_playlist()):
                self.load_playlists()
            else:
                message = QMessageBox(self)
                message.setText(dictionary['Ops! Something wrong!'][read_set('language')])
                message.show()
                
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Delete:
            self.delete()
        elif event.key() == Qt.Key_Up:
            self.playlist.setCurrentRow(self.playlist.currentRow() - 1)
        elif event.key() == Qt.Key_Down:
            self.playlist.setCurrentRow(self.playlist.currentRow() + 1)
        elif event.key() == Qt.Key_Enter:
            self.Enter_pressed.emit()
        return super().keyPressEvent(event)

    def closeEvent(self, event) -> bool:
        if not self.saved:
            dialog = QMessageBox(QMessageBox.Question, '', dictionary['Save changes in current playlist?'][read_set('language')], QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, parent=self)
            dialog.setStyleSheet("QLabel{ color: black}")
            dialog.exec_()
            ok = dialog.standardButton(dialog.clickedButton())
            if ok == dialog.Yes:
                self.save()
                event.accept()
                return True
            elif ok == dialog.No:
                event.accept()
                return True
            elif ok == dialog.Cancel:
                event.ignore()
                return False


class Searcher(QWidget):
    def __init__(self):
        super(Searcher, self).__init__()
        self.inputline = QLineEdit()
        self.label = QLabel('Input song name')
        self.label.setMaximumHeight(50)
        self.label.setAlignment(Qt.AlignHCenter)
        self.search_but = QPushButton('Search')
        self.show_but = QPushButton('Show')
        self.open_but = QPushButton('Open')
        self.sp = Songlist()

        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.label, 0, 0, 1, 4)
        self.main_layout.addWidget(self.inputline, 1, 0)
        self.main_layout.addWidget(self.search_but, 1, 1)
        self.main_layout.addWidget(self.show_but, 1, 2)
        self.main_layout.addWidget(self.open_but, 1, 3)
        self.main_layout.addWidget(self.sp, 2, 0, 4, 4)

        self.setLayout(self.main_layout)

        self.open_but.clicked.connect(self.open)
        self.search_but.clicked.connect(self.search)
        
    def load_language(self, lang: str) -> None:
        self.label.setText(dictionary['Input song name'][lang])
        self.search_but.setText(dictionary['Search'][lang])
        self.show_but.setText(dictionary['Show'][lang])
        self.open_but.setText(dictionary['Open'][lang])

    def open(self):
        if self.sp.currentItem():
            os.startfile(os.path.dirname(self.sp.currentItem().getpath()))

    def search(self):
        self.sp.clear()
        name = self.inputline.text()
        if name:
            ids = get_song_like(name)
            for num, id in enumerate(ids):
                self.sp.addItem(get_song(id))
                self.sp.item(num).setText(self.sp.item(num).getpath())
