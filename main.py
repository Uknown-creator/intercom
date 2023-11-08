import sys
import os

from crypto import hash_password, validate_password
import sqlite3

from PyQt5.QtWidgets import QApplication, QLineEdit
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5 import uic


class LoginForm(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('auth.ui', self)
        self.initUI()

    def initUI(self):
        self.passw.setEchoMode(QLineEdit.Password)
        self.auth_button.clicked.connect(self.login_function)

    def login_function(self):
        try:
            conn = sqlite3.connect('userdata.db')
            cur = conn.cursor()
            creds = cur.execute("""SELECT * FROM users WHERE login = ?""", (self.login.text(),)).fetchall()[0]
            if validate_password(creds[2], self.passw.text()):
                conn.commit()
                conn.close()
                self.main = MainForm()
                self.main.show()
                self.close()
            else:
                self.error_label.setText("Неверный логин или пароль")
        except IndexError as e:
            self.error_label.setText("Неверный логин или пароль")
        except Exception as e:
            self.error_label.setText(f"Неизвестная ошибка: {e}")
            print(e)
        # self.second_form.show()


class RegistrationForm(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('register.ui', self)

        conn = sqlite3.connect('userdata.db')
        cur = conn.cursor()
        cur.execute("""CREATE TABLE "users" (
                    "id"	INTEGER NOT NULL,
                    "login"	TEXT,
                    "password"	TEXT,
                    "role"	INTEGER NOT NULL,
                    "home_num"	INTEGER NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT)
                )""")
        cur.execute("""CREATE TABLE "entrances" (
                    "id"	INTEGER NOT NULL,
                    "date_entry"	TEXT NOT NULL,
                    "date_exit"	TEXT NOT NULL,
                    "home_num" INTEGER NOT NULL
                )""")
        conn.commit()
        conn.close()
        self.initUI()

    def initUI(self):
        self.passw.setEchoMode(QLineEdit.Password)
        self.passw_confirm.setEchoMode(QLineEdit.Password)
        self.reg_button.clicked.connect(self.reg_function)

    def reg_function(self):
        try:
            conn = sqlite3.connect('userdata.db')
            cur = conn.cursor()
            self.error_label.setText('')
            if self.passw.text() == self.passw_confirm.text():
                hash_passw = hash_password(self.passw.text())
                cur.execute("""INSERT INTO users(login, password, role, home_num) VALUES (?, ?, ?, ?)""",
                            (self.login.text(), hash_passw, 1, self.home_num.text()))
                conn.commit()
                self.main = MainForm()
                self.main.show()
                self.close()

                conn.commit()
                conn.close()
            else:
                self.error_label.setText("Ошибка: пароли не совпадают")
        except Exception as e:
            print(e)
            self.error_label.setText("Неизвестная ошибка: ", e)


class MainForm(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.initUI()

    def update_widget(self):
        conn = sqlite3.connect('userdata.db')
        cur = conn.cursor()
        res = cur.execute("""SELECT * FROM entrances""").fetchall()
        self.entries_widget.setColumnCount(4)
        self.entries_widget.setRowCount(0)
        for i, row in enumerate(res):
            self.entries_widget.setRowCount(self.entries_widget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.entries_widget.setItem(i, j, QTableWidgetItem(str(elem)))

    def initUI(self):
        self.update_widget()
        self.debug_button.clicked.connect(self.debug_menu)
        self.update_table.clicked.connect(self.update_widget)

    def debug_menu(self):
        user_id = self.id.text()
        dt_entry = self.entry.dateTime().toString(self.entry.displayFormat())
        dt_exit = self.exit.dateTime().toString(self.exit.displayFormat())
        home_num = self.home_num.text()

        conn = sqlite3.connect('userdata.db')
        cur = conn.cursor()
        cur.execute("""INSERT INTO entrances(id, date_entry, date_exit, home_num) VALUES (?, ?, ?, ?)""",
                    (user_id, dt_entry, dt_exit, home_num))
        conn.commit()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if os.path.isfile(f"{os.getcwd()}/userdata.db"):  # DB located
        ex = LoginForm()
    else:
        ex = RegistrationForm()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
