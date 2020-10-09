import sys
import logging
import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from os import path
import time
import json
import jsons

from modules.db import db
from modules.ui import Ui_MainWindow
from modules.md import Md
from modules.signals import Signals


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(f"{os.path.basename(__file__).partition('.')[0]}.log"),
        logging.StreamHandler()  # console
    ])


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


class ReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.lbl_from = QLabel(self, text="Replace")
        self.txt_from = QLineEdit(self)
        self.lbl_to = QLabel(self, text="With")
        self.txt_to = QLineEdit(self)
        h_layout = QHBoxLayout()
        self.cb_match_case = QCheckBox(self, text="Match &case")
        shortcut = QShortcut(QKeySequence("Alt+C"), self)
        shortcut.activated.connect(self.cb_match_case.click)
        self.cb_words = QCheckBox(self, text="W&ords")
        shortcut = QShortcut(QKeySequence("Alt+O"), self)
        shortcut.activated.connect(self.cb_words.click)
        layout.addWidget(self.lbl_from)
        layout.addWidget(self.txt_from)
        layout.addWidget(self.lbl_to)
        layout.addWidget(self.txt_to)
        h_layout.addWidget(self.cb_match_case)
        h_layout.addWidget(self.cb_words)
        layout.addLayout(h_layout)
        # OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setWindowTitle("Replace")

    def exec(self):
        result = self.exec_()
        return result, self.txt_from.text(), self.txt_to.text(), \
               self.cb_match_case.isChecked(), self.cb_words.isChecked()


class Form(QMainWindow, Ui_MainWindow, Signals):
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
            msg_box.setText("Can't make backup of database! Check path in settings")
            msg_box.setStandardButtons(QMessageBox.Ok)
            return msg_box.exec()

    def ask_to_save(self):
        if self.save_enabled:
            btn = self.show_msg_box("save")
            if btn == QMessageBox.Save:
                self.save()
                self.save_enabled = False
                return 'save'
            elif btn == QMessageBox.Cancel:
                return 'cancel'
            else:
                self.save_enabled = False
                return 'discard'

    def set_mode(self, mode):
        if mode == self.mode:
            return
        self.lb_count.setText(f"    Last backup: {self.last_backup} Total notes: {str(db.get_notes_count())}")
        self.logger.debug(f"Setting mode to {mode}..")
        if self.ask_to_save() == 'cancel':
            self.logger.debug("\tcanceled because of Save msg box")
            return
        if "search" in mode:
            self.mode = "search"
            self.st_widget.setCurrentIndex(1)
            self.setWindowTitle("Notes: search")
            self.txt_title.setEnabled(True)
            if mode == "search_title":
                self.txt_title.setText(self.search)
                self.tr_search.setFocus()
            else:
                self.txt_title.setText("")
                self.txt_title.setFocus()
            self.draw_tag_checkboxes()
            self.update_search()
        else:
            note = db.get_note(self.cur_note_id)
            note_id, note_title, note_body = note if note and len(note) == 3 else (None, None, None)
            note_tags = db.get_note_tags(self.cur_note_id)
            if "new" in mode:
                self.mode = "new"
                self.st_widget.setCurrentIndex(0)
                self.setWindowTitle("Notes: new")
                self.txt_title.setEnabled(True)
                self.txt_main.setPlainText("")
                if mode == "new_title":
                    self.txt_main.setFocus()
                else:
                    self.tags = []
                    self.txt_title.setText("")
                    self.txt_title.setFocus()
            elif "edit" in mode:
                self.mode = "edit"
                self.st_widget.setCurrentIndex(0)
                self.setWindowTitle("Notes: edit")
                self.txt_title.setEnabled(True)
                if all((note_id, note_title, note_body)):
                    self.txt_title.setText(note_title + (' #' + ' #'.join(note_tags) if note_tags else ""))
                    self.txt_main.setPlainText(note_body)
                    if note_tags:
                        self.tags = list(note_tags) if note_tags else []
                self.txt_main.setFocus()
            elif "view" in mode:
                self.mode = "view"
                self.st_widget.setCurrentIndex(2)
                self.setWindowTitle("Notes: view")
                self.txt_title.setEnabled(False)
                if all((note_id, note_title, note_body)):
                    self.txt_title.setText(note_title + (' #' + ' #'.join(note_tags) if note_tags else ""))
                    self.web_view.setHtml(self.markdown.render_html(f"## {self.txt_title.text()}\n***\n{note_body}"))
                self.web_view.setFocus()
            self.draw_tag_checkboxes(False if mode == "view" else True)
        self.save_enabled = False
        message = ""
        for name, key_seq, modes_allowed in self.settings.shortcuts:
            if any(shortcut_mode in mode for shortcut_mode in modes_allowed):
                message += f"{name} ({key_seq})    "
        self.statusbar.showMessage(message)
        self.logger.debug("\tdone")

    def update_search(self):
        self.search_data.clear()
        if not len(self.title):
            search = db.get_all_notes(self.tags)
        else:
            search = db.fts_note(''.join([i for i in self.txt_title.text() if i.isalnum() or i.isspace()]), self.tags)
        if search:
            for note_id, note_title, note_body in search:
                note_tags = db.get_note_tags(note_id)
                if note_tags and self.all_tags:
                    note_tags = [tag for tag in reversed(self.all_tags) if tag in note_tags]  # sort note tags by count
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

    def update_save_enabled(self):
        if self.mode == "new":
            self.save_enabled = True
        if self.mode == "edit":
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
                self.save_enabled = True
            else:
                self.save_enabled = False
        self.save_enabled = self.save_enabled if self.title and self.body else False

    def draw_tag_checkboxes(self, enabled=True):
        for i in reversed(range(self.v_layout_cb.count())):
            self.v_layout_cb.itemAt(i).widget().setParent(None)
        self.all_tags = db.get_all_tags()
        if self.all_tags:
            for i, tag in enumerate(self.all_tags):
                cb_tag = QCheckBox(self)
                cb_tag.setText(f"#{tag}")
                cb_tag.setObjectName(f"cb_tag{i + 1}")
                cb_tag.setFocusPolicy(Qt.NoFocus)
                cb_tag.setEnabled(enabled)
                cb_tag.setChecked(True if tag in self.tags else False)
                cb_tag.clicked.connect(self.cb_clicked)
                self.v_layout_cb.addWidget(cb_tag)

    def save(self):
        if self.mode == "new":  # makin' new note
            self.cur_note_id = db.insert_note(self.title, self.body)
        elif self.cur_note_id:  # edited existed note
            db.update_note(self.cur_note_id, self.title, self.body)
        db.set_note_tags(self.cur_note_id, self.tags)
        self.save_enabled = False
        self.set_mode("view")
        self.logger.debug(f"Note {self.title} saved.")

    class Settings:
        def __init__(self, **kwargs):
            self.css = kwargs.get("css", [
                "mini-nord.base.css",
                "manni.css",
                "global.css"])
            self.backup_path = kwargs.get("backup_path")
            self.shortcuts = kwargs.get("shortcuts", [])
            self.init_width = kwargs.get("init_width")
            self.init_height = kwargs.get("init_height")
            self.replace_match_case = kwargs.get("replace_match_case", False)
            self.replace_words = kwargs.get("replace_words", False)

    def __init__(self):
        self.logger = logging.getLogger()
        # UI init
        super().__init__()
        self.setupUi(self)
        self.dir = path.dirname(__file__)
        self.replace_dlg = ReplaceDialog()
        with open("settings.json") as file:
            self.settings = jsons.loads(file.read(), self.Settings)
            self.logger.info("Settings loaded")
        if self.settings.init_width and self.settings.init_height:
            self.resize(self.settings.init_width, self.settings.init_height)
        css = self.settings.css
        self.markdown = Md(*css)
        self.replace_dlg.cb_match_case.setChecked(self.settings.replace_match_case)
        self.replace_dlg.cb_words.setChecked(self.settings.replace_words)
        # local vars
        self.title = ""
        self.body = ""
        self.search = ""
        self.tags = []
        self.all_tags = []
        self.mode = None
        self.cur_note_id = None
        self.tags_count_prev = 0
        filename = path.join(self.settings.backup_path, db.fname + ".backup")
        self.logger.info(f"Backup filename is {filename}")
        if path.exists(filename):
            self.last_backup = time.ctime(path.getmtime(filename))
        else:
            self.last_backup = "---"
        self.save_enabled = False
        # widgets init
        sym_width = QFontMetrics(self.txt_main.font()).width(' ')
        self.txt_main.setTabStopWidth(4 * sym_width)
        self.txt_main.setTextInteractionFlags(self.txt_main.textInteractionFlags() | Qt.LinksAccessibleByMouse)
        # self.txt_main.setMinimumWidth(int(self.splitter_width * sym_width + 0.5))
        self.search_data = QStandardItemModel()
        self.tr_search.setModel(self.search_data)
        self.tr_search.setHeaderHidden(True)
        self.st_widget.setCurrentIndex(1)
        self.lb_count = QLabel()
        self.statusbar.addPermanentWidget(self.lb_count)
        self.web_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.web_view.customContextMenuRequested.connect(self.tb_view_menu_requested)
        # events
        self.tr_search.doubleClicked.connect(self.tr_double_clicked)
        self.search_data.itemChanged.connect(self.tr_item_changed)
        self.txt_title.textChanged.connect(self.txt_title_text_changed)
        self.txt_main.textChanged.connect(self.txt_main_text_changed)
        funcs = {"save": self.save_key, "new": self.new_key, "back": self.back_key, "edit": self.edit_key,
                 "search": self.search_key, "replace": self.replace_key}
        cnt = 0
        for name, key_seq, modes_allowed in self.settings.shortcuts:
            if name in funcs:
                QShortcut(QKeySequence(key_seq), self).activated.connect(funcs[name])
                cnt += 1
            else:
                self.logger.warning(f"Don't now such a function {name}!")
        if cnt != len(funcs):
            self.logger.warning("Not all functions were connected to shortcuts!")
        # keypresses
        self.tr_search.keyPressEvent = self.key_pressed(self.tr_search.keyPressEvent)
        self.txt_title.keyPressEvent = self.key_pressed(self.txt_title.keyPressEvent)
        self.txt_main.keyPressEvent = self.key_pressed(self.txt_main.keyPressEvent)
        self.web_view.keyPressEvent = self.key_pressed(self.web_view.keyPressEvent)

        self.set_mode("search")
        self.draw_tag_checkboxes()
        self.update_search()
        self.web_view.setHtml(self.markdown.render_html(""))  # just to initialise

    def closeEvent(self, event):
        self.logger.debug("Closing the app...")
        if self.ask_to_save() == 'cancel':
            event.ignore()
            self.logger.debug("Canceled because of Save dlg")
            return
        self.settings.init_width = self.width()
        self.settings.init_height = self.height()
        self.settings.replace_match_case = self.replace_dlg.cb_match_case.isChecked()
        self.settings.replace_words = self.replace_dlg.cb_words.isChecked()
        with open("settings.json", 'w') as file:
            json.dump(jsons.dump(self.settings), file, indent=4)
            self.logger.info("Saved settings")
        if self.settings.backup_path:
            if not db.make_backup(self.settings.backup_path):
                self.logger.error("Failed to make database backup!")
            else:
                self.logger.info("Built backup")
        self.logger.debug("\tdone")


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(path.join("icons", "notebook.svg")))
    form = Form()
    form.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
