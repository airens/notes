from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import re

from modules.db import db


class Signals:
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
                elif self.mode == 'edit':
                    self.set_mode("view")
                else:
                    self.set_mode("search_title")
            elif self.btn_search.isEnabled() and key == Qt.Key_F \
                    and (modifiers & Qt.ControlModifier):
                self.btn_search_clicked()
            elif self.mode == "view":
                if key in (Qt.Key_Enter, Qt.Key_Return) or key == Qt.Key_E and (modifiers & Qt.ControlModifier):
                    self.set_mode("edit")
            # txt_title
            elif self.txt_title.hasFocus():
                if key in (Qt.Key_Enter, Qt.Key_Return) and (modifiers & Qt.ControlModifier):
                    self.set_mode("new_title")
                elif key == Qt.Key_Down:
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
        self.draw_tag_checkboxes()
        # self.tags = sorted(self.tags, key=lambda x: len(x), reverse=True)
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
            if self.mode == "new":  # makin' new note
                self.cur_note_id = db.insert_note(self.title, self.body)
                db.set_note_tags(self.cur_note_id, self.tags)
                self.set_mode("edit")
            elif self.cur_note_id:  # edited existed note
                db.update_note(self.cur_note_id, self.title, self.body)
                db.set_note_tags(self.cur_note_id, self.tags)
                self.set_mode("view")


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

    def tr_double_clicked(self, index):
        self.cur_note_id = index.data(Qt.UserRole + 1)
        self.search = self.txt_title.text()
        self.set_mode("view")

    def tb_view_menu_requested(self, pt):
        menu = QMenu(self)
        action_edit = QAction("Edit note")
        action_edit.triggered.connect(self.tb_action_edit_triggered)
        menu.addAction(action_edit)
        menu.exec(self.web_view.mapToGlobal(pt))

    def tb_action_edit_triggered(self):
        self.set_mode("edit")
