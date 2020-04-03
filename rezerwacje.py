'''
Plik odpowiedzialny za zakładkę rezerwacje
'''
import datetime
import sys

from PyQt5.QtCore import QSortFilterProxyModel, Qt, pyqtSlot, QRegExp, QMetaObject, QSize, QRect
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableView, QPushButton, \
    QGroupBox, QCalendarWidget, QSizePolicy, QDateTimeEdit, QAbstractScrollArea, QAbstractItemView, QMessageBox, \
    QComboBox, QDialogButtonBox, QDialog, QInputDialog

from baza import HOST, USER, PASSWORD, polaczenie, transakcja


class Reservations(QWidget):
    """
    Klasa odpowiedzialna za widget klienci
    """

    def __init__(self, parent, db):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.btn_mod = QPushButton('Zmiana statusu')
        self.btn_usun = QPushButton('Usuń')
        self.btn_dodaj = QPushButton('Dodaj')
        self.lbl_klient_ = QLabel('')
        self.lbl_usluga_ = QLabel('')
        self.lbl_termin_ = QDateTimeEdit()
        self.gb_layout = QVBoxLayout()
        self.kalendarz = QCalendarWidget()
        self.view_u = QTableView()
        self.view_k = QTableView()
        self.view_p = QTableView()
        self.view = QTableView()
        self.proxy_u = QSortFilterProxyModel(self)
        self.proxy_k = QSortFilterProxyModel(self)
        self.proxy_p = QSortFilterProxyModel(self)
        self.proxy = QSortFilterProxyModel(self)
        self.id_klient = -1
        self.id_usluga = -1
        self.id_pracownik = -1
        self.id_rezerwacje = -1
        self.data = None
        self.data_do = None
        self.dzien_tyg = 0
        self.czas = []

        # Lista składana przycisków godzin
        self.btn_godz = [QPushButton(str(i + 1)) for i in range(16)]

        # Parametry połączenia z bazą
        self.model_u = QSqlTableModel(self, db)
        self.model_k = QSqlTableModel(self, db)
        self.model_p = QSqlTableModel(self, db)
        self.model = QSqlTableModel(self, db)

        self.initUI()

    def initUI(self):
        """
        Inicjuje UI
        """
        self.view_u.setObjectName('Usługi')
        self.view_k.setObjectName('Klienci')
        self.view_p.setObjectName('Pracownicy')
        self.view.setObjectName('Rezerwacje')
        self.table_init_u()
        self.table_init_k()
        self.table_init_p()
        self.table_init()
        self.btn_mod.setDisabled(True)
        self.btn_usun.setDisabled(True)
        self.btn_dodaj.setDisabled(True)

        # Tworzenie kontrolek
        lbl_wysz_u = QLabel('Wyszukaj usługę:')
        lbl_wysz_k = QLabel('Wyszukaj klienta:')
        lbl_wysz_p = QLabel('Wyszukaj pracownika:')
        txt_wysz_u = QLineEdit(self)
        txt_wysz_k = QLineEdit(self)
        txt_wysz_p = QLineEdit(self)
        lbl_klient = QLabel('Klient:')
        lbl_usluga = QLabel('Usługa:')
        lbl_termin = QLabel('Termin:')

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.kalendarz.sizePolicy().hasHeightForWidth())
        self.kalendarz.setSizePolicy(sizePolicy)

        # Tworzenie widoków
        centralbox = QHBoxLayout()
        hbox_wysz_u = QHBoxLayout()
        hbox_wysz_k = QHBoxLayout()
        hbox_wysz_p = QHBoxLayout()
        vbox_u = QVBoxLayout()
        vbox_k = QVBoxLayout()
        vbox_p = QVBoxLayout()
        vbox_right = QVBoxLayout()
        hbox_btn = QHBoxLayout()
        hbox_k = QHBoxLayout()
        hbox_u = QHBoxLayout()
        hbox_t = QHBoxLayout()
        vbox_cal = QVBoxLayout()
        groupbox = QGroupBox('Godziny:')
        groupbox.setLayout(self.gb_layout)
        hbox_left = QHBoxLayout()

        # Metody
        self.lbl_termin_.setCalendarWidget(self.kalendarz)
        self.lbl_termin_.setDate(self.kalendarz.selectedDate())
        self.dzien_tyg = self.kalendarz.selectedDate().dayOfWeek()
        txt_wysz_u.textChanged.connect(self.wyszukiwanie_u)
        txt_wysz_k.textChanged.connect(self.wyszukiwanie_k)
        txt_wysz_p.textChanged.connect(self.wyszukiwanie_p)
        self.view_k.clicked.connect(lambda: self.clicked_table(self.view_k))
        self.view_p.clicked.connect(lambda: self.clicked_table(self.view_p))
        self.view_u.clicked.connect(lambda: self.clicked_table(self.view_u))
        self.view.clicked.connect(lambda: self.clicked_table(self.view))
        self.kalendarz.clicked.connect(self.show_data)
        self.btn_dodaj.clicked.connect(self.add)
        self.btn_mod.clicked.connect(self.modify)
        self.btn_usun.clicked.connect(self.remove)

        # Ustawianie widoków
        hbox_wysz_k.addWidget(lbl_wysz_k)
        hbox_wysz_k.addWidget(txt_wysz_k)
        hbox_wysz_p.addWidget(lbl_wysz_p)
        hbox_wysz_p.addWidget(txt_wysz_p)
        hbox_wysz_u.addWidget(lbl_wysz_u)
        hbox_wysz_u.addWidget(txt_wysz_u)
        vbox_u.addLayout(hbox_wysz_u)
        vbox_u.addWidget(self.view_u)
        vbox_k.addLayout(hbox_wysz_k)
        vbox_k.addWidget(self.view_k)
        vbox_p.addLayout(hbox_wysz_p)
        vbox_p.addWidget(self.view_p)
        vbox_right.addLayout(vbox_p)
        vbox_right.addLayout(vbox_u)
        vbox_right.addLayout(vbox_k)
        hbox_btn.addWidget(self.btn_usun)
        hbox_btn.addWidget(self.btn_mod)
        hbox_k.addWidget(lbl_klient)
        hbox_k.addWidget(self.lbl_klient_)
        hbox_u.addWidget(lbl_usluga)
        hbox_u.addWidget(self.lbl_usluga_)
        hbox_t.addWidget(lbl_termin)
        hbox_t.addWidget(self.lbl_termin_)
        vbox_cal.addWidget(self.kalendarz)
        vbox_cal.addLayout(hbox_k)
        vbox_cal.addLayout(hbox_t)
        vbox_cal.addLayout(hbox_u)
        self.view.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))
        vbox_cal.addWidget(self.view)
        vbox_cal.addLayout(hbox_btn)
        vbox_cal.addWidget(self.btn_dodaj)
        hbox_left.addLayout(vbox_cal)
        hbox_left.addWidget(groupbox)
        centralbox.addLayout(hbox_left)
        centralbox.addLayout(vbox_right)

        self.setLayout(centralbox)
        self.show()

    def show_data(self):
        self.lbl_termin_.setDate(self.kalendarz.selectedDate())
        self.dzien_tyg = self.kalendarz.selectedDate().dayOfWeek()
        self.clicked_table(self.view_p)

    def table_init_u(self):
        """
        Inicjuje wygląd tabeli usługi
        """
        # self.model_u.setTable('uslugi')
        query = QSqlQuery(
            'SELECT uslugi.uslugi_id, uslugi.nazwa, uslugi.cena, date_format(uslugi.czas, "%H:%i") AS czas FROM uslugi NATURAL JOIN uzytkownik_usluga WHERE uzytkownik_usluga.uzytkownik_id = ' + str(
                self.id_pracownik) + ';')
        self.model_u.setQuery(query)
        # self.model_u.select()

        self.proxy_u.setSourceModel(self.model_u)

        naglowki = {
            'uslugi_id': 'ID',
            'nazwa': 'Nazwa',
            'cena': 'Cena',
            "czas": 'Czas',
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

    def table_init_k(self):
        """
        Inicjuje wygląd tabeli klienta
        """
        self.model_k.setTable('klienci')
        query = QSqlQuery(
            'SELECT klienci_id, imie, nazwisko, email, telefon, ulica, numer_mieszkania, miejscowosc, poczta FROM '
            'klienci;')
        self.model_k.setQuery(query)
        # self.model_k.select()

        self.proxy_k.setSourceModel(self.model_k)

        naglowki = {
            'klienci_id': 'ID',
            'imie': 'Imię',
            'nazwisko': 'Nazwisko',
            "email": 'Email',
            'telefon': 'Telefon',
            'ulica': 'Ulica',
            'numer_mieszkania': 'Numer mieszkania',
            'miejscowosc': 'Miejscowosc',
            'poczta': 'Kod pocztowy',
        }
        # Ustawianie nagłówków
        ilosc_kolumn = self.model_k.columnCount()
        for i in range(ilosc_kolumn):
            nazwa_kolumn = self.model_k.headerData(i, Qt.Horizontal)
            self.model_k.setHeaderData(i, Qt.Horizontal, naglowki[nazwa_kolumn])

        self.view_k.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.view_k.setSortingEnabled(True)
        self.view_k.setAlternatingRowColors(True)

        # Wczytanie danych
        self.view_k.setModel(self.proxy_k)
        self.view_k.hideColumn(0)
        self.view_k.sortByColumn(1, Qt.AscendingOrder)
        self.view_k.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def table_init_p(self):
        """
        Inicjuje wygląd tabeli pracownik
        """
        self.model_p.setTable('uzytkownik')
        query = QSqlQuery('SELECT uzytkownik_id, uzytkownik_nazwa, imie, nazwisko, pracownik FROM uzytkownik WHERE '
                          'pracownik = 1;')
        self.model_p.setQuery(query)
        # self.model_p.select()

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
        self.view_p.sortByColumn(1, Qt.AscendingOrder)
        self.view_p.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def table_init(self):
        """
        Inicjuje wygląd tabeli
        """
        query = QSqlQuery(
            'SELECT wizyty.wizyty_id, CONCAT(klienci.imie, " ", klienci.nazwisko) AS klient, uslugi.nazwa, '
            'wizyty.rezerwacja_od, wizyty.rezerwacja_do, wizyty.status FROM klienci, uslugi NATURAL JOIN wizyty WHERE wizyty.rezerwacja_od > CURRENT_TIMESTAMP AND wizyty.uzytkownik_id = ' + str(
                self.id_pracownik) + ';')
        self.model.setQuery(query)
        self.proxy.setSourceModel(self.model)

        naglowki = {
            'wizyty_id': 'ID',
            'klient': 'Klient',
            'nazwa': 'Usługa',
            'rezerwacja_od': 'Rezerwacja od',
            "rezerwacja_do": 'Rezerwacja do',
            'status': 'Status rezerwacji'
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
        self.view.sortByColumn(4, Qt.AscendingOrder)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def clicked_table(self, view):
        """
        Metoda edytująca zaznaczone wiersze - Wstawia wartości z wierszy w odpowiednie pola
        """
        index = (view.selectionModel().currentIndex())
        if view.objectName() == 'Klienci':
            self.id_klient = index.sibling(index.row(), 0).data()
            self.lbl_klient_.setText(
                '<b>' + index.sibling(index.row(), 1).data() + ' ' + index.sibling(index.row(), 2).data() + '</b>')
        elif view.objectName() == 'Usługi':
            self.id_usluga = index.sibling(index.row(), 0).data()
            self.lbl_usluga_.setText('<b>' + index.sibling(index.row(), 1).data() + '</b>')
            self.data_do = index.sibling(index.row(), 3).data()
        elif view.objectName() == 'Rezerwacje':
            self.id_rezerwacje = index.sibling(index.row(), 0).data()
            if self.id_rezerwacje > 0:
                self.btn_mod.setEnabled(True)
                self.btn_usun.setEnabled(True)
        elif view.objectName() == 'Pracownicy':
            self.id_pracownik = index.sibling(index.row(), 0).data()
            self.czas = []
            for i in reversed(range(self.gb_layout.count())):
                self.gb_layout.itemAt(i).widget().setParent(None)
            czas = datetime.datetime(2000, 1, 1, 8, 0)
            dzien = {
                1: ('pon_od', 'pon_do'),
                2: ('wt_od', 'wt_do'),
                3: ('sr_od', 'sr_do'),
                4: ('czw_od', 'czw_do'),
                5: ('pt_od', 'pt_do'),
                6: ('sob_od', 'sob_do'),
                7: ('', '')
            }
            query = 'SELECT date_format({}, "%H") AS g_start, date_format({}, "%H") AS g_stop FROM godziny WHERE ' \
                    'uzytkownik_id = {};'.format(dzien[self.dzien_tyg][0], dzien[self.dzien_tyg][1], self.id_pracownik)
            wynik = polaczenie(query)
            if wynik:
                godzina_stop = (int(wynik[1]) - int(wynik[0])) * 2
                godzina = int(wynik[0])
                for btn in self.btn_godz:
                    btn.setEnabled(True)
            else:
                godzina_stop = 0
                godzina = 1
                for btn in self.btn_godz:
                    btn.setDisabled(True)
            minuta = 0
            czas = datetime.time(godzina, minuta)
            for i in range(godzina_stop):
                self.btn_godz[i].setText(czas.strftime("%H:%M"))
                self.czas.append(czas)
                self.btn_godz[i].setObjectName(str(i))
                self.gb_layout.addWidget(self.btn_godz[i])
                if i % 2 != 0:
                    godzina += 1
                    minuta = 0
                else:
                    minuta = 30
                czas = datetime.time(godzina, minuta)
            QMetaObject.connectSlotsByName(self)

            # Czyszczenie, odświeżanie
            self.refresh()
            query = QSqlQuery(
                'SELECT uslugi.uslugi_id, uslugi.nazwa, uslugi.cena, date_format(uslugi.czas, "%H:%i") AS czas FROM uslugi NATURAL JOIN uzytkownik_usluga WHERE uzytkownik_usluga.uzytkownik_id = ' + str(
                    self.id_pracownik) + ';')
            self.model_u.setQuery(query)
            self.lbl_klient_.setText('')
            self.lbl_usluga_.setText('')

        if self.id_klient > 0 and self.id_pracownik > 0 and self.id_usluga > 0:
            self.btn_dodaj.setEnabled(True)

    def if_checked(self, txt, q, val=None):
        """
        Sprawdza poprawność wprowadzonych damych.
        :param val: wartości do zapytania
        :param q: zapytanie query MySql
        :param txt: komunikat
        """
        if self.id_klient < 0 or self.id_pracownik < 0 or self.id_usluga < 0 or self.data:
            msg = QMessageBox(self)
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

            return True

    def refresh(self):
        """
        Odświeża widok tabeli rezerwacji
        """
        # Odświeżanie widoku tabeli
        query = QSqlQuery(
            'SELECT wizyty.wizyty_id, CONCAT(klienci.imie, " ", klienci.nazwisko) AS klient, uslugi.nazwa, '
            'wizyty.rezerwacja_od, wizyty.rezerwacja_do, wizyty.status FROM klienci, uslugi NATURAL JOIN wizyty WHERE wizyty.rezerwacja_od > CURRENT_TIMESTAMP AND wizyty.uzytkownik_id = ' + str(
                self.id_pracownik) + ';')
        self.model.setQuery(query)
        self.view.reset()

    def add(self):
        """
        Dodaje rezerwację do bazy danych i odświeża widok.
        """
        tekst = 'Nie wprowadzono wszystkich danych'
        self.data = self.lbl_termin_.dateTime().toString(Qt.ISODate)
        self.data_do = datetime.datetime.fromisoformat(self.data) + datetime.timedelta(
            hours=datetime.time.fromisoformat(self.data_do).hour,
            minutes=datetime.time.fromisoformat(self.data_do).minute)
        self.data_do = datetime.time.fromisoformat(self.data_do).hour
        # Dodanie nowego użytkownika
        query = 'INSERT INTO wizyty (klienci_id, uslugi_id, uzytkownik_id, rezerwacja_od, rezerwacja_do, ' \
                'status) VALUES (%s, %s, %s, %s, %s, %s);'
        val = (
            self.id_klient,
            self.id_usluga,
            self.id_pracownik,
            self.data,
            self.data_do,
            'oczekuje'
        )
        print(val)

        if self.if_checked(tekst, query, val):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setText('Rezerwacja została dodana do bazy danych')
            msg.setWindowTitle("Dodano nową rezerwację")
            msg.exec_()
            self.refresh()

    def modify(self):
        """
        Zmienia status rezerwacji i odświeża widok.
        """
        tekst = 'Nie wprowadzono wszystkich danych'

        items = ('Oczekuje', 'Wykonana', 'Rezygnacja')
        item, ok = QInputDialog.getItem(self, "Wybierz status",
                                        "Wybierz nowy status rezerwacji", items, 0, False)

        if ok and item:
            # Zmodyfikowanie statusu
            query = 'UPDATE wizyty SET status = %s WHERE wizyty_id = %s;'
            val = (
                item.lower(),
                self.id_rezerwacje
            )

            if self.if_checked(tekst, query, val):
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setText('Status rezerwacji został zmodyfikowany')
                msg.setWindowTitle("Zmodyfikowano status")
                msg.exec_()
                self.refresh()

    def remove(self):
        """
        Usuwa rezerwację z bazy danych
        """
        test = 'Błąd! Nie można usunąć danej rezerwacji!'
        query = 'DELETE FROM wizyty WHERE wizyty_id = %s'
        val = (self.id_rezerwacje,)
        ret = QMessageBox.question(self, 'Usuwanie rezerwacji', "Czy na pewno chcesz usunąć daną rezerwację klienta?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret == QMessageBox.Yes:
            if self.if_checked(test, query, val):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText('Rezerwacja została usunięta')
                msg.setWindowTitle("Usunięto")
                msg.exec_()

                self.refresh()

    @pyqtSlot()
    def on_0_clicked(self):
        self.lbl_termin_.setTime(self.czas[0])

    @pyqtSlot()
    def on_1_clicked(self):
        self.lbl_termin_.setTime(self.czas[1])

    @pyqtSlot()
    def on_2_clicked(self):
        self.lbl_termin_.setTime(self.czas[2])

    @pyqtSlot()
    def on_3_clicked(self):
        self.lbl_termin_.setTime(self.czas[3])

    @pyqtSlot()
    def on_4_clicked(self):
        self.lbl_termin_.setTime(self.czas[4])

    @pyqtSlot()
    def on_5_clicked(self):
        self.lbl_termin_.setTime(self.czas[5])

    @pyqtSlot()
    def on_6_clicked(self):
        self.lbl_termin_.setTime(self.czas[6])

    @pyqtSlot()
    def on_7_clicked(self):
        self.lbl_termin_.setTime(self.czas[7])

    @pyqtSlot()
    def on_8_clicked(self):
        self.lbl_termin_.setTime(self.czas[8])

    @pyqtSlot()
    def on_9_clicked(self):
        self.lbl_termin_.setTime(self.czas[9])

    @pyqtSlot()
    def on_10_clicked(self):
        self.lbl_termin_.setTime(self.czas[10])

    @pyqtSlot()
    def on_11_clicked(self):
        self.lbl_termin_.setTime(self.czas[11])

    @pyqtSlot()
    def on_12_clicked(self):
        self.lbl_termin_.setTime(self.czas[12])

    @pyqtSlot()
    def on_13_clicked(self):
        self.lbl_termin_.setTime(self.czas[13])

    @pyqtSlot()
    def on_14_clicked(self):
        self.lbl_termin_.setTime(self.czas[14])

    @pyqtSlot()
    def on_15_clicked(self):
        self.lbl_termin_.setTime(self.czas[15])

    @pyqtSlot(str)
    def wyszukiwanie_u(self, text):
        """
        Wyszukuje po wszystkich kolumnach tabeli
        :param text:
        """
        search = QRegExp(text,
                         Qt.CaseInsensitive,
                         QRegExp.RegExp
                         )
        self.proxy_u.setFilterRegExp(search)
        # Odpowiedzialne za kolumnę, po której filtruje
        self.proxy_u.setFilterKeyColumn(-1)

    @pyqtSlot(str)
    def wyszukiwanie_k(self, text):
        """
        Wyszukuje po wszystkich kolumnach tabeli
        :param text:
        """
        search = QRegExp(text,
                         Qt.CaseInsensitive,
                         QRegExp.RegExp
                         )
        self.proxy_k.setFilterRegExp(search)
        # Odpowiedzialne za kolumnę, po której filtruje
        self.proxy_k.setFilterKeyColumn(-1)

    @pyqtSlot(str)
    def wyszukiwanie_p(self, text):
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
        self.proxy_p.setFilterKeyColumn(-1)


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
    ex = Reservations(Program, db)
    ex.setFixedSize(1000, 600)
    Program.show()
    sys.exit(app.exec_())
