import sys
import json

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import re
from os import path

from modules.syntax import PythonHighlighter

from modules.db import db
from modules.ui import Ui_MainWindow


def qt_message_handler(mode, context, message):
    if mode == QtCore.QtInfoMsg:
        mode = 'INFO'
    elif mode == QtCore.QtWarningMsg:
        mode = 'WARNING'
    elif mode == QtCore.QtCriticalMsg:
        mode = 'CRITICAL'
    elif mode == QtCore.QtFatalMsg:
        mode = 'FATAL'
    else:
        mode = 'DEBUG'
    print('qt_message_handler: line: %d, func: %s(), file: %s' % (
        context.line, context.function, context.file))
    print('  %s: %s\n' % (mode, message))


qInstallMessageHandler(qt_message_handler)
qDebug('MyApp')


class Form(QMainWindow, Ui_MainWindow):
    @staticmethod
    def show_msg_box(mb_type):
        msg_box = QMessageBox()
        if mb_type == "delete":
            msg_box.setWindowTitle("Delete")
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setText("DELETE the note?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Cancel)
            return msg_box.exec()
        elif mb_type == "save":
            msg_box.setWindowTitle("Save")
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setText("Save changes?")
            msg_box.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Save)
            return msg_box.exec()
        elif mb_type == "tags":
            msg_box.setWindowTitle("Tags")
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setText("No tags in note. Continue?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Cancel)
            return msg_box.exec()
        elif mb_type == "backup":
            msg_box.setWindowTitle("Backup")
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText("Can't make backup of database! Check path in settings.json")
            msg_box.setStandardButtons(QMessageBox.Ok)
            return msg_box.exec()

    def ask_to_save(self):
        if self.btn_new_save.text() == "Save" and self.btn_new_save.isEnabled():
            btn = self.show_msg_box("save")
            if btn == QMessageBox.Save:
                self.btn_new_save_clicked()
            elif btn == QMessageBox.Cancel:
                return

    def set_mode(self, mode):
        self.lb_count.setText(f"Total notes: {str(db.get_notes_count())}")
        if "search" in mode:
            self.ask_to_save()
            self.mode = "search"
            self.st_widget.setCurrentIndex(1)
            self.setWindowTitle("Notes: search")
            if mode == "search_title":
                self.txt_title.setText(self.search)
                self.tr_search.setFocus()
            else:
                self.tags = []
                self.txt_title.setText("")
                self.txt_title.setFocus()
            self.btn_new_save.setText("New")
            self.btn_new_save.setEnabled(True)
            self.update_tag_checkboxes()
            self.update_search()
            self.statusbar.showMessage("New note |Ctrl-N, Ctrl-Enter|     Open note |Enter|")
        else:
            if "new" in mode:
                self.mode = "new"
                self.st_widget.setCurrentIndex(0)
                self.setWindowTitle("Notes: new")
                if mode == "new_title":
                    self.txt_main.setFocus()
                else:
                    self.tags = []
                    self.txt_title.setText("")
                    self.txt_title.setFocus()
                self.txt_main.setPlainText('\n' + '-' * 50 + '\n')
                # cursor = QTextCursor(self.txt_main.document())
                # cursor.insertHtml("<a href=\"http://www.google.com\" >Google</a>")
                self.btn_new_save.setText("Save")
                self.btn_new_save.setEnabled(False)
                self.update_tag_checkboxes()
                self.statusbar.showMessage("Save note |Ctrl-S|     Return to search |Ctrl-F, Escape|")
            elif "edit" in mode:
                self.mode = "edit"
                self.st_widget.setCurrentIndex(0)
                self.setWindowTitle("Notes: edit")
                self.btn_new_save.setText("New")
                self.btn_new_save.setEnabled(True)
                self.txt_main.setFocus()
                self.statusbar.showMessage(
                    "New note |Ctrl-N|     Save note |Ctrl-S|     Return to search |Ctrl-F, Escape|")

    def update_search(self):
        self.search_data.clear()
        if not len(self.title):
            search = db.get_all_notes(self.tags)
        else:
            search = db.fts_note(self.title, self.tags)
        if search:
            all_tags = db.get_all_tags()
            for note_id, note_title, note_body in search:
                note_tags = db.get_note_tags(note_id)
                if note_tags and all_tags:
                    note_tags = [tag for tag in reversed(all_tags) if tag in note_tags]  # sort note tags by count
                    title = QStandardItem(note_title + ' #' + ' #'.join(note_tags))
                else:
                    title = QStandardItem(note_title)
                title.setData(note_id, Qt.UserRole + 1)  # id
                title.setData("title", Qt.UserRole + 2)  # id
                # title.setEditable(False)
                body = QStandardItem(note_body)
                body.setData(note_id, Qt.UserRole + 1)  # id
                body.setData("body", Qt.UserRole + 2)  # id
                title.appendRow(body)
                self.search_data.appendRow(title)

    def update_btn_new_save(self):
        if self.mode == "new":
            self.btn_new_save.setEnabled(True if self.title else False)
        elif self.mode == "edit":
            note = db.get_note(self.cur_note_id)
            if not note:
                return
            note_id, note_title, note_body = note
            note_tags = db.get_note_tags(self.cur_note_id)
            if not note_tags:
                note_tags = []
            if all((note_id, note_title, note_body)) and (self.title != note_title or
                                                          self.body != note_body or
                                                          sorted(self.tags) != sorted(note_tags)):
                self.btn_new_save.setText("Save")
            else:
                self.btn_new_save.setText("New")

    def update_tag_checkboxes(self):
        for i in range(self.tags_layout.count()):
            cb_tag = self.tags_layout.itemAt(i).widget()
            cb_tag.setChecked(True if cb_tag.text()[1:] in self.tags else False)

    def draw_tag_checkboxes(self):
        for i in reversed(range(self.tags_layout.count())):
            self.tags_layout.itemAt(i).widget().setParent(None)
        all_tags = db.get_all_tags()
        if all_tags:
            for i, tag in enumerate(all_tags):
                cb_tag = QCheckBox(self.grp_tags)
                cb_tag.setText(f"#{tag}")
                cb_tag.setObjectName(f"cb_tag{i + 1}")
                cb_tag.setFocusPolicy(Qt.NoFocus)
                cb_tag.clicked.connect(self.cb_clicked)
                self.tags_layout.addWidget(cb_tag)
            self.update_tag_checkboxes()

    def key_pressed(self, func):
        def f(*args):
            key = args[0].key()
            modifiers = args[0].modifiers()
            #  global
            if self.btn_new_save.isEnabled() and (
                    # ctrl-s
                    (key == Qt.Key_S and (modifiers & Qt.ControlModifier) and self.btn_new_save.text() == "Save") or
                    # ctrl-n
                    (key == Qt.Key_N and (modifiers & Qt.ControlModifier) and self.btn_new_save.text() == "New")):
                self.btn_new_save_clicked()
            elif key == Qt.Key_Escape:
                if self.mode == 'search':
                    self.txt_title.setText("")
                else:
                    self.set_mode("search_title")
            elif self.btn_search.isEnabled() and key == Qt.Key_F \
                    and (modifiers & Qt.ControlModifier):
                self.btn_search_clicked()
            # txt_title
            elif self.txt_title.hasFocus():
                if key in (Qt.Key_Enter, Qt.Key_Return) and (modifiers & Qt.ControlModifier):
                    self.set_mode("new_title")
                elif key == Qt.Key_Down or key in (Qt.Key_Enter, Qt.Key_Return):
                    if self.mode == "search" and self.search_data.rowCount():
                        self.tr_search.setCurrentIndex(self.search_data.index(0, 0))
                        self.tr_search.setFocus()
                    elif self.mode != "search":
                        self.txt_main.setFocus()
            # txt_main
            elif self.txt_main.hasFocus() and key == Qt.Key_Up and (modifiers & Qt.ControlModifier):
                self.txt_title.setFocus()
            # tr_search
            elif self.tr_search.hasFocus():
                if key in (Qt.Key_Enter, Qt.Key_Return):
                    self.tr_double_clicked(self.tr_search.currentIndex())
                elif self.tr_search.currentIndex() == self.search_data.index(0, 0) \
                        and key == Qt.Key_Up:
                    self.txt_title.setFocus()
                elif key == Qt.Key_Delete:
                    item = self.tr_search.currentIndex()
                    note_type = item.data(Qt.UserRole + 2)
                    if note_type == "title":
                        if key == Qt.Key_Delete and self.show_msg_box("delete") == QMessageBox.Yes:
                            db.delete_note(item.data(Qt.UserRole + 1))
                            self.draw_tag_checkboxes()
                            self.update_search()
            func(*args)

        return f

    @staticmethod
    def tr_item_changed(item):
        item_id = item.data(Qt.UserRole + 1)
        item_type = item.data(Qt.UserRole + 2)
        item_text = item.text()
        if item_type == "title":
            db.update_note_title(item_id, item_text)
        elif item_type == "body":
            db.update_note_body(item_id, item_text)

    def txt_title_text_changed(self, txt):
        self.title = txt
        self.tags = [tag for tag in re.findall("#(\\w+)", self.title)]
        self.update_tag_checkboxes()
        self.tags = sorted(self.tags, key=lambda x: len(x), reverse=True)
        for tag in self.tags:
            self.title = self.title.replace('#' + tag, '')
        self.title = self.title.strip()
        if self.mode == "search":
            self.update_search()
        else:
            self.update_btn_new_save()

    def txt_main_text_changed(self):
        self.body = self.txt_main.toPlainText()
        if self.mode != "search":
            self.update_btn_new_save()

    def btn_new_save_clicked(self):
        if self.btn_new_save.text() == "New":
            self.set_mode("new")
        elif self.btn_new_save.text() == "Save":
            # if not self.tags and self.show_msg_box("tags") == Qt.Key_Cancel:
            #     return
            if self.mode == "new":
                self.cur_note_id = db.insert_note(self.title, self.body)
                self.btn_new_save.setText("New")
            elif self.cur_note_id:
                db.update_note(self.cur_note_id, self.title, self.body)
                self.btn_new_save.setText("New")
            db.set_note_tags(self.cur_note_id, self.tags)
            self.draw_tag_checkboxes()

    def btn_search_clicked(self):
        self.set_mode("search")

    def cb_clicked(self, checked):
        tag = self.sender().text()
        if not tag:
            return
        txt = self.txt_title.text()
        if checked and tag not in txt:
            self.txt_title.setText(txt + f" {tag}")
        elif not checked and tag in txt:
            self.txt_title.setText(txt.replace(' ' + tag, ""))
        if self.mode == "search":
            self.update_search()
        else:
            self.update_btn_new_save()

    def tr_clicked(self, index):
        if self.tr_search.isExpanded(index):
            self.tr_search.setExpanded(index, False)
        else:
            self.tr_search.setExpanded(index, True)
        print(index.data(Qt.UserRole + 1))

    def tr_double_clicked(self, index):
        self.cur_note_id = index.data(Qt.UserRole + 1)
        self.search = self.txt_title.text()
        note = db.get_note(self.cur_note_id)
        if not note:
            return
        note_id, note_title, note_body = note
        note_tags = db.get_note_tags(self.cur_note_id)
        if all((note_id, note_title, note_body)):
            self.txt_title.setText(note_title + (' #' + ' #'.join(note_tags) if note_tags else ""))
            self.hl.active = "python" in note_tags
            self.txt_main.setPlainText(note_body)
            self.tags = list(note_tags) if note_tags else []
            self.update_tag_checkboxes()
            self.set_mode("edit")

    def __init__(self):
        # UI init
        super().__init__()
        self.setupUi(self)
        with open("settings.json") as file:
            try:
                settings = json.load(file)
                if "main_window" in settings:
                    if "width" in settings["main_window"] and "height" in settings["main_window"]:
                        self.resize(settings["main_window"]["width"], settings["main_window"]["height"])
            except Exception as e:
                print("JSON", e)
        # local vars
        self.title = ""
        self.body = ""
        self.search = ""
        self.tags = []
        self.mode = "search"
        self.cur_note_id = None
        # widgets init
        self.hl = PythonHighlighter(self.txt_main.document())
        metrics = QFontMetrics(self.txt_main.font())
        self.txt_main.setTabStopWidth(4 * metrics.width(' '))
        self.txt_main.setTextInteractionFlags(self.txt_main.textInteractionFlags() | Qt.LinksAccessibleByMouse)
        self.search_data = QStandardItemModel()
        self.tr_search.setModel(self.search_data)
        self.tr_search.setHeaderHidden(True)
        self.st_widget.setCurrentIndex(1)
        self.lb_count = QLabel()
        self.statusbar.addPermanentWidget(self.lb_count)
        # events
        # self.tr_search.clicked.connect(self.tr_clicked)
        self.tr_search.doubleClicked.connect(self.tr_double_clicked)
        self.search_data.itemChanged.connect(self.tr_item_changed)

        self.tags_layout.setAlignment(Qt.AlignTop)
        self.btn_new_save.clicked.connect(self.btn_new_save_clicked)
        self.btn_search.clicked.connect(self.btn_search_clicked)
        self.txt_title.textChanged.connect(self.txt_title_text_changed)
        # self.txt_title.btnClicked.connect(self.btn_history_click)
        # self.txt_title.selected.connect(self.srch_selected)
        self.txt_main.textChanged.connect(self.txt_main_text_changed)
        # self.txt_main.resize.connect(self.resize)
        # keypresses
        self.tr_search.keyPressEvent = self.key_pressed(self.tr_search.keyPressEvent)
        self.txt_title.keyPressEvent = self.key_pressed(self.txt_title.keyPressEvent)
        self.txt_main.keyPressEvent = self.key_pressed(self.txt_main.keyPressEvent)

        self.set_mode("search")
        self.draw_tag_checkboxes()
        self.update_search()

    def closeEvent(self, *args, **kwargs):
        self.ask_to_save()
        settings = {"main_window": {}}
        try:
            settings = json.load(open("settings.json"))
        except Exception as e:
            print("JSON", e)
        settings["main_window"]["width"] = self.width()
        settings["main_window"]["height"] = self.height()
        try:
            json.dump(settings, open("settings.json", 'w'))
        except Exception as e:
            print("JSON", e)
        if "backup" in settings and "backup_path" in settings["backup"]:
            if not db.make_backup(settings["backup"]["backup_path"]):
                print("Failed to make database backup!")

    # def __del__(self):


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(path.join("icons", "notebook.svg")))
    form = Form()
    form.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
