#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import stat
import platform
import subprocess
import shutil
from datetime import datetime
try:
    from pwd import getpwuid
except ImportError:
    # This module is not crucial and it only works on Linux
    pass
import time
from gi import require_version

require_version( 'Gtk', '3.0' )
from gi.repository import Gtk, Gdk, Gio
from gi.repository.GdkPixbuf import Pixbuf


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
NO_PERMISSI__on_file_delete_DISCLAIMER = 'Nie masz uprawnień aby usunąć ten plik.'
NO_PROPERTIES_AVAILABLE = 'Nie udało się wczytać właściwości pliku.'

def show_info_popup(window, title, text):
    dialog = Gtk.MessageDialog(
        window,
        0,
        Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK,
        title,
    )
    dialog.format_secondary_text(text)
    dialog.run()
    dialog.destroy()

def show_yes_no_popup(window, title, text, onYes):
    dialog = Gtk.MessageDialog()
    dialog.set_parent(window)
    dialog.set_title(title)
    dialog.add_button("Tak", Gtk.ResponseType.YES)
    dialog.add_button("Nie", Gtk.ResponseType.NO)
    dialog.format_secondary_text(text)
    response = dialog.run()
    if response == Gtk.ResponseType.YES:
        onYes()
    dialog.destroy()

class FilesTree():
    def __init__(self, text_buffer, window):
        self.__text_buffer = text_buffer
        self.__window = window

    def __populate_file_system_tree(self, tree_store, path, parent=None):
        itemCounter = 0
        try:
            for item in os.listdir(path):
                item_full_name = os.path.join(path, item)
                item_is_folder = os.path.isdir(item_full_name)
                item_size = ""
                item_size_in_bytes = 0
                if not item_is_folder:
                    try:
                        item_size_in_bytes = os.path.getsize(item_full_name)
                        item_size = self.__convert_file_size_to_string(item_size_in_bytes)
                    except PermissionError:
                        pass
                timestamp = os.path.getmtime(item_full_name)
                date_time = datetime.fromtimestamp(timestamp)
                item_modified_date = date_time.strftime("%d.%m.%Y %H:%M")
                current_iter = tree_store.append(parent, 
                    [item, item_full_name, item_size, item_modified_date, item_size_in_bytes, timestamp])

                if item_is_folder: tree_store.append(
                    current_iter, 
                    [None, None, None, None, None, None]
                )

                itemCounter += 1
     
            if itemCounter < 1: tree_store.append(parent, [None, None, None, None, None, None])
        except PermissionError:
            pass

    def __refresh_tree(self):
        self.fileSystemTreeView.set_model(self.get_new_tree_model(self.__path))

    def __convert_file_size_to_string(self, size_in_bytes):
        if size_in_bytes < 1024:
            return str(size_in_bytes) + ' bytes'
        if size_in_bytes < 1024 * 1024:
            return str(round(size_in_bytes / 1024.0, 2)) + ' KB'
        if size_in_bytes < 1024 * 1024 * 1024:
            return str(round(size_in_bytes / (1024.0 * 1024.0), 2)) + ' MB'
        return str(round(size_in_bytes / (1024.0 * 1024.0 * 1024.0), 2)) + ' GB'

    def __on_row_expanded(self, tree_view, tree_iter, _):
        tree_store = tree_view.get_model()
        # Full path
        new_path = tree_store.get_value(tree_iter, 1)

        self.__populate_file_system_tree(tree_store, new_path, tree_iter)
        # remove the first child (dummy node)
        tree_store.remove(tree_store.iter_children(tree_iter))

    def __on_row_collapsed(self, tree_view, tree_iter, _):
        tree_store = tree_view.get_model()

        current_child_iter = tree_store.iter_children(tree_iter)

        while current_child_iter:
            tree_store.remove(current_child_iter)
            current_child_iter = tree_store.iter_children(tree_iter)

        tree_store.append(tree_iter, [None, None, None, None])

    def __on_row_selected(self, tree_view, tree_path, view_column):
        tree_store = tree_view.get_model()

        path = tree_store.get_value(tree_store.get_iter(tree_path), 1)
        if os.path.isfile(path):
            try:
                with open(path, 'r') as myfile:
                    data = myfile.read()
                    if not data or data == '' or data.isspace():
                        data = EMPTY_FILE_DISCLAIMER
                    self.__text_buffer.set_text(data)
            # File is not a text file
            except UnicodeDecodeError:
                self.__text_buffer.set_text(CANNOT_OPEN_FILE_DISCLAIMER)
            except PermissionError:
                self.__text_buffer.set_text(NO_PERMISSION_FILE_DISCLAIMER)

    def __on_right_click(self, widget, event):
        # right mouse click
        if event.button == 3:
            path, _, _, _ = widget.get_path_at_pos(event.x, event.y)
            if path != None:
                tree_store = widget.get_model()
                tree_iter = tree_store.get_iter(path)
                new_path = tree_store.get_value(tree_iter, 1)
                self.__append_right_click_menu(widget, new_path)

    def __append_right_click_menu(self, widget, new_path):
        self.__menu = Gtk.Menu()

        self.__open_menu = Gtk.MenuItem.new_with_label("Otwórz")
        self.__delete_menu = Gtk.MenuItem.new_with_label("Usuń")
        self.__properties_menu = Gtk.MenuItem.new_with_label("Właściwości")

        self.__open_menu.connect('activate', self.__on_file_open(new_path))
        self.__delete_menu.connect('activate', self.__on_file_delete(new_path))
        self.__properties_menu.connect('activate', self.__on_file_properties(new_path))

        self.__menu.append(self.__open_menu)
        self.__menu.append(self.__delete_menu)
        self.__menu.append(self.__properties_menu)
        self.__menu.show_all()
        self.__menu.popup_at_pointer()
        
    def __on_file_open(self, path):
        def open_file_internal(e):
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        
        return open_file_internal

    def __delete_file(self, path):
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            self.__refresh_tree()
        except PermissionError:
            show_info_popup(self.__window, "Brak uprawnień", "Nie ma uprawnień aby usunąć ten plik")

    def __on_file_delete(self, path):
        def delete_file_internal(e):
            quit_msg = f"Czy jesteś pewien, że chesz usunąć: {path}?"
            show_yes_no_popup(
                self.__window, 
                'Czy jesteś pewien?', 
                quit_msg, 
                lambda: self.__delete_file(path)
            )
        
        return delete_file_internal

    def __on_file_properties(self, path):
        def file_properties_internal(e):
            show_info_popup(self.__window, "Właściwości", self.__build_properties_text(path))
        
        return file_properties_internal

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
            if platform == "linux" or platform == "linux2":
                text += f'Właściciel: {getpwuid(file_stats.st_uid).pw_name}\n'
            text += f'Uprawnienia: {stat.filemode(file_stats.st_mode)}'
            return text
        except:
            return NO_PROPERTIES_AVAILABLE

    def __get_formated_modified_date(self, path):
        timestamp = os.path.getmtime(path)
        date_time = datetime.fromtimestamp(timestamp)
        return date_time.strftime("%d.%m.%Y %H:%M")

    def get_new_tree_view(self, path='/'):
        self.fileSystemtree_store = self.get_new_tree_model(path)

        self.fileSystemTreeView = Gtk.TreeView(self.fileSystemtree_store)
        self.fileSystemTreeView.set_activate_on_single_click(True)
  
        # Name column
        treeViewCol = Gtk.TreeViewColumn("Nazwa")
        colCellText = Gtk.CellRendererText()
        treeViewCol.pack_start(colCellText, True)
        treeViewCol.add_attribute(colCellText, "text", 0)
        treeViewCol.set_sort_column_id(0)
        treeViewCol.set_sort_indicator(True)
        self.fileSystemTreeView.append_column(treeViewCol)

        # size column
        treeViewCol = Gtk.TreeViewColumn("Rozmiar")
        colCellText = Gtk.CellRendererText()
        treeViewCol.pack_start(colCellText, True)
        treeViewCol.add_attribute(colCellText, "text", 2)
        treeViewCol.set_sort_column_id(4)
        treeViewCol.set_sort_indicator(True)
        self.fileSystemTreeView.append_column(treeViewCol)

        # last modified column
        treeViewCol = Gtk.TreeViewColumn("Data edycji")
        colCellText = Gtk.CellRendererText()
        treeViewCol.pack_start(colCellText, True)
        treeViewCol.add_attribute(colCellText, "text", 3)
        treeViewCol.set_sort_column_id(5)
        treeViewCol.set_sort_indicator(True)
        self.fileSystemTreeView.append_column(treeViewCol)

        self.fileSystemTreeView.connect("row-expanded", self.__on_row_expanded)
        self.fileSystemTreeView.connect("row-collapsed", self.__on_row_collapsed)
        self.fileSystemTreeView.connect("row-activated", self.__on_row_selected)
        self.fileSystemTreeView.connect("button_press_event", self.__on_right_click)

        return self.fileSystemTreeView

    def get_new_tree_model(self, path):
        self.__path = path
        # Displayed name, full path, size, date of last edit date, size in bytes, timestamp
        # The last two columns are just for sorting purposes
        self.fileSystemtree_store = Gtk.TreeStore(str, str, str, str, int, int)

        self.__populate_file_system_tree(self.fileSystemtree_store, path)

        return self.fileSystemtree_store

class MenuWindow(Gtk.Window):
    __MENU_BAR = """
        <ui>
        <menubar name='MenuBar'>
            <menu action='FileMenu'>
            <menuitem action='FileOpenFolder' />
            <separator />
            </menu>
            <menu action='HelpMenu'>
            <menuitem action='HelpMenuTutorial' />
            </menu>
            <menu action='AboutMenu'>
            <menuitem action='AboutMenuAuthor' />
            </menu>
        </menubar>
        </ui>
    """

    def __init__(self):
        super(MenuWindow, self).__init__()

        self.set_title("Eksplorator plików")
        self.set_default_size(1000, 600)

        action_group = Gtk.ActionGroup("my_actions")

        self.__add_file_menu_actions(action_group)
        self.__add_edit_menu_actions(action_group)
        self.__add_choices_menu_actions(action_group)

        uimanager = self.__create_ui_manager()
        uimanager.insert_action_group(action_group)

        menubar = uimanager.get_widget("/MenuBar")
        self.__set_layout(menubar)
        
    def __set_layout(self, menubar):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(menubar, False, False, 0)

        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text('')

        scrolled_window_for_text = Gtk.ScrolledWindow()
        scrolled_window_for_text.set_border_width(10)
        scrolled_window_for_text.add(self.textview)

        self.tree = FilesTree(self.textbuffer, self)
        self.treeView = self.tree.get_new_tree_view()

        scrolled_window_for_tree = Gtk.ScrolledWindow()
        scrolled_window_for_tree.set_border_width(10)
        scrolled_window_for_tree.add(self.treeView)

        horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        horizontal_box.pack_start(scrolled_window_for_tree, True, True, 0)
        horizontal_box.pack_start(scrolled_window_for_text, True, True, 0)

        box.pack_start(horizontal_box, True, True, 0)

        self.add(box)

    def __add_file_menu_actions(self, action_group):
        action_group.add_actions(
            [
                ("FileMenu", None, "Folder"),
                ("FileOpenFolder", Gtk.STOCK_OPEN, "Otwórz", None, None, self.__on_menu_openFolder),
            ]
        )

    def __add_edit_menu_actions(self, action_group):
        action_group.add_actions(
            [
                ("HelpMenu", None, "Pomoc"),
                ("HelpMenuTutorial", Gtk.STOCK_HELP, "Otwórz przewodnik", "<control>H", None, self.__on_menu_tutorial),
            ]
        )

    def __add_choices_menu_actions(self, action_group):
        action_group.add_actions(
            [
                ("AboutMenu", None, "O autorze"),
                ("AboutMenuAuthor", Gtk.STOCK_ABOUT, "Informacje o autorze", "<control>I", None, self.__on_menu_author_info),
            ]
        )

    def __create_ui_manager(self):
        uimanager = Gtk.UIManager()

        uimanager.add_ui_from_string(MenuWindow.__MENU_BAR)

        accelgroup = uimanager.get_accel_group()
        self.add_accel_group(accelgroup)
        return uimanager

    def __on_menu_openFolder(self, widget):
        dialog = Gtk.FileChooserDialog(
            "Wybierz folder",
            self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            ("Anuluj", Gtk.ResponseType.CANCEL, "Wybierz", Gtk.ResponseType.OK),
        )
        dialog.set_default_size(300, 300)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.treeView.set_model(self.tree.get_new_tree_model(dialog.get_filename()))
        dialog.destroy()

    def __on_menu_tutorial(self, widget):
        show_info_popup(self, "Pomoc", HELP_GUIDE)

    def __on_menu_author_info(self, widget):
        show_info_popup(self, "O autorze", AUTHOR_INFO)


window = MenuWindow()
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
