"""
Plik odpowiedzialny za zakładkę Pracownicy
"""
import sys
from datetime import timedelta

from PyQt5.QtCore import QSortFilterProxyModel, pyqtSlot, QRegExp, Qt
from PyQt5.QtSql import QSqlDatabase, QSqlRelationalTableModel, QSqlRelationalDelegate, QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout, QApplication, QTableWidget, QTableView, \
    QAbstractItemView, QAbstractScrollArea, QVBoxLayout, QLabel, QFormLayout, QGroupBox, QCheckBox, QSpacerItem, \
    QMessageBox

from baza import HOST, USER, PASSWORD, polaczenie, transakcja


class Employee(QWidget):
    """
    Klasa odpowiedzialna za widget Zmiany hasła
    """

    def __init__(self, parent, db):
        super(QWidget, self).__init__(parent)
        self.btn_usun = QPushButton('Usuń')
        self.btn_modyfikuj = QPushButton('Modyfikuj')
        self.id_modify = -1
        self.view = QTableView()
        self.cb_pracownik = QCheckBox('Pracownik')
        self.txt_login = QLineEdit()
        self.txt_nazwisko = QLineEdit()
        self.txt_imie = QLineEdit()
        self.parent = parent
        self.layout = QHBoxLayout()
        self.lbl_wysz = QLabel("Wyszukaj:")
        self.txt_wysz = QLineEdit(self)
        self.proxy = QSortFilterProxyModel(self)

        # Parametry połączenia z bazą
        self.model = QSqlTableModel(self, db)
        self.initUI()

    def initUI(self):
        """
        Inicjuje UI
        """
        fbox = QFormLayout()
        fbox.addRow(self.lbl_wysz, self.txt_wysz)
        self.txt_wysz.textChanged.connect(self.wyszukiwanie)
        self.table_init()

        # Pokazuje wszystko
        # self.model.select()

        group_box = QGroupBox("Edycja danych użytkownika")
        fbox2 = QFormLayout()
        lbl_imie = QLabel('Imię:')
        lbl_nazwisko = QLabel('Nazwisko:')
        lbl_login = QLabel('Login:')
        btn_dodaj = QPushButton('Dodaj')
        self.btn_modyfikuj.setDisabled(True)
        self.btn_usun.setDisabled(True)
        fbox2.addRow(lbl_imie, self.txt_imie)
        fbox2.addRow(lbl_nazwisko, self.txt_nazwisko)
        fbox2.addRow(lbl_login, self.txt_login)
        fbox2.addRow(self.cb_pracownik)
        lhbox = QHBoxLayout()
        lhbox.addWidget(self.btn_usun)
        lhbox.addSpacing(35)
        lhbox.addWidget(self.btn_modyfikuj)
        lhbox.addSpacing(35)
        lhbox.addWidget(btn_dodaj)
        fbox2.addRow(lhbox)
        group_box.setLayout(fbox2)
        fbox.addRow(group_box)

        # Formatka dni
        self.group_box_dni = QGroupBox('Godziny pracy')
        fbox_dni = QFormLayout()
        lhbox_pon = QHBoxLayout()
        lhbox_wt = QHBoxLayout()
        lhbox_sr = QHBoxLayout()
        lhbox_czw = QHBoxLayout()
        lhbox_pt = QHBoxLayout()
        lhbox_sob = QHBoxLayout()
        lbl_pon = QLabel('Poniedziałek')
        lbl_wt = QLabel('Wtorek')
        lbl_sr = QLabel('Środa')
        lbl_czw = QLabel('Czwartek')
        lbl_pt = QLabel('Piątek')
        lbl_sob = QLabel('Sobota')
        self.txt_pon_od = QLineEdit()
        self.txt_pon_do = QLineEdit()
        self.txt_wt_od = QLineEdit()
        self.txt_wt_do = QLineEdit()
        self.txt_sr_od = QLineEdit()
        self.txt_sr_do = QLineEdit()
        self.txt_czw_od = QLineEdit()
        self.txt_czw_do = QLineEdit()
        self.txt_pt_od = QLineEdit()
        self.txt_pt_do = QLineEdit()
        self.txt_sob_od = QLineEdit()
        self.txt_sob_do = QLineEdit()
        self.pola = (
            self.txt_pon_od,
            self.txt_pon_do,
            self.txt_wt_od,
            self.txt_wt_do,
            self.txt_sr_od,
            self.txt_sr_do,
            self.txt_czw_od,
            self.txt_czw_do,
            self.txt_pt_od,
            self.txt_pt_do,
            self.txt_sob_od,
            self.txt_sob_do
        )
        lhbox_pon.addWidget(self.txt_pon_od)
        lhbox_pon.addSpacing(30)
        lhbox_pon.addWidget(self.txt_pon_do)
        lhbox_wt.addWidget(self.txt_wt_od)
        lhbox_wt.addSpacing(30)
        lhbox_wt.addWidget(self.txt_wt_do)
        lhbox_sr.addWidget(self.txt_sr_od)
        lhbox_sr.addSpacing(30)
        lhbox_sr.addWidget(self.txt_sr_do)
        lhbox_czw.addWidget(self.txt_czw_od)
        lhbox_czw.addSpacing(30)
        lhbox_czw.addWidget(self.txt_czw_do)
        lhbox_pt.addWidget(self.txt_pt_od)
        lhbox_pt.addSpacing(30)
        lhbox_pt.addWidget(self.txt_pt_do)
        lhbox_sob.addWidget(self.txt_sob_od)
        lhbox_sob.addSpacing(30)
        lhbox_sob.addWidget(self.txt_sob_do)
        fbox_dni.addRow(lbl_pon, lhbox_pon)
        fbox_dni.addRow(lbl_wt, lhbox_wt)
        fbox_dni.addRow(lbl_sr, lhbox_sr)
        fbox_dni.addRow(lbl_czw, lhbox_czw)
        fbox_dni.addRow(lbl_pt, lhbox_pt)
        fbox_dni.addRow(lbl_sob, lhbox_sob)
        group_box_szablon = QGroupBox('Szablony')
        btn1 = QPushButton('7-15')
        btn2 = QPushButton('8-16')
        btn3 = QPushButton('9-17')
        btn4 = QPushButton('10-18')
        vbox = QVBoxLayout()
        vbox.addWidget(btn1)
        vbox.addWidget(btn2)
        vbox.addWidget(btn3)
        vbox.addWidget(btn4)
        group_box_szablon.setLayout(vbox)
        hbox_dni = QHBoxLayout()
        hbox_dni.addLayout(fbox_dni)
        hbox_dni.addWidget(group_box_szablon)
        self.group_box_dni.setLayout(hbox_dni)
        fbox.addRow(self.group_box_dni)
        self.group_box_dni.setVisible(False)

        self.view.clicked.connect(self.change)
        btn_dodaj.clicked.connect(self.add)
        self.btn_modyfikuj.clicked.connect(self.modify)
        self.btn_usun.clicked.connect(self.remove)
        self.cb_pracownik.stateChanged.connect(self.changeGroupBox)
        btn1.clicked.connect(lambda: self.hour(7))
        btn2.clicked.connect(lambda: self.hour(8))
        btn3.clicked.connect(lambda: self.hour(9))
        btn4.clicked.connect(lambda: self.hour(10))

        self.layout.addLayout(fbox)
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)
        self.show()

    def hour(self, godz):
        """
        Wypełnia godzinami odpowiednie pola
        :param godz: int godzina rozpoczęcia
        """
        for i, value in enumerate(self.pola):
            if i % 2 == 0:
                value.setText(str(timedelta(hours=godz)))
            else:
                value.setText(str(timedelta(hours=godz + 8)))

    def changeGroupBox(self, state):
        """
        Sprawdza, czy zaznaczono checkbox pracownik
        :param state: status pola pracownik
        """
        if state == Qt.Checked:
            self.group_box_dni.setVisible(True)
        else:
            self.group_box_dni.setVisible(False)

    def table_init(self):
        """
        Inicjuje wygląd tabeli
        """
        self.model.setTable('uzytkownik')
        query = QSqlQuery('SELECT uzytkownik_id, uzytkownik_nazwa, imie, nazwisko, pracownik FROM uzytkownik;')
        self.model.setQuery(query)

        self.proxy.setSourceModel(self.model)

        naglowki = {
            'uzytkownik_id': 'ID',
            'uzytkownik_nazwa': 'Login',
            'imie': 'Imię',
            "nazwisko": 'Nazwisko',
            'pracownik': 'Pracownik',
        }
        # Ustawianie nagłówków
        ilosc_kolumn = self.model.columnCount()
        for i in range(ilosc_kolumn):
            nazwa_kolumn = self.model.headerData(i, Qt.Horizontal)
            self.model.setHeaderData(i, Qt.Horizontal, naglowki[nazwa_kolumn])

        # TODO Poprawić wiywietlanie kolumny Pracownik
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
        if len(self.txt_imie.text()) < 2 or len(self.txt_nazwisko.text()) < 2 or len(self.txt_login.text()) < 5:
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

    def employee_type(self):
        """
        Sprawdza, czy dana osoba jest pracownikiem, czy nie.
        :return: int Pracownik
        """
        return 1 if self.cb_pracownik.checkState() else 0

    def add(self):
        """
        Dodaje nową osobę do bazy danych i odświeża widok.
        """
        tekst = "Dane zostały błędnie wprowadzone.\nLogin musi mieć minimum 5 znaków."

        # Dodanie nowego użytkownika
        query1 = 'INSERT INTO uzytkownik (imie, nazwisko, uzytkownik_nazwa, haslo, pracownik) VALUES (%s, %s, %s, ' \
                 'sha(%s), %s)'
        val1 = (
            self.txt_imie.text(),
            self.txt_nazwisko.text(),
            self.txt_login.text(),
            self.txt_login.text(),
            self.employee_type()
        )

        # Dodanie godzin do pracownika
        if self.cb_pracownik.checkState():
            query2 = 'INSERT INTO godziny (uzytkownik_id, pon_od, pon_do, wt_od, wt_do, sr_od, sr_do, czw_od, czw_do, pt_od, pt_do, sob_od, sob_do) VALUES (LAST_INSERT_ID(),"' + self.txt_pon_od.text() + '","' + self.txt_pon_do.text() + '","' + self.txt_wt_od.text() + '","' + self.txt_wt_do.text() + '","' + self.txt_sr_od.text() + '","' + self.txt_sr_do.text() + '","' + self.txt_czw_od.text() + '","' + self.txt_czw_do.text() + '","' + self.txt_pt_od.text() + '","' + self.txt_pt_do.text() + '","' + self.txt_sob_od.text() + '","' + self.txt_sob_do.text() + '");'
            val2 = None
        else:
            query2 = None
            val2 = None

        if self.if_checked(tekst, [(query1, val1), (query2, val2)]):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setText('Dodano nowego użytkownika')
            msg.setWindowTitle("Dodano użytkownika")
            msg.exec_()

    def modify(self):
        """
        Modyfikuje bazę danych
        """
        query = 'SELECT * FROM godziny WHERE uzytkownik_id = %s'
        val = (self.id_modify,)
        wynik = polaczenie(query, val)

        test = 'Dane zostały błędnie zmodyfikowane.'
        query = 'UPDATE uzytkownik SET imie = %s, nazwisko = %s, uzytkownik_nazwa = %s, ' \
                'pracownik = %s WHERE uzytkownik_id = %s'
        val = (
            self.txt_imie.text(),
            self.txt_nazwisko.text(),
            self.txt_login.text(),
            self.employee_type(),
            self.id_modify
        )
        self.if_checked(test, query, val)

        if wynik and self.cb_pracownik.checkState():
            query = 'UPDATE godziny SET pon_od = %s, pon_do = %s, wt_od = %s, wt_do = %s, sr_od = %s, sr_do = %s, ' \
                    'czw_od = %s, czw_do = %s, pt_od = %s, pt_do = %s, sob_od = %s, sob_do = %s WHERE uzytkownik_id = %s;'
            val = (
                self.txt_pon_od.text(),
                self.txt_pon_do.text(),
                self.txt_wt_od.text(),
                self.txt_wt_do.text(),
                self.txt_sr_od.text(),
                self.txt_sr_do.text(),
                self.txt_czw_od.text(),
                self.txt_czw_do.text(),
                self.txt_pt_od.text(),
                self.txt_pt_do.text(),
                self.txt_sob_od.text(),
                self.txt_sob_do.text(),
                self.id_modify
            )
            polaczenie(query, val)
        elif self.cb_pracownik.checkState():
            query = 'INSERT INTO godziny SET uzytkownik_id = %s, pon_od = %s, pon_do = %s, wt_od = %s, wt_do = %s, ' \
                    'sr_od = %s, ' \
                    'sr_do = %s, ' \
                    'czw_od = %s, czw_do = %s, pt_od = %s, pt_do = %s, sob_od = %s, sob_do = %s; '
            val = (
                self.id_modify,
                self.txt_pon_od.text(),
                self.txt_pon_do.text(),
                self.txt_wt_od.text(),
                self.txt_wt_do.text(),
                self.txt_sr_od.text(),
                self.txt_sr_do.text(),
                self.txt_czw_od.text(),
                self.txt_czw_do.text(),
                self.txt_pt_od.text(),
                self.txt_pt_do.text(),
                self.txt_sob_od.text(),
                self.txt_sob_do.text()
            )
            polaczenie(query, val)
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText('Zmodyfikowano dane użytkownika')
        msg.setWindowTitle("Zmodyfikowano użytkownika")
        msg.exec_()

    def remove(self):
        """
        Usuwa dane z bazy danych
        """
        test = 'Błąd! Nie można usunąć danego użytkownika!'
        query1 = 'DELETE FROM uzytkownik WHERE uzytkownik_id = %s'
        val1 = (self.id_modify,)
        query2 = 'DELETE FROM godziny WHERE uzytkownik_id = %s'
        val2 = (self.id_modify,)
        if self.id_modify == 1:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Błąd! Nie można usunąć domyślnego użytkownika')
            msg.setWindowTitle("Popraw dane")
            msg.exec_()
        else:
            ret = QMessageBox.question(self, 'Usuwanie użytkownika', "Czy na pewno chcesz usunąć danego użytkownika?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ret == QMessageBox.Yes:
                if self.if_checked(test, [(query2, val2), (query1, val1)]):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText('Użytkownik został usunięty')
                    msg.setWindowTitle("Usunięto")
                    msg.exec_()

                    self.txt_imie.setText('')
                    self.txt_login.setText('')
                    self.txt_nazwisko.setText('')
                    if self.cb_pracownik.checkState():
                        self.cb_pracownik.toggle()

    def change(self):
        """
        Metoda edytująca zaznaczone wiersze - Wstawia wartości z wierszy w odpowiednie pola
        """
        index = (self.view.selectionModel().currentIndex())
        value = index.sibling(index.row(), index.column()).data()
        self.id_modify = index.sibling(index.row(), 0).data()
        self.txt_imie.setText(index.sibling(index.row(), 2).data())
        self.txt_nazwisko.setText(index.sibling(index.row(), 3).data())
        self.txt_login.setText(index.sibling(index.row(), 1).data())

        if self.id_modify >= 0 and self.txt_imie.text() and self.txt_login.text() and self.txt_nazwisko.text():
            self.btn_modyfikuj.setEnabled(True)
            self.btn_usun.setEnabled(True)
        else:
            self.btn_usun.setDisabled(True)
            self.btn_modyfikuj.setDisabled(True)
        if index.sibling(index.row(), 4).data() == 1:
            if not self.cb_pracownik.checkState():
                self.cb_pracownik.toggle()
        else:
            if self.cb_pracownik.checkState():
                for value in self.pola:
                    value.setText('')
                self.cb_pracownik.toggle()

        if self.cb_pracownik.checkState():
            query = 'SELECT * FROM godziny WHERE uzytkownik_id = %s'
            val = (self.id_modify,)
            wynik = polaczenie(query, val)
            for i, value in enumerate(self.pola, 2):
                if wynik:
                    value.setText(str(wynik[i]))
                else:
                    value.setText('')

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
    ex = Employee(Program, db)
    ex.setFixedSize(1000, 600)
    Program.show()
    sys.exit(app.exec_())
