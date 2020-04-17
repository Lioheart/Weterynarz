"""
Plik odpowiedzialny za widget usług
"""
import sys

from PyQt5.QtCore import QSortFilterProxyModel, Qt, pyqtSlot, QRegExp
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QAbstractScrollArea, QAbstractItemView, QTableView, \
    QLabel, QLineEdit, QGroupBox, QVBoxLayout, QPushButton, QFormLayout, QTextEdit, QMessageBox

from baza import HOST, USER, PASSWORD, query_to_db, transaction_to_db


class Services(QWidget):
    """
    Klasa odpowiedzialna za widget usług
    """

    def __init__(self, parent, db):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.proxy = QSortFilterProxyModel(self)
        self.view = QTableView()
        self.txt_nazwa = QLineEdit()
        self.txt_cena = QLineEdit()
        self.txt_czas = QLineEdit()
        self.txt_opis = QTextEdit()
        self.btn_mod = QPushButton('Modyfikuj')
        self.btn_usun = QPushButton('Usuń')
        self.id_modify = -1

        # Parametry połączenia z bazą
        self.model = QSqlTableModel(self, db)

        self.initUI()

    def initUI(self):
        """
        Inicjuje UI
        """
        self.table_init()
        self.btn_usun.setDisabled(True)
        self.btn_mod.setDisabled(True)
        self.txt_czas.setInputMask('99:00')

        # Tworzenie kontrolek
        lbl_wysz = QLabel("Wyszukaj zabieg:")
        txt_wysz = QLineEdit(self)
        btn_dodaj = QPushButton('Dodaj')
        lbl_nazwa = QLabel('Nazwa:')
        lbl_cena = QLabel('Cena:')
        lbl_czas = QLabel('Czas:')
        lbl_opis = QLabel('Opis:')

        # Tworzenie widoków
        centralbox = QHBoxLayout()
        findbox = QHBoxLayout()
        vbox = QVBoxLayout()
        groupbox = QGroupBox('Zabiegi')
        groupbox_layout = QVBoxLayout()
        button_hbox = QHBoxLayout()
        formbox = QFormLayout()

        # Metody
        self.view.clicked.connect(self.change)
        txt_wysz.textChanged.connect(self.searching)
        btn_dodaj.clicked.connect(self.add)
        self.btn_mod.clicked.connect(self.modify)
        self.btn_usun.clicked.connect(self.remove)

        # Ustawianie widoków
        findbox.addWidget(lbl_wysz)
        findbox.addWidget(txt_wysz)
        button_hbox.addWidget(btn_dodaj)
        button_hbox.addWidget(self.btn_mod)
        button_hbox.addWidget(self.btn_usun)
        formbox.addRow(lbl_nazwa, self.txt_nazwa)
        formbox.addRow(lbl_cena, self.txt_cena)
        formbox.addRow(lbl_czas, self.txt_czas)
        formbox.addRow(lbl_opis, self.txt_opis)
        groupbox_layout.addLayout(formbox)
        groupbox_layout.addLayout(button_hbox)
        groupbox.setLayout(groupbox_layout)
        vbox.addLayout(findbox)
        vbox.addWidget(groupbox)
        centralbox.addLayout(vbox)
        centralbox.addWidget(self.view)
        self.setLayout(centralbox)
        self.show()

    def table_init(self):
        """
        Inicjuje wygląd tabeli
        """
        self.model.setTable('uslugi')
        # query = QSqlQuery('SELECT uzytkownik_id, uzytkownik_nazwa, imie, nazwisko, pracownik FROM uzytkownik;')
        # self.model.setQuery(query)
        self.model.select()

        self.proxy.setSourceModel(self.model)

        naglowki = {
            'uslugi_id': 'ID',
            'nazwa': 'Nazwa',
            'cena': 'Cena',
            "czas": 'Czas',
            'Opis': 'Opis',
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

    def change(self):
        """
        Metoda edytująca zaznaczone wiersze - Wstawia wartości z wierszy w odpowiednie pola
        """
        index = (self.view.selectionModel().currentIndex())
        value = index.sibling(index.row(), index.column()).data()
        self.id_modify = index.sibling(index.row(), 0).data()
        self.txt_nazwa.setText(index.sibling(index.row(), 1).data())
        self.txt_cena.setText(str(index.sibling(index.row(), 2).data()))
        self.txt_czas.setText(index.sibling(index.row(), 3).data())
        self.txt_opis.setText(index.sibling(index.row(), 4).data())

        if self.id_modify >= 0 and self.txt_nazwa.text() and self.txt_cena.text() and self.txt_czas.text():
            self.btn_mod.setEnabled(True)
            self.btn_usun.setEnabled(True)
        else:
            self.btn_usun.setDisabled(True)
            self.btn_mod.setDisabled(True)
            value.setText('')

    def if_checked(self, txt, q, val=None):
        """
        Sprawdza poprawność wprowadzonych damych.
        :param val: wartości do zapytania
        :param q: zapytanie query MySql
        :param txt: komunikat
        """
        if len(self.txt_nazwa.text()) < 3 or len(self.txt_cena.text()) < 1 or len(self.txt_czas.text()) < 2:
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
                t = query_to_db(q, val)
                print(t)
                return t  # = polaczenie(q, val)
            else:
                print('Transakcja')
                return transaction_to_db(q)

    def add(self):
        """
        Dodaje nową usługę do bazy danych i odświeża widok.
        """
        tekst = 'Nie wprowadzono wszystkich danych'
        # Dodanie nowego użytkownika
        query = 'INSERT INTO uslugi (nazwa, cena, czas, Opis) VALUES (%s, %s, %s, %s)'
        val = (
            self.txt_nazwa.text(),
            self.txt_cena.text().replace(',', '.'),
            self.txt_czas.text(),
            self.txt_opis.toPlainText()
        )

        if self.if_checked(tekst, query, val):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setText('Dodano nową usługę')
            msg.setWindowTitle("Dodano nową usługę")
            msg.exec_()
        else:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setText('Usługa znajduje się już w bazie')
            msg.setWindowTitle("Błąd!")
            msg.exec_()
        # Odświeżanie widoku tabeli
        self.model.select()
        self.view.reset()

    def modify(self):
        """
        Modyfikuje bazę danych
        """
        test = 'Dane zostały błędnie zmodyfikowane.'
        query = 'UPDATE uslugi SET nazwa = %s, cena = %s, czas = %s, Opis = %s WHERE uslugi_id = %s;'
        val = (
            self.txt_nazwa.text(),
            self.txt_cena.text().replace(',', '.'),
            self.txt_czas.text(),
            self.txt_opis.toPlainText(),
            self.id_modify
        )

        if self.if_checked(test, query, val):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setText('Informacje o usłudze zostały pomyślnie zmodyfikowane')
            msg.setWindowTitle("Zmodyfikowano usługi")
            msg.exec_()
        # Odświeżanie widoku tabeli
        self.model.select()
        self.view.reset()

    def remove(self):
        """
        Usuwa dane z bazy danych
        """
        test = 'Błąd! Nie można usunąć danej usługi!'
        query2 = 'DELETE FROM wizyty WHERE uslugi_id = %s'
        query = 'DELETE FROM uslugi WHERE uslugi_id = %s'
        val = (self.id_modify,)
        query1 = 'DELETE FROM uzytkownik_usluga WHERE uslugi_id = %s'
        ret = QMessageBox.question(self, 'Usuwanie usługi', "Czy na pewno chcesz usunąć daną usługę?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret == QMessageBox.Yes:
            if self.if_checked(test, [(query2, val), (query1, val), (query, val)]):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText('Usługa została usunięta')
                msg.setWindowTitle("Usunięto")
                msg.exec_()

                self.txt_nazwa.setText('')
                self.txt_cena.setText('')
                self.txt_czas.setText('')
                self.txt_opis.setText('')

        # Odświeżanie widoku tabeli
        self.model.select()
        self.view.reset()

    @pyqtSlot(str)
    def searching(self, text):
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
        self.proxy.setFilterKeyColumn(1)


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
    ex = Services(Program, db)
    Program.show()
    sys.exit(app.exec_())
