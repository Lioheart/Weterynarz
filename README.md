# Weterynarz
Projekt programu obsługującego bazy danych na zaliczenie.

Login:  admin

Hasło:  123
### Instalacja
Aby zainstalować program, wystarczy pobrać plik [setup.exe](https://github.com/Lioheart/Weterynarz/releases/latest)
### Uruchomienie ze źródeł
W przypadku chęci uruchomienia ze źródeł, należe zainstalować Python conajmniej w wersji 3.7.5 oraz git.
* Należy pobrać repozytorium, wpisując w terminal komendę `git clone https://github.com/Lioheart/Weterynarz.git`
* Następnie przechodzimy do katalogu `cd .\Weterynarz`
* W danym folderze uruchamiamy komendę, aby zainicjować utworzenie venv `python3 -m venv venv`
* Następnie tworzymy venv za pomocą komendy `virtualenv venv`
* Należy teraz aktywować venv za pomocą komendy (tylko linux i macOS) `source venv/bin/activate`
- **W przypadku systemu Windows:**
    - Uruchom Windows PowerShell w trybie administratora i wprowadź poniższą komendę, zgadzając się na zmiany `Set-ExecutionPolicy RemoteSigned`
    - Następnie uruchom Windows PowerShell bez uprawnień, przejdź do katalogu z projektem, po czym użyj komendy `venv\Scripts\activate`
    - Przejdź ponownie do Windows PowerShell w trybie administratora i wycofaj zmiany, za pomocą komendy `Set-ExecutionPolicy Restricted`   
* Zainstaluj niezbędne pakiety używając komendy `python setup.py install`
* Ostatnią rzeczą jaką należy wykonać, to skopiować plik sip za pomocą poniższej komendy. Jest to potrzebne, ze wzgl
ędu na to, że na Windows 10 nie istaluje się poprawnie PyQt5.
`copy .\venv\Lib\site-packages\PyQt5_sip-12.7.2-py3.7-win-amd64.egg\PyQt5\sip.cp37-win_amd64.pyd .\venv\Lib\site-packages\PyQt5-5.13.1-py3.7-win-amd64.egg\PyQt5\`
* Uruchom `python main.py`