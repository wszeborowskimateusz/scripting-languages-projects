#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import stat
import platform
import subprocess
import shutil
import time
from datetime import datetime
try:
    from pwd import getpwuid
except ImportError:
    # This module is not crucial and it only works on Linux
    pass

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

HELP_GUIDE = '''
Możliwe funkcje w programie:
- Menu Folder - pozwala na otworzenie nowego folderu jako folder root
- Po kliknięciu w wybrany nagłówek, zawartość zostanie posortowana względem podanej wartości
- Zaznaczenie pliku tekstowego pozwala na wyświetlenie jego treści
- Menu pod prawym przyciskiem myszy:
    - Otwórz - otwiera plik/folder w okienku systemowym
    - Usuń - usuwa plik/folder, przed usunięciem pyta o potwierdzenie
    - Właściwości - wyświetla właściwości wybranego elementu: typ, rozmiar, datę edycji, właściciela oraz uprawnienia 
'''

AUTHOR_INFO = '''
Program stworzony na potrzeby przedmiotu Języki Programowania 2020
Autor: Mateusz Wszeborowski 165562
'''

CANNOT_OPEN_FILE_DISCLAIMER = 'Nie udało się otworzyć pliku. Najprawdopodobniej nie jest to plik tekstowy.'
EMPTY_FILE_DISCLAIMER = 'Wybrany plik jest pusty.'
NO_PERMISSION_FILE_DISCLAIMER = 'Nie masz uprawnień aby otworzyć ten plik.'
NO_PERMISSION_FILE_DELETE_DISCLAIMER = 'Nie masz uprawnień aby usunąć ten plik.'
NO_PROPERTIES_AVAILABLE = 'Nie udało się wczytać właściwości pliku.'

class PolishQFileSystemModel(QFileSystemModel):
    def headerData(self, section, orientation, role):
        if section == 0 and role == Qt.DisplayRole:
            return "Nazwa"
        elif section == 1 and role == Qt.DisplayRole:
            return "Rozmiar"
        elif section == 3 and role == Qt.DisplayRole:
            return "Data edycji"
        else:
            return super(PolishQFileSystemModel, self).headerData(section, orientation, role)

class Browser(QWidget):
    def __init__(self, file_viewer):
        super(Browser, self).__init__()

        self.file_viewer = file_viewer

        self.treeView = QTreeView()
        self.fileSystemModel = PolishQFileSystemModel(self.treeView)
        self.fileSystemModel.setReadOnly(False)
        
        root = self.fileSystemModel.setRootPath('/')
        self.treeView.setModel(self.fileSystemModel)
        self.treeView.setRootIndex(root)
        self.treeView.setSortingEnabled(True)
        self.treeView.setExpandsOnDoubleClick(True)
        self.treeView.clicked.connect(self.__single_click)
        self.treeView.hideColumn(2)

        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)  
        self.treeView.customContextMenuRequested.connect(self.__create_right_click_menu)  

        Layout = QVBoxLayout(self)
        Layout.addWidget(self.treeView)
        self.setLayout(Layout)

    def __open_file_name_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName = str(QFileDialog.getExistingDirectory(self,"Wybierz folder", options=options))
        if fileName:
            return fileName
        return None

    def set_new_directory(self):
        new_file_name = self.__open_file_name_dialog()
        if new_file_name:
            root = self.fileSystemModel.setRootPath(new_file_name)
            self.treeView.setModel(self.fileSystemModel)
            self.treeView.setRootIndex(root)

    def __open_system_file_browser(self, index):
        path = self.sender().model().filePath(index)
        self.__open_file(path)

    def __delete_file(self, index):
        path = self.sender().model().filePath(index)
        quit_msg = f"Czy jesteś pewien, że chesz usunąć: {path}?"
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle('Czy jesteś pewien?')
        msg_box.setText(quit_msg)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        yes_button = msg_box.button(QMessageBox.Yes)
        yes_button.setText('Tak')
        no_button = msg_box.button(QMessageBox.No)
        no_button.setText('Nie')
        msg_box.exec_()

        if msg_box.clickedButton() == yes_button:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True) 
            except PermissionError:
                self.__show_no_permission_popup()

    def __show_no_permission_popup(self):
        self.no_permision_popup = QMessageBox()
        self.no_permision_popup.setWindowTitle("Brak uprawnień")
        self.no_permision_popup.setText(NO_PERMISSION_FILE_DELETE_DISCLAIMER)
        x = self.no_permision_popup.exec_() 

    def __create_right_click_menu(self, event):
        self.right_click_menu = QMenu(self.treeView)
        open_action = self.right_click_menu.addAction("Otwórz")
        delete_action = self.right_click_menu.addAction("Usuń")
        properties_action = self.right_click_menu.addAction("Właściwości")
        picked_action = self.right_click_menu.exec_(self.treeView.mapToGlobal(event))
        if picked_action:
            index = self.treeView.indexAt(event)
            if index.isValid():
                if picked_action == open_action:
                    self.__open_system_file_browser(index)
                elif picked_action == delete_action:
                    self.__delete_file(index)
                elif picked_action == properties_action:
                    self.__show_file_properties(index)

    def __single_click(self, index):
        path = self.sender().model().filePath(index)
        if os.path.isfile(path):
            try:
                with open(path, 'r') as myfile:
                    data = myfile.read()
                    if not data or data == '' or data.isspace():
                        data = EMPTY_FILE_DISCLAIMER
                    self.file_viewer.setPlainText(data)
            # File is not a text fileopen_file
            except UnicodeDecodeError:
                self.file_viewer.setPlainText(CANNOT_OPEN_FILE_DISCLAIMER)
            except PermissionError:
                self.file_viewer.setPlainText(NO_PERMISSION_FILE_DISCLAIMER)

    def __open_file(self, path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def __show_file_properties(self, index):
        path = self.sender().model().filePath(index)
        self.file_properties_popup = QMessageBox()
        self.file_properties_popup.setWindowTitle("Właściwości")
        self.file_properties_popup.setText(self.__build_properties_text(path))
        x = self.file_properties_popup.exec_() 

    def __build_properties_text(self, path):
        try:
            text = f'Nazwa: {path}\n'
            if os.path.isfile(path):
                text += 'Typ: Plik\n'
            elif os.path.isdir(path):
                text += 'Typ: Folder\n'
            file_stats = os.stat(path)
            text += f'Rozmiar: {os.path.getsize(path)} bajtów\n'
            text += f'Data edycji: {self.__get_formated_modified_date(path)}\n'
            if sys.platform == "linux" or sys.platform == "linux2":
                text += f'Właściciel: {getpwuid(file_stats.st_uid).pw_name}\n'
            text += f'Uprawnienia: {stat.filemode(file_stats.st_mode)}'
            return text
        except:
            return NO_PROPERTIES_AVAILABLE

    def __get_formated_modified_date(self, path):
        timestamp = os.path.getmtime(path)
        date_time = datetime.fromtimestamp(timestamp)
        return date_time.strftime("%d.%m.%Y %H:%M")


class MainLayout(QWidget):
    def __init__(self, left_widget, right_widget):
        super(MainLayout, self).__init__()

        hbox = QHBoxLayout(self)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([400, 500])
        hbox.addWidget(splitter)
        self.setLayout(hbox)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(1000, 600)
        self.setWindowTitle("Eksplorator plików")

        self.file_viewer = QPlainTextEdit()
        self.file_viewer.setReadOnly(True)
        self.tree_widget = Browser(self.file_viewer)

        self.main_layout = MainLayout(self.tree_widget, self.file_viewer)
        self.setCentralWidget(self.main_layout)

        self.statusBar()
        self.__file_menu()
        self.__help_menu()
        self.__about_menu()


    def __file_menu(self):
        open_folder_menu = QAction("Otwórz", self)
        open_folder_menu.setShortcut("Ctrl+O")
        open_folder_menu.setStatusTip('Otwórz folder')
        open_folder_menu.triggered.connect(self.tree_widget.set_new_directory)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&Folder')
        fileMenu.addAction(open_folder_menu)

    def __help_menu(self):
        help_folder_menu = QAction("Otwórz przewodnik", self)
        help_folder_menu.setShortcut("Ctrl+H")
        help_folder_menu.setStatusTip('Przewodnik')
        help_folder_menu.triggered.connect(self.__open_guide)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&Pomoc')
        fileMenu.addAction(help_folder_menu)

    def __open_guide(self):
        self.help_guide = QMessageBox()
        self.help_guide.setWindowTitle("Pomoc")
        self.help_guide.setText(HELP_GUIDE)
        x = self.help_guide.exec_() 

    def __about_menu(self):
        about_menu = QAction("Informacje o autorze", self)
        about_menu.setShortcut("Ctrl+I")
        about_menu.setStatusTip('Informacje o autorze')
        about_menu.triggered.connect(self.__open_about_info)

        mainMenu = self.menuBar()
        about = mainMenu.addMenu('&O autorze')
        about.addAction(about_menu)

    def __open_about_info(self):
        self.about_info = QMessageBox()
        self.about_info.setWindowTitle("O autorze")
        self.about_info.setText(AUTHOR_INFO)
        x = self.about_info.exec_() 

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())