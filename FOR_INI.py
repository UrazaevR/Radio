# -*- coding: cp1251 -*-
import configparser
import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QSpinBox, QApplication, QPushButton
from Globals import *    


def create_ini():
    x = open('Settings.ini', 'w')
    x.write('\n'.join(['[Settings]', 'volume = 50', 'delay = 0', 'mode = single', 'bells = True', 'playlist = ', 'language = EN', 'autosave = 0', '', '[Visible]', 'video_wid = 1', 'search = 1', 'playlist = 1', 'schedule = 1']))
    x.close()


def read_set(name: str, type: str = 'Settings'):
    if not os.path.exists('Settings.ini') or os.path.getsize('Settings.ini') == 0:
        create_ini()
    config = configparser.ConfigParser()
    config.read('Settings.ini')
    return config[type][name]


def save_conf(name, zn, type: str = 'Settings'):
    if not os.path.exists('Settings.ini') or os.path.getsize('Settings.ini') == 0:
        create_ini()
    config = configparser.ConfigParser()
    config.read('Settings.ini')
    config[type][name] = str(zn)
    with open("settings.ini", "w") as f:
        config.write(f)


class Settings(QWidget):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.setWindowTitle('Settings')
        self.resize(290, 300)
        
        #Layouts
        self.language_box = QHBoxLayout()
        self.autosave_box = QHBoxLayout()
        self.lower_box = QHBoxLayout()
        self.main_box = QVBoxLayout()
        
        #Widgets
        self.save_but = QPushButton('Save')
        self.apply_but = QPushButton('Apply')

        self.lan_label = QLabel('Language')
        self.lan_combo = QComboBox()
        self.autosave_label = QLabel('Autosave')
        self.autosave_spin = QSpinBox(minimum=0, maximum=60, value=int(read_set('autosave')), suffix=' min')
        
        for elem in dictionary.keys():
            for key in dictionary[elem].keys():
                self.lan_combo.addItem(key)
            break
        self.lan_combo.setCurrentText(read_set('language'))

        #Place
        self.language_box.addWidget(self.lan_label)
        self.language_box.addWidget(self.lan_combo)
        
        self.autosave_box.addWidget(self.autosave_label)
        self.autosave_box.addWidget(self.autosave_spin)
        
        self.lower_box.addStretch()
        self.lower_box.addWidget(self.apply_but)
        self.lower_box.addWidget(self.save_but)
        
        self.main_box.addLayout(self.autosave_box)
        self.main_box.addSpacing(50)
        self.main_box.addLayout(self.language_box)
        self.main_box.addStretch()
        self.main_box.addLayout(self.lower_box)
        
        self.setLayout(self.main_box)
        self.load_language()
        
    def save_set(self):
        save_conf('language', self.lan_combo.currentText())
        save_conf('autosave', self.autosave_spin.text().split()[0])
        
    def load_language(self):
        lang = read_set('language')
        self.setWindowTitle(dictionary['Settings'][lang])
        self.save_but.setText(dictionary['Save'][lang])
        self.apply_but.setText(dictionary['Apply'][lang])
        self.lan_label.setText(dictionary['Language'][lang])
        self.autosave_label.setText(dictionary['Autosave'][lang])
        self.autosave_spin.setSuffix(dictionary['min'][lang])
        

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Settings()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())