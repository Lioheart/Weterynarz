"""
Plik odpowiedzialny za zakładkę Klienci
"""
import sys

from PyQt5.QtCore import pyqtSlot, QRegExp, Qt, QSortFilterProxyModel
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLineEdit, QLabel, QTableView, QVBoxLayout, QGroupBox, \
    QGridLayout, QPushButton, QFormLayout, QAbstractScrollArea, QAbstractItemView, QMessageBox

from baza import HOST, USER, PASSWORD, polaczenie, transakcja


class Customer(QWidget):
    """
    Klasa odpowiedzialna za widget klienci
    """

    def __init__(self, parent, db):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.btn_usun = QPushButton('Usuń')
        self.btn_mod = QPushButton('Modyfikuj')

        self.txt_imie = QLineEdit()
        self.txt_nazwisko = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_tel = QLineEdit()
        self.txt_ulica = QLineEdit()
        self.txt_nr_dom = QLineEdit()
        self.txt_kod = QLineEdit()
        self.txt_miasto = QLineEdit()

        self.proxy = QSortFilterProxyModel(self)
        self.view = QTableView()
        # Parametry połączenia z bazą
        self.model = QSqlTableModel(self, db)
        self.id_modify = -1
        self.initUI()

    def initUI(self):
        """
        Inicjuje UI
        """
        self.table_init()
        self.btn_usun.setDisabled(True)
        self.btn_mod.setDisabled(True)

        # Walidacja
        self.txt_kod.setInputMask('99-999')

        # Tworzenie kontrolek
        lbl_wyszukaj = QLabel('Wyszukaj klienta:')
        txt_wysz = QLineEdit(self)
        btn_dodaj = QPushButton('Dodaj')
        lbl_1 = QLabel('Imię:')
        lbl_2 = QLabel('Nazwisko:')
        lbl_3 = QLabel('Email:')
        lbl_4 = QLabel('Telefon:')
        lbl_5 = QLabel('Ulica:')
        lbl_6 = QLabel('Numer domu:')
        lbl_7 = QLabel('Kod pocztowy:')
        lbl_8 = QLabel('Miejscowość:')

        # Tworzenie widoków
        centralbox = QVBoxLayout()
        hbox_wysz = QHBoxLayout()
        gropubox = QGroupBox('Edycja danych klienta')
        grop_layout = QGridLayout()
        hbox_btn = QHBoxLayout()
        form_left = QFormLayout()
        form_right = QFormLayout()

        # Metody
        self.view.clicked.connect(self.change)
        btn_dodaj.clicked.connect(self.add)
        self.btn_mod.clicked.connect(self.modify)
        self.btn_usun.clicked.connect(self.remove)
        txt_wysz.textChanged.connect(self.wyszukiwanie)

        # Ustawianie widoków
        hbox_wysz.addWidget(lbl_wyszukaj)
        hbox_wysz.addWidget(txt_wysz)
        hbox_btn.addWidget(self.btn_usun)
        hbox_btn.addWidget(self.btn_mod)
        hbox_btn.addWidget(btn_dodaj)
        form_left.setSpacing(9)
        form_right.setSpacing(9)
        form_left.setContentsMargins(0, 0, 10, 0)
        form_right.setContentsMargins(10, 0, 0, 0)
        form_left.addRow(lbl_1, self.txt_imie)
        form_left.addRow(lbl_2, self.txt_nazwisko)
        form_left.addRow(lbl_3, self.txt_email)
        form_left.addRow(lbl_4, self.txt_tel)
        form_right.addRow(lbl_5, self.txt_ulica)
        form_right.addRow(lbl_6, self.txt_nr_dom)
        form_right.addRow(lbl_7, self.txt_kod)
        form_right.addRow(lbl_8, self.txt_miasto)
        grop_layout.addItem(form_left, 0, 0)
        grop_layout.addItem(form_right, 0, 1)
        gropubox.setLayout(grop_layout)
        centralbox.addLayout(hbox_wysz)
        centralbox.addWidget(self.view)
        centralbox.addWidget(gropubox)
        centralbox.addLayout(hbox_btn)
        self.setLayout(centralbox)
        self.show()

    def change(self):
        """
        Metoda edytująca zaznaczone wiersze - Wstawia wartości z wierszy w odpowiednie pola
        """
        index = (self.view.selectionModel().currentIndex())
        value = index.sibling(index.row(), index.column()).data()
        self.id_modify = index.sibling(index.row(), 0).data()
        self.txt_imie.setText(index.sibling(index.row(), 1).data())
        self.txt_nazwisko.setText(str(index.sibling(index.row(), 2).data()))
        self.txt_email.setText(index.sibling(index.row(), 3).data())
        self.txt_tel.setText(index.sibling(index.row(), 4).data())
        self.txt_ulica.setText(index.sibling(index.row(), 5).data())
        self.txt_nr_dom.setText(index.sibling(index.row(), 6).data())
        self.txt_miasto.setText(index.sibling(index.row(), 7).data())
        self.txt_kod.setText(index.sibling(index.row(), 8).data())

        if self.id_modify >= 0 and self.txt_imie.text() and self.txt_nazwisko.text():
            self.btn_mod.setEnabled(True)
            self.btn_usun.setEnabled(True)
        else:
            self.btn_usun.setDisabled(True)
            self.btn_mod.setDisabled(True)
            value.setText('')

    def table_init(self):
        """
        Inicjuje wygląd tabeli
        """
        self.model.setTable('klienci')
        query = QSqlQuery('SELECT klienci_id, imie, nazwisko, email, telefon, ulica, numer_mieszkania, miejscowosc, poczta FROM '
                          'klienci;')
        self.model.setQuery(query)
        self.proxy.setSourceModel(self.model)

        naglowki = {
            'klienci_id': 'ID',
            'imie': 'Imię',
            'nazwisko': 'Nazwisko',
            "email": 'Email',
            'telefon': 'Telefon',
            'ulica': 'Ulica',
            'numer_mieszkania':'Numer mieszkania',
            'miejscowosc': 'Miejscowosc',
            'poczta': 'Kod pocztowy',
        }
        # Ustawianie nagłówków
        ilosc_kolumn = self.model.columnCount()
        for i in range(ilosc_kolumn):
            nazwa_kolumn = self.model.headerData(i, Qt.Horizontal)
            self.model.setHeaderData(i, Qt.Horizontal, naglowki[nazwa_kolumn])

        self.view.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.view.setSortingEnabled(True)
        self.view.setAlternatingRowColors(True)

        # Wczytanie danych
        self.view.setModel(self.proxy)
        self.view.hideColumn(0)
        self.view.sortByColumn(1, Qt.AscendingOrder)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def if_checked(self, txt, q, val=None):
        """
        Sprawdza poprawność wprowadzonych damych.
        :param val: wartości do zapytania
        :param q: zapytanie query MySql
        :param txt: komunikat
        """
        if len(self.txt_imie.text()) < 3 or len(self.txt_nazwisko.text()) < 1:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(txt)
            msg.setWindowTitle("Popraw dane")
            msg.exec_()
            return False
        else:
            print('Trwa zmiana w bazie danych')
            if val:
                print('Połączenie')
                polaczenie(q, val)
            else:
                print('Transakcja')
                return transakcja(q)

            # Odświeżanie widoku tabeli
            self.model.select()
            self.view.reset()
            return True

    def add(self):
        """
        Dodaje nowego klienta do bazy danych i odświeża widok.
        """
        tekst = 'Nie wprowadzono wszystkich danych'
        # Dodanie nowego użytkownika
        query = 'INSERT INTO klienci (imie, nazwisko, email, telefon, ulica, numer_mieszkania, miejscowosc, ' \
                'poczta) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'
        val = (
            self.txt_imie.text(),
            self.txt_nazwisko.text(),
            self.txt_email.text(),
            self.txt_tel.text(),
            self.txt_ulica.text(),
            self.txt_nr_dom.text(),
            self.txt_miasto.text(),
            self.txt_kod.text()
        )

        if self.if_checked(tekst, query, val):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setText('Klient został dodany do bazy danych')
            msg.setWindowTitle("Dodano nowego klienta")
            msg.exec_()

    def modify(self):
        """
        Modyfikuje bazę danych
        """
        tekst = 'Nie wprowadzono wszystkich danych'
        # Dodanie nowego użytkownika
        query = 'UPDATE klienci SET imie = %s, nazwisko = %s, email = %s, telefon = %s, ulica = %s, ' \
                'numer_mieszkania = %s, miejscowosc = %s, poczta = %s WHERE klienci_id = %s;'
        val = (
            self.txt_imie.text(),
            self.txt_nazwisko.text(),
            self.txt_email.text(),
            self.txt_tel.text(),
            self.txt_ulica.text(),
            self.txt_nr_dom.text(),
            self.txt_miasto.text(),
            self.txt_kod.text(),
            self.id_modify
        )
        if self.if_checked(tekst, query, val):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setText('Dane klienta zostały pomyślnie zmodyfikowane')
            msg.setWindowTitle("Dane klienta zostały zmodyfikowane")
            msg.exec_()

    def remove(self):
        """
        Usuwa klientów z bazy danych
        """
        test = 'Błąd! Nie można usunąć danej usługi!'
        query = 'DELETE FROM klienci WHERE klienci_id = %s'
        val = (self.id_modify,)
        ret = QMessageBox.question(self, 'Usuwanie klienta', "Czy na pewno chcesz usunąć danego klienta?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret == QMessageBox.Yes:
            if self.if_checked(test, query, val):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText('Klient został usunięty')
                msg.setWindowTitle("Usunięto")
                msg.exec_()

                self.txt_imie.setText('')
                self.txt_nazwisko.setText(''),
                self.txt_email.setText(''),
                self.txt_tel.setText(''),
                self.txt_ulica.setText(''),
                self.txt_nr_dom.setText(''),
                self.txt_miasto.setText(''),
                self.txt_kod.setText(''),

    @pyqtSlot(str)
    def wyszukiwanie(self, text):
        """
        Wyszukuje po wszystkich kolumnach tabeli
        :param text:
        """
        search = QRegExp(text,
                         Qt.CaseInsensitive,
                         QRegExp.RegExp
                         )
        self.proxy.setFilterRegExp(search)
        # Odpowiedzialne za kolumnę, po której filtruje
        self.proxy.setFilterKeyColumn(-1)


if __name__ == '__main__':
    # Parametry połączenia z bazą
    db = QSqlDatabase.addDatabase('QMYSQL')
    db.setHostName(HOST)
    db.setDatabaseName("NC6H7fYEuE")
    db.setUserName(USER)
    db.setPassword(PASSWORD)
    if db.open():
        print('Otworzono bazę danych')
    else:
        print(db.lastError().text())
        print(db.drivers())

    app = QApplication(sys.argv)
    Program = QWidget()
    Program.setFixedSize(1000, 600)
    ex = Customer(Program, db)
    ex.setFixedSize(1000, 600)
    Program.show()
    sys.exit(app.exec_())
