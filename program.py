"""
Wyświetla główne okno programu
"""
import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QWidget, QVBoxLayout, QTabWidget

# centrowanie
from baza import HOST, USER, PASSWORD
from klienci import Customer
from pracownicy import Employee
from pracownicy_uslugi import ServEmpl
from rezerwacje import Reservations
from uslugi import Services
from zmiana_hasla import Password


def center(self):
    """
    Centruje okno.
    :param self: Klasa PyQT5
    """
    qr = self.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())


class Program(QMainWindow):
    """
    Główna klasa programu. Główne okno
    """

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

        # Parametry połączenia z bazą
        self.db = QSqlDatabase.addDatabase('QMYSQL')
        self.db.setHostName(HOST)
        self.db.setDatabaseName("NC6H7fYEuE")
        self.db.setUserName(USER)
        self.db.setPassword(PASSWORD)
        if self.db.open():
            print('Otworzono bazę danych')
        else:
            print(self.db.lastError().text())
            print(self.db.drivers())

        self.table_widget = TabsWidget(self)
        self.settings = QSettings('Jakub Hawro', 'System rezerwacji')

        self.initUI()

    def initUI(self):
        """
        Inicjalizuje UI
        """
        # Odpowiedzialne za utrzymanie rozmiaru i pozycji
        geometry = self.settings.value('geometria', bytes('', 'utf-8'))
        self.restoreGeometry(geometry)
        self.setCentralWidget(self.table_widget)

        # self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Program')
        center(self)
        self.show()

    def closeEvent(self, event):
        """
        Zapisuje rozmiar i położenie okna podczas zamknięcia
        :param event: Zakmnięcie programu
        """
        self.db.close()
        geometry = self.saveGeometry()
        self.settings.setValue('geometria', geometry)
        super(Program, self).closeEvent(event)


class TabsWidget(QWidget):
    """
    Klasa odpowiedzialna za zakładki
    """

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.initUI()

    def initUI(self):
        """
        Inicjalizuje UI
        """
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.South)
        tab1 = Reservations(self, self.parent.db)
        tab2 = Customer(self, self.parent.db)
        tab3 = ServEmpl(self, self.parent.db)
        tab4 = Services(self, self.parent.db)
        tab5 = Employee(self, self.parent.db)
        tab6 = Password(self)

        tabs.addTab(tab1, QIcon('icons/rezerwacje.png'), 'Rezerwacje')
        tabs.addTab(tab2, QIcon('icons/klienci.png'), 'Klienci')
        tabs.addTab(tab3, QIcon('icons/uslugi_pracownicy.png'), 'Pracownik-Usługi')
        tabs.addTab(tab4, QIcon('icons/uslugi.png'), 'Usługi')
        tabs.addTab(tab5, QIcon('icons/pracownicy.png'), 'Pracownicy')
        tabs.addTab(tab6, QIcon('icons/ustawienia.png'), 'Zmiana hasła')

        self.layout.addWidget(tabs)
        self.setLayout(self.layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Program(1)
    sys.exit(app.exec_())
