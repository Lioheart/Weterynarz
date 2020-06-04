# Weterynarz
Projekt programu obsługującego bazy danych na zaliczenie.

Login:  admin

Hasło:  123
### Instalacja
Aby zainstalować program, wystarczy pobrać plik [setup.exe](https://github.com/Lioheart/Weterynarz/releases/latest)

**Koniecznie** trzeba zainstalować najnowszy [pakiet redystrybucyjny Microsoft Visual C++ dla programu Visual Studio
 2015, 2017 i 2019](https://support.microsoft.com/pl-pl/help/2977003/the-latest-supported-visual-c-downloads)
 
### Uruchomienie ze źródeł
W przypadku chęci uruchomienia ze źródeł, należe zainstalować [Python](https://www.python.org/downloads/) w wersji co
  najmniej 3.7.5 (koniecznie zaznacz pole add to PATH), oraz [git](https://git-scm.com/downloads).
* Aby uruchomić PowerShell w systemie Windows 10, kliknij prawym przyciskiem myszy w start, następnie wybierz
  Program Windows PowerShell.
* Należy pobrać repozytorium, wpisując w terminal komendę `git clone https://github.com/Lioheart/Weterynarz.git`
* Następnie przechodzimy do katalogu`cd Weterynarz` lub dla PowerShell `cd .\Weterynarz`
 * Uruchom drugie okno konsoli lub PowerShella w trybie administratora.
 * Zainstaluj paczkę (tylko z uprawnieniami administratora), dzięki której utworzysz wirtualne środowisko `pip install
  virtualenv`
 * Przejdź do pierwszego okna i utwórz virtual env za pomocą komendy `virtualenv venv`
 * Należy teraz aktywować virtual env za pomocą komendy (tylko linux i macOS) `source venv/bin/activate`
 * W przypadku, gdy używamy konsoli cmd Microsoft Windows należy użyć komendy `venv\Scripts\activate`
 
 
W momencie utworzenia folderu venv i zainstalowania niezbędnych paczek, należy:
* Pobrać plik z poniższego linku `https://github.com/thecodemonkey86/qt_mysql_driver/releases/tag/qmysql_5.13.1`
* Rozpakować plik. Po rozpakowaniu powinniśmy mieć folder sqldrivers oraz plik libmysql.dll
* Folder sqldrivers umieścić w lokalizacji `.\venv\Lib\site-packages\PyQt5\Qt\plugins`
* Plik libmysql.dll umieszczamy w katalogu głównym (jeśli nie było)
* Należy też upewnić się, czy mamy zainstalowany MySQL C Connector v6.1 `https://downloads.mysql.com/archives/c-c/?version=6.1.11&amp;os=src`
 
- **W przypadku systemu Windows:**
    - Uruchom Windows PowerShell w trybie administratora i wprowadź poniższą komendę, zgadzając się na zmiany `Set-ExecutionPolicy RemoteSigned`
    - Następnie przejdź do okna Windows PowerShell, w którym wykonywałeś poprzednie polecenia, przejdź do katalogu z
  projektem, po czym użyj komendy `venv\Scripts\activate`
    - Przejdź ponownie do Windows PowerShell w trybie administratora i wycofaj zmiany, za pomocą komendy `Set-ExecutionPolicy Restricted`   
* Zainstaluj niezbędne pakiety używając komendy `python setup.py install`
* Ostatnią rzeczą jaką należy wykonać, to skopiować plik sip za pomocą poniższej komendy. Jest to potrzebne, ze wzgl
ędu na to, że na Windows 10 nie istaluje się poprawnie PyQt5.
`copy .\venv\Lib\site-packages\PyQt5_sip-12.7.2-py3.7-win-amd64.egg\PyQt5\sip.cp37-win_amd64.pyd .\venv\Lib\site-packages\PyQt5-5.13.1-py3.7-win-amd64.egg\PyQt5\`
* Uruchom `python main.py`