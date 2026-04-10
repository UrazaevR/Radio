from PyQt5 import QtCore, QtGui, QtWidgets
from Globals import me_photo
import sys


class Ui_Author(object):
    def setupUi(self, Author):
        Author.setObjectName("Author")
        Author.setWindowModality(QtCore.Qt.WindowModality.NonModal)
        Author.resize(624, 444)
        self.photo = QtWidgets.QLabel(parent=Author)
        self.photo.setGeometry(QtCore.QRect(10, 10, 341, 411))
        self.photo.setObjectName("photo")
        self.label = QtWidgets.QLabel(parent=Author)
        self.label.setGeometry(QtCore.QRect(370, 10, 251, 411))
        font = QtGui.QFont()
        font.setFamily("MS Reference Sans Serif")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignTop)
        self.label.setObjectName("label")

        self.retranslateUi(Author)
        QtCore.QMetaObject.connectSlotsByName(Author)

    def retranslateUi(self, Author):
        _translate = QtCore.QCoreApplication.translate
        Author.setWindowTitle(_translate("Author", "Автор"))
        self.photo.setText(_translate("Author", "тут должно быть фото"))
        self.label.setText(_translate("Author", "Основной разработчик:\n"
"Уразаев Руслан Равилевич, г.Пенза\n"
"Почта для связи:\n"
"urazaewrus@yandex.ru\n"
"\n"
"Лучшие в мире дизайнеры:\n"
"Карямова Миляуша Ильдаровна,\n"
" г.Набережные Челны\n"
"Кирьякова Алиса Сергеевна,\n"
" г. Москва"))


class Author(QtWidgets.QWidget, Ui_Author):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(me_photo)
        self.photo.setPixmap(pixmap.scaledToWidth(self.photo.width()))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('ICONS/icon.ico'))
        self.setWindowIcon(icon)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = Author()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())