"""
Plik odpowiedzialny za widget pracownicy-usługi
"""
import sys

from PyQt5.QtCore import QSortFilterProxyModel, pyqtSlot, QRegExp, Qt
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery, QSqlRelationalTableModel
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QGroupBox, QTableView, QVBoxLayout, QLabel, QFormLayout, \
    QSpacerItem, QSizePolicy, QLineEdit, QAbstractScrollArea, QAbstractItemView, QMessageBox

from baza import HOST, USER, PASSWORD, query_to_db


class ServEmpl(QWidget):
    """
    Klasa odpowiedzialna za widget pracownicy-usługi
    """

    def __init__(self, parent, db):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.lbl_imie = QLabel()
        self.lbl_nazwisko = QLabel()
        self.view_p = QTableView()
        self.view_pu = QTableView()
        self.view_u = QTableView()
        self.proxy_p = QSortFilterProxyModel(self)
        self.proxy_pu = QSortFilterProxyModel(self)
        self.proxy_u = QSortFilterProxyModel(self)
        self.id_pracownik = -1

        # Parametry połączenia z bazą
        self.model_p = QSqlTableModel(self, db)
        self.model_pu = QSqlRelationalTableModel(self, db)
        self.model_u = QSqlTableModel(self, db)

        self.initUI()

    def initUI(self):
        """
        Inicjuje UI
        """
        pracownicy = '''
        Kliknij <u>tutaj</u> aby wybrać danego pracownika.
        Poniżej znajdują się wszystkie usługi, jakie dany pracownik może robić.
        '''
        uslugi = '''
        Kliknij dwukrotnie <u>tutaj</u> aby <b>przypisać</b> daną usługę do wybranego pracownika.
        '''
        pracownik_uslugi = '''
        Kliknij dwukrotnie <u>tutaj</u> aby <b>usunąć</b> przypisanie danej usługi pracownikowi.
        '''
        self.table_init_u()
        self.table_init_p()
        self.table_init_pu()
        self.view_p.setToolTip(pracownicy)
        self.view_u.setToolTip(uslugi)
        self.view_pu.setToolTip(pracownik_uslugi)

        # Tworzenie kontrolek
        lbl_wyszukaj = QLabel('Wyszukaj pracownika:')
        lbl_imie_static = QLabel('Imię:')
        lbl_nazwisko_static = QLabel('Nazwisko:')
        txt_wysz = QLineEdit(self)

        # Tworzenie widoków
        centralbox = QHBoxLayout()
        hbox_p = QHBoxLayout()
        hbox_pu = QHBoxLayout()
        hbox_u = QHBoxLayout()
        vbox_right = QVBoxLayout()
        vbox_left = QVBoxLayout()
        groupbox_p = QGroupBox('Pracownicy')
        groupbox_pu = QGroupBox('Wykonywane usługi')
        groupbox_u = QGroupBox('Usługi')
        formbox = QFormLayout()

        # Metody
        txt_wysz.textChanged.connect(self.searching)
        self.view_p.clicked.connect(self.change_p)
        self.view_u.doubleClicked.connect(lambda: self.change_add_remove(True))
        self.view_pu.doubleClicked.connect(lambda: self.change_add_remove(False))

        # Ustawianie widoków
        formbox.addRow(lbl_wyszukaj, txt_wysz)
        formbox.addRow(lbl_imie_static, self.lbl_imie)
        formbox.addRow(lbl_nazwisko_static, self.lbl_nazwisko)
        formbox.setSpacing(15)
        vbox_left.addLayout(formbox)
        vbox_left.addWidget(groupbox_u)
        vbox_left.setSpacing(200)
        hbox_p.addWidget(self.view_p)
        hbox_pu.addWidget(self.view_pu)
        hbox_u.addWidget(self.view_u)
        groupbox_p.setLayout(hbox_p)
        groupbox_pu.setLayout(hbox_pu)
        groupbox_u.setLayout(hbox_u)
        vbox_right.addWidget(groupbox_p)
        vbox_right.addWidget(groupbox_pu)
        vbox_right.setSpacing(25)
        centralbox.addLayout(vbox_left)
        centralbox.addLayout(vbox_right)
        self.setLayout(centralbox)
        self.show()

    def change_p(self):
        """
        Metoda edytująca zaznaczone wiersze - Wstawia wartości z wierszy w odpowiednie pola
        """
        index = (self.view_p.selectionModel().currentIndex())
        self.id_pracownik = index.sibling(index.row(), 0).data()
        self.lbl_imie.setText("<b>" + index.sibling(index.row(), 2).data() + "</b>")
        self.lbl_nazwisko.setText("<b>" + index.sibling(index.row(), 3).data() + "</b>")

        # Odświeżanie widoku tabeli
        query = QSqlQuery(
            'SELECT uslugi.uslugi_id, uslugi.nazwa, uslugi.cena, uslugi.czas FROM uslugi, uzytkownik_usluga WHERE '
            'uslugi.uslugi_id = uzytkownik_usluga.uslugi_id AND uzytkownik_usluga.uzytkownik_id = ' + str(
                self.id_pracownik) + ';')
        self.model_pu.setQuery(query)
        self.view_pu.reset()

    def change_add_remove(self, quest):
        """
        Metoda ogólna odpowiadająca za dodawanie i usuwanie usług wybranemu pracownikowi
        """
        tekst_p = "Czy chcesz dodać nową usługę do użytkownika {}?".format(self.lbl_imie.text())
        if quest:
            index = (self.view_u.selectionModel().currentIndex())
            id_modify = index.sibling(index.row(), 0).data()
            ret = QMessageBox.question(self, 'Dodawanie usługi', tekst_p,
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ret == QMessageBox.Yes:
                query = 'INSERT INTO uzytkownik_usluga (uzytkownik_id, uslugi_id) VALUES (%s, %s); '
                val = (
                    self.id_pracownik,
                    id_modify
                )
                if query_to_db(query, val):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText('Usługa została dodana do usług oferowanych przez pracownika')
                    msg.setWindowTitle("Dodano usługę")
                    msg.exec_()
        else:
            index = (self.view_pu.selectionModel().currentIndex())
            id_modify = index.sibling(index.row(), 0).data()
            ret = QMessageBox.question(self, 'Usuwanie usługi', "Czy na pewno chcesz usunąć daną usługę?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ret == QMessageBox.Yes:
                query = 'DELETE FROM uzytkownik_usluga WHERE uzytkownik_id = %s AND uslugi_id = %s; '
                val = (
                    self.id_pracownik,
                    id_modify
                )
                if query_to_db(query, val):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText('Usługa została dodana do usług oferowanych przez pracownika')
                    msg.setWindowTitle("Dodano usługę")
                    msg.exec_()
        # Odświeżanie widoku tabeli
        query = QSqlQuery(
            'SELECT uslugi.uslugi_id, uslugi.nazwa, uslugi.cena, uslugi.czas FROM uslugi, uzytkownik_usluga WHERE '
            'uslugi.uslugi_id = uzytkownik_usluga.uslugi_id AND uzytkownik_usluga.uzytkownik_id = ' + str(
                self.id_pracownik) + ';')
        self.model_pu.setQuery(query)
        self.view_pu.reset()

    def table_init_u(self):
        """
        Inicjuje wygląd tabeli usługi
        """
        self.model_u.setTable('uslugi')
        # query = QSqlQuery('SELECT uzytkownik_id, uzytkownik_nazwa, imie, nazwisko, pracownik FROM uzytkownik;')
        # self.model.setQuery(query)
        self.model_u.select()

        self.proxy_u.setSourceModel(self.model_u)

        naglowki = {
            'uslugi_id': 'ID',
            'nazwa': 'Nazwa',
            'cena': 'Cena',
            "czas": 'Czas',
            'Opis': 'Opis',
        }
        # Ustawianie nagłówków
        ilosc_kolumn = self.model_u.columnCount()
        for i in range(ilosc_kolumn):
            nazwa_kolumn = self.model_u.headerData(i, Qt.Horizontal)
            self.model_u.setHeaderData(i, Qt.Horizontal, naglowki[nazwa_kolumn])

        self.view_u.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.view_u.setSortingEnabled(True)
        self.view_u.setAlternatingRowColors(True)

        # Wczytanie danych
        self.view_u.setModel(self.proxy_u)
        self.view_u.hideColumn(0)
        self.view_u.sortByColumn(1, Qt.AscendingOrder)
        self.view_u.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def table_init_p(self):
        """
        Inicjuje wygląd tabeli pracownicy
        """
        self.model_p.setTable('pracownicy')
        query = QSqlQuery('SELECT uzytkownik_id, uzytkownik_nazwa, imie, nazwisko, pracownik FROM uzytkownik WHERE pracownik = 1;')
        self.model_p.setQuery(query)
        # self.model_u.select()

        self.proxy_p.setSourceModel(self.model_p)

        naglowki = {
            'uzytkownik_id': 'ID',
            'uzytkownik_nazwa': 'Login',
            'imie': 'Imię',
            "nazwisko": 'Nazwisko',
            'pracownik': 'Pracownik',
        }
        # Ustawianie nagłówków
        ilosc_kolumn = self.model_p.columnCount()
        for i in range(ilosc_kolumn):
            nazwa_kolumn = self.model_p.headerData(i, Qt.Horizontal)
            self.model_p.setHeaderData(i, Qt.Horizontal, naglowki[nazwa_kolumn])

        self.view_p.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.view_p.setSortingEnabled(True)
        self.view_p.setAlternatingRowColors(True)

        # Wczytanie danych
        self.view_p.setModel(self.proxy_p)
        self.view_p.hideColumn(0)
        self.view_p.hideColumn(4)
        self.view_p.sortByColumn(1, Qt.AscendingOrder)
        self.view_p.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def table_init_pu(self):
        """
        Inicjuje wygląd tabeli pracownicy-usługi
        """
        query = QSqlQuery(
            'SELECT uslugi.uslugi_id, uslugi.nazwa, uslugi.cena, uslugi.czas FROM uslugi, uzytkownik_usluga WHERE '
            'uslugi.uslugi_id = uzytkownik_usluga.uslugi_id AND uzytkownik_usluga.uzytkownik_id = ' + str(
                self.id_pracownik) + ';')
        self.model_pu.setQuery(query)

        self.proxy_pu.setSourceModel(self.model_pu)

        naglowki = {
            'uslugi_id': 'ID usługi',
            'nazwa': 'Nazwa usługi',
            'cena': 'Cena',
            'czas': 'Czas'
        }
        # Ustawianie nagłówków
        ilosc_kolumn = self.model_pu.columnCount()
        for i in range(ilosc_kolumn):
            nazwa_kolumn = self.model_pu.headerData(i, Qt.Horizontal)
            self.model_pu.setHeaderData(i, Qt.Horizontal, naglowki[nazwa_kolumn])

        self.view_pu.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.view_pu.setSortingEnabled(True)
        self.view_pu.setAlternatingRowColors(True)

        # Wczytanie danych
        self.view_pu.setModel(self.proxy_pu)
        self.view_pu.hideColumn(0)
        self.view_pu.sortByColumn(1, Qt.AscendingOrder)
        self.view_pu.setEditTriggers(QAbstractItemView.NoEditTriggers)

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
        self.proxy_p.setFilterRegExp(search)
        # Odpowiedzialne za kolumnę, po której filtruje
        self.proxy_p.setFilterKeyColumn(1)


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
    ex = ServEmpl(Program, db)
    ex.setFixedSize(1000, 600)
    Program.show()
    sys.exit(app.exec_())
