"""
Plik konfiguracyjny bazy danych oraz funkcje, za pomocą których nastąpi połączenie.
"""
import mysql.connector

HOST = 'remotemysql.com'
USER = 'NC6H7fYEuE'
PASSWORD = 'blQCzhy3Dn'

query = "SELECT * FROM uzytkownik WHERE uzytkownik_nazwa = '{}' AND haslo = sha({}) ;".format('admin', '123')


def polaczenie(q, sqlinjection=None):
    """
    Funkcja wykonująca jedno zapytanie na bazie danych
    :param sqlinjection: String dane
    :param q: Query MySQL
    :return: Wartość z bazy danych
    """
    mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        passwd=PASSWORD,
        database="NC6H7fYEuE"
    )

    mycursor = mydb.cursor()
    try:
        if sqlinjection:
            mycursor.execute(q, sqlinjection)
        else:
            mycursor.execute(q)
        print('Wykonano')
    except (mysql.connector.errors.ProgrammingError, mysql.connector.errors.Error):
        mydb.rollback()
        mycursor.close()
        mydb.close()
        return None

    myresult = mycursor.fetchone()
    if 'UPDATE' in q:
        myresult = mycursor.rowcount

    mycursor.close()
    mydb.commit()
    mydb.close()
    print("Zamknięto połączenie")

    if 'SELECT' in q:
        return myresult
    else:
        return True


def transakcja(*args):
    """
    Funkcja wykonująca transakcje na bazie danych (czyli kilka query naraz)
    :param args:
    """
    try:
        mydb = mysql.connector.connect(
            host=HOST,
            user=USER,
            passwd=PASSWORD,
            database="NC6H7fYEuE"
        )
        mydb.autocommit = False
        mycursor = mydb.cursor()
        for q, sqlinjection in args[0]:
            if sqlinjection:
                mycursor.execute(q, sqlinjection)
            else:
                mycursor.execute(q)
            print('Wykonano transakcję')
            flag = True
        mydb.commit()
    except mysql.connector.Error as err:
        print("Błąd update bazy danych: {}".format(err))
        mydb.rollback()
        flag = False
    finally:
        if (mydb.is_connected()):
            mycursor.close()
            mydb.close()
            print("Zamknięto połączenie")
    return flag


if __name__ == '__main__':
    print(polaczenie(query))
    print(query)
