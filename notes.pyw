import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from os import path
import time
import configparser


from modules.db import db
from modules.ui import Ui_MainWindow
from modules.md import Md
from modules.signals import Signals


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
        if self.btn_new_save.text() == "Save" and self.btn_new_save.isEnabled():
            btn = self.show_msg_box("save")
            if btn == QMessageBox.Save:
                self.btn_new_save_clicked()
                return 'save'
            elif btn == QMessageBox.Cancel:
                return 'cancel'
            else:
                return 'discard'

    def set_mode(self, mode):
        self.lb_count.setText(f"Last backup: {self.last_backup} Total notes: {str(db.get_notes_count())}")
        if "search" in mode:
            if self.ask_to_save() == 'cancel':
                return
            self.mode = "search"
            self.st_widget.setCurrentIndex(1)
            self.setWindowTitle("Notes: search")
            self.txt_title.setEnabled(True)
            if mode == "search_title":
                self.txt_title.setText(self.search)
                self.tr_search.setFocus()
            else:
                self.tags = []
                self.txt_title.setText("")
                self.txt_title.setFocus()
            self.btn_new_save.setText("New")
            self.btn_new_save.setEnabled(True)
            self.draw_tag_checkboxes()
            self.update_search()
            self.statusbar.showMessage("New note |Ctrl-N, Ctrl-Enter|     Open note |Enter|")
        else:
            note = db.get_note(self.cur_note_id)
            note_id, note_title, note_body = note if note and len(note) == 3 else (None, None, None)
            note_tags = db.get_note_tags(self.cur_note_id)
            self.tags = list(note_tags) if note_tags else []
            if "new" in mode:
                self.mode = "new"
                self.st_widget.setCurrentIndex(0)
                self.setWindowTitle("Notes: new")
                self.txt_title.setEnabled(True)
                if mode == "new_title":
                    self.txt_main.setFocus()
                else:
                    self.tags = []
                    self.txt_title.setText("")
                    self.txt_title.setFocus()
                text = ""
                if "python" in self.tags:
                    text += "```python\n\n```"
                if "linux" in self.tags:
                    text = "```bash\n\n```"
                self.txt_main.setPlainText(text + '\n' + '*' * 3 + '\n')
                self.btn_new_save.setText("Save")
                self.btn_new_save.setEnabled(True)
                self.statusbar.showMessage("Save note |Ctrl-S|     Return to search |Ctrl-F, Escape|")
            elif "edit" in mode:
                self.mode = "edit"
                self.st_widget.setCurrentIndex(0)
                self.setWindowTitle("Notes: edit")
                self.txt_title.setEnabled(True)
                self.btn_new_save.setText("New")
                self.btn_new_save.setEnabled(False)
                if all((note_id, note_title, note_body)):
                    self.txt_title.setText(note_title + (' #' + ' #'.join(note_tags) if note_tags else ""))
                    self.txt_main.setPlainText(note_body)
                    if note_tags:
                        self.tags = list(note_tags) if note_tags else []
                self.txt_main.setFocus()
                self.statusbar.showMessage(
                    "New note |Ctrl-N|     Save note |Ctrl-S|     Replace |Ctrl-H|     Return to search |Ctrl-F, Escape|")
            elif "view" in mode:
                self.mode = "view"
                self.st_widget.setCurrentIndex(2)
                self.setWindowTitle("Notes: view")
                self.txt_title.setEnabled(False)
                self.btn_new_save.setText("New")
                self.btn_new_save.setEnabled(True)
                if all((note_id, note_title, note_body)):
                    self.txt_title.setText(note_title + (' #' + ' #'.join(note_tags) if note_tags else ""))
                    self.web_view.setHtml(self.markdown.render_html(f"## {self.txt_title.text()}\n***\n{note_body}"))
                self.statusbar.showMessage(
                    "New note |Ctrl-N|     Edit note |Ctrl-E, Enter|     Return to search |Ctrl-F, Escape|")
                self.web_view.setFocus()
            self.draw_tag_checkboxes(False if mode is "view" else True)

    def update_search(self):
        self.search_data.clear()
        if not len(self.title):
            search = db.get_all_notes(self.tags)
        else:
            search = db.fts_note(self.title, self.tags)
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

            self.btn_new_save.setEnabled(True)

    def draw_tag_checkboxes(self, enabled=True):
        for i in reversed(range(self.tags_layout.count())):
            self.tags_layout.itemAt(i).widget().setParent(None)
        self.all_tags = db.get_all_tags()
        if self.all_tags:
            for i, tag in enumerate(self.all_tags):
                cb_tag = QCheckBox(self.grp_tags)
                cb_tag.setText(f"#{tag}")
                cb_tag.setObjectName(f"cb_tag{i + 1}")
                cb_tag.setFocusPolicy(Qt.NoFocus)
                cb_tag.setEnabled(enabled)
                cb_tag.setChecked(True if tag in self.tags else False)
                cb_tag.clicked.connect(self.cb_clicked)
                self.tags_layout.addWidget(cb_tag)

    def __init__(self):
        # UI init
        super().__init__()
        self.setupUi(self)
        self.dir = path.dirname(__file__)
        self.replace_dlg = ReplaceDialog()

        self.conf = configparser.ConfigParser(allow_no_value=True)
        self.conf.read("notes.ini")
        width = self.conf.getint("SAVED_PARAMS", "WIDTH", fallback=None)
        height = self.conf.getint("SAVED_PARAMS", "HEIGHT", fallback=None)
        if width and height:
            self.resize(width, height)
        self.backup_path = self.conf.get("CUSTOM", "BACKUP_PATH", fallback=self.dir)
        css = self.conf.get("CUSTOM", "CSS", fallback="")
        css = css.split()
        self.markdown = Md(*css)
        self.replace_dlg.cb_match_case.setChecked(self.conf.getboolean("SAVED_PARAMS", "MATCH_CASE", fallback=False))
        self.replace_dlg.cb_words.setChecked(self.conf.getboolean("SAVED_PARAMS", "WORDS", fallback=False))
        # local vars
        self.title = ""
        self.body = ""
        self.search = ""
        self.tags = []
        self.all_tags = []
        self.mode = "search"
        self.cur_note_id = None
        self.tags_count_prev = 0
        filename = path.join(self.backup_path, db.fname + ".backup")
        if path.exists(filename):
            self.last_backup = time.ctime(path.getmtime(filename))
        else:
            self.last_backup = "---"
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
        self.tags_layout.setAlignment(Qt.AlignTop)
        self.btn_new_save.clicked.connect(self.btn_new_save_clicked)
        self.btn_search.clicked.connect(self.btn_search_clicked)
        self.txt_title.textChanged.connect(self.txt_title_text_changed)
        self.txt_main.textChanged.connect(self.txt_main_text_changed)
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.replace_key)
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
        if self.ask_to_save() == 'cancel':
            event.ignore()
            return
        if "SAVED_PARAMS" not in self.conf:
            self.conf["SAVED_PARAMS"] = {}
        self.conf["SAVED_PARAMS"]["WIDTH"] = str(self.width())
        self.conf["SAVED_PARAMS"]["HEIGHT"] = str(self.height())
        self.conf["SAVED_PARAMS"]["MATCH_CASE"] = str(self.replace_dlg.cb_match_case.isChecked())
        self.conf["SAVED_PARAMS"]["WORDS"] = str(self.replace_dlg.cb_words.isChecked())
        with open("notes.ini", 'w') as file:
            self.conf.write(file)
        if self.backup_path:
            if not db.make_backup(self.backup_path):
                print("Failed to make database backup!")


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(path.join("icons", "notebook.svg")))
    form = Form()
    form.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
