"""
Plik odpowiedzialny za widget zmiany hasła
"""
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QGroupBox, QGridLayout, QLabel, QPushButton, QLineEdit, \
    QSizePolicy, QHBoxLayout, QMessageBox

from baza import polaczenie


class Password(QWidget):
    """
    Klasa odpowiedzialna za widget Zmiany hasła
    """

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent

        # Ustawianie Layoutu wigdetu
        self.txt_h_nowe2 = QLineEdit()
        self.txt_h_nowe1 = QLineEdit()
        self.txt_h_stare = QLineEdit()
        self.btn_h_zmien = QPushButton('Zmień')
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.initUI()

    def initUI(self):
        """
        Inicjuje UI
        """
        # Ustawianie layoutu groupboxa
        grid = QGridLayout()
        group_box = QGroupBox("Zmiana hasła")
        group_box.setLayout(grid)

        lblhaslo1 = QLabel('Stare hasło:')
        lblhaslo2 = QLabel('Nowe hasło:')
        lblhaslo3 = QLabel('Powtórz hasło:')

        # Wyłączenie przycisku i ustawienie sprawdzania
        self.btn_h_zmien.setDisabled(True)
        self.txt_h_stare.textChanged[str].connect(self.empty)
        self.txt_h_nowe1.textChanged[str].connect(self.empty)
        self.txt_h_nowe2.textChanged[str].connect(self.empty)
        self.btn_h_zmien.clicked.connect(self.accept)

        grid.addWidget(lblhaslo1, 0, 0)
        grid.addWidget(lblhaslo2, 1, 0)
        grid.addWidget(lblhaslo3, 2, 0)
        grid.addWidget(self.txt_h_stare, 0, 1)
        grid.addWidget(self.txt_h_nowe1, 1, 1)
        grid.addWidget(self.txt_h_nowe2, 2, 1)
        grid.addWidget(self.btn_h_zmien, 3, 1)

        group_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.layout.addWidget(group_box)
        self.show()

    def empty(self):
        """
        W momencie, gdy wszystkie pola tekstowe są wpisane, włącza przycisk.
        Sprawdza wypełnienie pól formularza zmiany hasła
        """
        if self.txt_h_nowe1.text() and \
                self.txt_h_nowe2.text() and \
                self.txt_h_stare.text() and \
                self.txt_h_nowe1.text() == self.txt_h_nowe2.text():
            self.btn_h_zmien.setEnabled(True)
        else:
            self.btn_h_zmien.setDisabled(True)

    def accept(self):
        """
        Metoda odpowiedzialna za zmianę hasła
        """
        query = 'UPDATE uzytkownik SET haslo = sha(%s) WHERE uzytkownik_id = %s AND haslo = sha(%s);'
        prevent = (self.txt_h_nowe1.text(), self.parent.parent.user_id, self.txt_h_stare.text())
        try:
            if polaczenie(query, prevent) != 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Hasło zostało zmienione")
                msg.setWindowTitle("Zmiana hasła")
                msg.exec_()
                self.txt_h_nowe1.setText('')
                self.txt_h_nowe2.setText('')
                self.txt_h_stare.setText('')
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Podane hasło jest niepoprawne")
                msg.setWindowTitle("Błędne hasło")
                msg.exec_()
        except BaseException as err:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Wystąpił błąd. Szczegóły poniżej")
            msg.setDetailedText(err)
            msg.setWindowTitle("Błąd!")
            msg.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Program = QWidget()
    ex = Password(Program)
    Program.show()
    sys.exit(app.exec_())
