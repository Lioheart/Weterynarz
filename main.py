"""
Aplekacja Weterynarz służąca do rezerwowania wizyt u weterynarza.

Moduł ten zawiera klasę logowania.
"""
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QStyleFactory, QDialogButtonBox, QDialog, QLabel, QLineEdit, QFormLayout, \
    QMessageBox
import threading
import time

from baza import polaczenie
from program import Program


class UI_Logowanie(QDialog):
    """
    Klasa odpowiedzialna za okno logowania
    """

    def __init__(self):
        super().__init__()
        self.txthaslo = QLineEdit()
        self.txtlogin = QLineEdit()
        self.buttonBox = QDialogButtonBox(self)
        self.initUI()

    def initUI(self):
        """
        Inicjalizuje UI
        """
        lbllogin = QLabel('Użytkownik:')
        lblhaslo = QLabel('Hasło:')
        self.txthaslo.setEchoMode(QLineEdit.Password)

        # Do USUNIECIA
        # self.txtlogin.setText('admin')
        # self.txthaslo.setText('123')

        # Ustawienie własnych przycisków
        self.buttonBox.addButton('Zaloguj', QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton('Anuluj', QDialogButtonBox.RejectRole)

        fbox = QFormLayout()
        fbox.addRow(lbllogin, self.txtlogin)
        fbox.addRow(lblhaslo, self.txthaslo)
        fbox.addWidget(self.buttonBox)
        self.setLayout(fbox)

        self.setWindowTitle('Logowanie')
        self.setFixedSize(300, 100)
        self.setWhatsThis('<h3>Pole logowania</h3>')

        self.buttonBox.accepted.connect(self.zaloguj)
        self.buttonBox.rejected.connect(self.anuluj)
        self.show()

    def anuluj(self):
        """
        Metoda Anuluj. Wyłącza aplikację
        """
        sys.exit(app.exec_())

    def zaloguj(self):
        """
        Metoda Zaloguj. Sprawdza, czy dany użytkownik jest w bazie, po czy zwraca jego ID
        :return: ID użytkownika
        """
        login = self.txtlogin.text()
        haslo = self.txthaslo.text()
        query = "SELECT * FROM uzytkownik WHERE uzytkownik_nazwa = '{}' AND haslo = sha('{}');".format(login, haslo)
        odczytanie = polaczenie(query)
        if odczytanie:
            self.accept()
            return odczytanie[0]
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Błędna nazwa użytkownika lub hasło.")
            msg.setWindowTitle("Błąd logowania")
            msg.exec_()

    def closeEvent(self, event):
        """
        Zapisuje rozmiar i położenie okna podczas zamknięcia
        :param event: Zakmnięcie programu
        """
        sys.exit(app.exec_())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    app.setWindowIcon(QIcon('icons/pawprint.png'))

    # self.setWindowIcon(QIcon('icons/pawprint.png'))

    translator = QTranslator()
    translator.load('./resources/qt_pl.qm')
    app.installTranslator(translator)

    ui = UI_Logowanie()
    id_user = ui.exec_()
    if id_user == QtWidgets.QDialog.Accepted:
        main_window = Program(id_user)
    sys.exit(app.exec_())
