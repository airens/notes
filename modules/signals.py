from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QTextCursor
import re
from modules.db import db


class Signals:
    def key_pressed(self, func):
        def f(*args):
            key = args[0].key()
            modifiers = args[0].modifiers()
            # txt_title
            if self.txt_title.hasFocus():
                if key in (Qt.Key_Enter, Qt.Key_Return):
                    self.set_mode("new_title")
                elif key == Qt.Key_Down:
                    if self.mode == "search" and self.search_data.rowCount():
                        self.tr_search.setCurrentIndex(self.search_data.index(0, 0))
                        self.tr_search.setFocus()
                    elif self.mode != "search":
                        self.txt_main.setFocus()
            # txt_main
            elif self.txt_main.hasFocus():
                cursor = self.txt_main.textCursor()
                if key == Qt.Key_Up and (modifiers & Qt.ControlModifier):
                    self.txt_title.setFocus()
                elif key in (Qt.Key_Enter, Qt.Key_Return):
                    if not cursor.hasSelection():
                        cursor.movePosition(QTextCursor.StartOfLine,  QTextCursor.KeepAnchor)
                        line = cursor.selectedText()
                        if line:
                            cnt = len(line) - len(line.lstrip())  # define count of whitespace symbols at the beginning
                            line = line + '\n' + line[:cnt] + ('\t' if line[-1] == ':' else '')
                            cursor.insertText(line)
                            return
                elif key == Qt.Key_Tab or key == Qt.Key_Backtab:
                    if cursor.hasSelection():
                        text = ""
                        cnt = 0
                        for line in cursor.selection().toPlainText().split('\n'):
                            if not line:
                                text += '\n'
                            else:
                                if key == Qt.Key_Tab:
                                    text += '\t' + line + '\n'
                                    cnt += 1
                                else:
                                    text += (line[1:] if line[0] == '\t' else line) + '\n'
                                    cnt -= 1
                        if text:
                            text = text[:-1]
                        sel_start = cursor.selectionStart()
                        sel_end = cursor.selectionEnd()
                        cursor.insertText(text)
                        # repair selection
                        cursor.setPosition(sel_start)
                        cursor.setPosition(sel_end + cnt, QTextCursor.KeepAnchor)
                        self.txt_main.setTextCursor(cursor)
                        return  # to cancel regular behaviour for TAB
                elif key == Qt.Key_Home:
                    old_cursor = QTextCursor(cursor)
                    cursor.clearSelection()
                    cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
                    line = cursor.selectedText()
                    if line:
                        cnt = len(line) - len(line.lstrip())  # define count of whitespace symbols at the beginning
                        if cnt:
                            new_pos = cnt if cnt != len(line) else 0
                            old_cursor.setPosition(cursor.position() + new_pos,
                                               QTextCursor.KeepAnchor if modifiers & Qt.ShiftModifier else QTextCursor.MoveAnchor)
                            self.txt_main.setTextCursor(old_cursor)
                            return
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

    def save_key(self):
        self.logger.debug("save_key()")
        if self.save_enabled:
            self.save()

    def new_key(self):
        self.logger.debug("new_key()")
        self.set_mode("new")

    def back_key(self):
        self.logger.debug("back_key()")
        if self.mode == 'search':
            self.txt_title.setText("")
        elif self.mode == 'edit':
            self.set_mode("view")
        else:
            self.set_mode("search_title")

    def edit_key(self):
        self.logger.debug("edit_key()")
        if self.mode == "view":
            self.set_mode("edit")

    def search_key(self):
        self.logger.debug("search_key()")
        self.set_mode("search")

    def replace_key(self):
        self.logger.debug("replace_key()")
        if self.mode == "edit" or self.mode == "new":
            btn, txt_from, txt_to, match_case, words = self.replace_dlg.exec()
            if btn:
                if not self.txt_main.textCursor().hasSelection():
                    self.txt_main.selectAll()
                cursor = self.txt_main.textCursor()
                selection = cursor.selection().toPlainText()
                result = re.sub(txt_from if not words else f"\\b{txt_from}", txt_to, selection,
                                flags=re.IGNORECASE if not match_case else 0)
                cursor.insertText(result)

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
            self.update_save_enabled()

    def txt_main_text_changed(self):
        self.body = self.txt_main.toPlainText()
        if self.mode != "search":
            self.update_save_enabled()

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
            self.update_save_enabled()

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

        def tb_action_edit_triggered():
            self.set_mode("edit")
        action_edit.triggered.connect(tb_action_edit_triggered)
        menu.addAction(action_edit)
        menu.exec(self.web_view.mapToGlobal(pt))
