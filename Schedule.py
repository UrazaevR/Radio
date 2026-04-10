# -*- coding: cp1251 -*-
from PyQt5.QtWidgets import QWidget, QLabel, QTableWidget, QSpinBox, QCheckBox, QGridLayout, QTableWidgetItem, \
    QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QColor
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
import os
from Globals import *
from datetime import datetime, timedelta
import csv


def load_schedule() -> list:
    if os.path.exists('Schedule.csv'):
        with open('Schedule.csv', 'r') as file:
            reader = csv.reader(file, delimiter=';')
            return [[x.strip().rjust(5, '0') for x in row] for row in reader]
    else:
        with open('Schedule.csv', 'w') as _: pass
        return []


def save_schedule(sched: list):
    with open('Schedule.csv', 'w') as file:
        writer = csv.writer(file, delimiter=';', lineterminator="\r")
        writer.writerows(sched)


class Scheduler(QWidget):
    bell_before = pyqtSignal()
    bell_after = pyqtSignal()
    BEFORE_BELL = 1
    AFTER_BELL = 2

    def __init__(self):
        super(Scheduler, self).__init__()
        self.flag_bell = True

        self.label = QLabel('Schedule editor')
        self.label.setAlignment(Qt.AlignHCenter)
        self.table = QTableWidget()
        self.delay = QSpinBox(minimum=-600, maximum=600, value=0, suffix=' sec')
        self.bells = QCheckBox('Bells')
        self.but_add = QPushButton('Add lesson')
        self.but_remove = QPushButton('Remove lesson')
        self.but_save = QPushButton('Save schedule')
        self.but_load = QPushButton('Load schedule')

        self.timer = QTimer()
        self.bell_player = QMediaPlayer(self)

        self.lab = QLabel('Delay:')
        self.lab.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.delay_box = QHBoxLayout()
        self.delay_box.addWidget(self.bells)
        self.delay_box.addWidget(self.lab)
        self.delay_box.addWidget(self.delay)

        self.but_box = QHBoxLayout()
        self.but_box.addWidget(self.but_add)
        self.but_box.addWidget(self.but_remove)
        self.but_box.addWidget(self.but_save)
        self.but_box.addWidget(self.but_load)

        self.main_box = QGridLayout()
        self.main_box.addWidget(self.label, 0, 0, 1, 2)
        self.main_box.addLayout(self.delay_box, 1, 0, 1, 2)
        self.main_box.addWidget(self.table, 2, 0, 1, 2)
        self.main_box.addLayout(self.but_box, 3, 0, 1, 2)

        self.setLayout(self.main_box)
        self.initUI()

    def initUI(self):
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Start lesson', 'End lesson'])
        self.table.resizeEvent = self.resize_cells
        self.load_table()

        self.but_add.clicked.connect(lambda: self.table.setRowCount(self.table.rowCount() + 1))
        self.but_remove.clicked.connect(lambda: self.table.removeRow(self.table.currentRow()))

        self.but_load.clicked.connect(self.load_table)
        self.but_save.clicked.connect(self.save_table)

        self.timer.timeout.connect(self.check_bell)
        self.timer.start(1000)

    def check_bell(self):
        if self.bells.isChecked() and self.flag_bell:
            for i in range(self.table.rowCount()):
                if self.table.item(i, 0):
                    if self.table.item(i, 0).text().strip().rjust(5, '0') + ':00' == \
                            (datetime.today() + timedelta(seconds=self.delay.value() + 51)).time().strftime('%H:%M:%S'):
                        self.run_bell(self.BEFORE_BELL)
                if self.table.item(i, 1):
                    if self.table.item(i, 1).text().strip().rjust(5, '0') + ':00' == \
                            (datetime.today() + timedelta(seconds=self.delay.value() + 51)).time().strftime('%H:%M:%S'):
                        self.run_bell(self.AFTER_BELL)
            for i in range(self.table.rowCount()):
                if self.table.item(i, 0):
                    if self.table.item(i, 0).text().strip().rjust(5, '0') + ':00' == \
                            (datetime.today() + timedelta(seconds=self.delay.value())).time().strftime('%H:%M:%S'):
                        self.table.item(i, 0).setBackground(QColor(30, 255, 30))
                        self.bell_before.emit()
                if self.table.item(i, 1):
                    if self.table.item(i, 1).text().strip().rjust(5, '0') + ':00' == \
                            (datetime.today() + timedelta(seconds=self.delay.value())).time().strftime('%H:%M:%S'):
                        self.table.item(i, 1).setBackground(QColor(30, 255, 30))
                        self.bell_after.emit()

    def run_bell(self, type):
        if type == self.BEFORE_BELL:
            bell = QUrl.fromLocalFile('Bells/Defolt/2.wav')
        else:
            bell = QUrl.fromLocalFile('Bells/Defolt/1.wav')
        self.bell_player.setMedia(QMediaContent(bell))
        self.bell_player.play()

    def resize_cells(self, event):
        self.table.setColumnWidth(0, self.table.size().width() // 2 - 10)
        self.table.setColumnWidth(1, self.table.size().width() // 2 - 10)
        QTableWidget.resizeEvent(self.table, event)

    def load_table(self):
        schedule = load_schedule()
        self.table.setRowCount(len(schedule))
        for i, row in enumerate(schedule):
            for j, col in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(col))

    def save_table(self):
        save_schedule([[self.table.item(row, column).text().strip().rjust(5, '0')
                       for column in range(self.table.columnCount())]
                      for row in range(self.table.rowCount())])
        
    def load_language(self, lang: str):
        self.label.setText(dictionary['Schedule editor'][lang])
        self.delay.setSuffix(dictionary['sec'][lang])
        self.bells.setText(dictionary['Bells'][lang])
        self.but_add.setText(dictionary['Add lesson'][lang])
        self.but_remove.setText(dictionary['Remove lesson'][lang])
        self.but_save.setText(dictionary['Save schedule'][lang])
        self.but_load.setText(dictionary['Load schedule'][lang])
        self.lab.setText(dictionary['Delay'][lang] + ':')
        self.table.setHorizontalHeaderLabels([dictionary['Start lesson'][lang], dictionary['End lesson'][lang]])
