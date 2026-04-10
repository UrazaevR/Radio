import sys
from PyQt5.QtWidgets import QApplication
from Schedule import Scheduler
from Playlist import MainPlaylistWidget, Searcher
from Player import MyPlayer


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Searcher()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())