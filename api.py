import sqlite3
import json

class API():
    def __init__(self, nazwa_pliku: str = "data.db"):
        self.nazwa_pliku = nazwa_pliku
        self._utworz_tabele()

    def _polaczenie(self):
        conn = sqlite3.connect(self.nazwa_pliku)
        conn.row_factory = sqlite3.Row
        return conn

    def _utworz_tabele(self):
        with self._polaczenie() as conn:
            cursor = conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS "Czolg" (
                    "IDC"	INTEGER NOT NULL UNIQUE,
                    "Nazwa"	TEXT NOT NULL UNIQUE,
                    "Wyprodukowano"	INTEGER,
                    PRIMARY KEY("IDC" AUTOINCREMENT)
                );

                CREATE TABLE IF NOT EXISTS "Klient" (
                    "IDK"	INTEGER NOT NULL UNIQUE,
                    "Nazwa"	TEXT NOT NULL UNIQUE,
                    "Wydatki"	INTEGER NOT NULL,
                    PRIMARY KEY("IDK" AUTOINCREMENT)
                );

                CREATE TABLE IF NOT EXISTS Zamowienia (
                    "IDZ"         INTEGER PRIMARY KEY AUTOINCREMENT,
                    "Klient_ID"  INTEGER NOT NULL,
                    "Czolg_ID"	INTEGER NOT NULL,
                    "Ilosc"	INTEGER NOT NULL,
                    "Dostarczono"	INTEGER NOT NULL,
                    "Kwota"      INTEGER NOT NULL,
                    FOREIGN KEY (Klient_ID)
                        REFERENCES Klient(IDK)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE,

                    FOREIGN KEY (Czolg_ID)
                        REFERENCES Czolg(IDC)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                );
            """)
            conn.commit()

    def nowy_klient(self, nazwa: str) -> None:
        with self._polaczenie() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO Klient (Nazwa, Wydatki) VALUES (?, ?)""",
                (nazwa, 0)
            )
            conn.commit()

    def nowy_czolg(self, nazwa: str) -> None:
        with self._polaczenie() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO Czolg (Nazwa, Wyprodukowano) VALUES (?, ?)""",
                (nazwa, 0)
            )
            conn.commit()

    def zamow(self, klient_ID: int, czolg_ID: int, ilosc: int, kwota: int,) -> None:
        with self._polaczenie() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO Zamowienia (Klient_ID, Czolg_ID, Ilosc, Dostarczono,Kwota) VALUES (?, ?, ?, ?, ?);""",
                (klient_ID, czolg_ID, ilosc, 0, kwota)
            )
            cursor.execute(
                """UPDATE Klient
                SET Wydatki = Wydatki + (?)
                WHERE IDK = (?)""",
                (kwota,klient_ID)
            )
            conn.commit()
    
    def zatrzyj_slad(self, idZ: int) -> None:
        with self._polaczenie()as con:
            cursor = con.cursor()
            cursor.execute("""
                DELETE FROM Zamowienia
                WHERE IDZ = ? 
            """, (idZ,))
            con.commit()

    def realizuj(self, zamowienie_ID: int, ilosc: int) -> None:
        with self._polaczenie() as con:
            cursor = con.cursor()
            cursor.execute("""
            UPDATE Zamowienia
            SET Dostarczono = Dostarczono + (?)
            WHERE IDZ = (?)
            """, (ilosc, zamowienie_ID,))

            cursor.execute("""
                SELECT Czolg_ID
                FROM Zamowienia
                WHERE IDZ = (?)""",
                (zamowienie_ID,))
            cursor.execute("""
                UPDATE Czolg
                SET Wyprodukowano = Wyprodukowano + (?)
                WHERE IDC = (?)""",
                (ilosc,dict(cursor.fetchone())["Czolg_ID"],))

            con.commit()

    def inf_klient(self, klient_ID:int) -> dict:
        with self._polaczenie()as con:
            cursor = con.cursor()
            cursor.execute("""
                SELECT Nazwa, Wydatki
                FROM Klient
                WHERE IDK = ? 
            """, (klient_ID,))
            return(dict(cursor.fetchone()))

    def list_zamowienia_klienta(self, klient_id: int) -> list[dict]:
        with self._polaczenie() as con:
            cursor = con.cursor()
            cursor.execute("""
                SELECT IDZ, Nazwa, Ilosc, Dostarczono, Kwota
                FROM Zamowienia, Czolg
                WHERE Klient_ID = ? AND IDC = Czolg_ID
            """, (klient_id,))
            return [dict(r) for r in cursor.fetchall()]

    def inf_czołg(self, czolg_ID: int) -> dict:
        with self._polaczenie()as con:
            cursor = con.cursor()
            cursor.execute("""
                SELECT Nazwa, Wyprodukowano
                FROM Czolg
                WHERE IDC = ? 
            """, (czolg_ID,))
            return(dict(cursor.fetchone()))

    def saveDB(self, filePath: str = "data.json") -> None:
        KlientData = None
        ZamowieniaData = None
        CzolgData = None

        with self._polaczenie()as con:
            cursor = con.cursor()
            cursor.execute("""SELECT IDK, Nazwa, Wydatki FROM Klient""")
            KlientData = [dict(r) for r in cursor.fetchall()]

            cursor.execute("""SELECT IDZ, Klient_ID, Czolg_ID, Ilosc, Dostarczono, Kwota FROM Zamowienia""")
            ZamowieniaData = [dict(r) for r in cursor.fetchall()]

            cursor.execute("""SELECT IDC, Nazwa, Wyprodukowano FROM Czolg""")
            CzolgData = [dict(r) for r in cursor.fetchall()]

        data = {
            "Klient" : KlientData,
            "Zamowienia" : ZamowieniaData,
            "Czolg" : CzolgData
        }
        with open(filePath, "w") as file:
            json.dump(data, file, indent=4)

    def loadDB(self, restartDB = True, filePath: str = "data.json") -> None:
        with open(filePath, "r") as file:
            data = json.load(file)

        KlientData = data["Klient"]
        ZamowieniaData = data["Zamowienia"]
        CzolgData = data["Czolg"]

        with self._polaczenie()as con:
            cursor = con.cursor()

            if restartDB == True:   #SCARY!!!
                cursor.executescript("""
                DELETE FROM Klient;
                DELETE FROM Zamowienia;
                DELETE FROM Czolg
                """)

            for dK in KlientData:
                try:
                    cursor.execute("""
                    INSERT INTO Klient (IDK, Nazwa, Wydatki) VALUES (?, ?, ?)""",
                    (dK["IDK"],dK["Nazwa"],dK["Wydatki"]))
                    con.commit()
                except: print("error: ID sie powtarza")
            
            for dC in CzolgData:
                try:
                    cursor.execute("""
                    INSERT INTO Czolg (IDC, Nazwa, Wyprodukowano) VALUES (?, ?, ?)""",
                    (dC["IDC"],dC["Nazwa"],dC["Wyprodukowano"]))
                    con.commit()
                except: print("error: ID sie powtarza")

            for dZ in ZamowieniaData:
                try:
                    cursor.execute("""
                    INSERT INTO Zamowienia (IDZ, Klient_ID, Czolg_ID, Ilosc, Dostarczono, Kwota) VALUES (?, ?, ?, ?, ?, ?)""",
                    (dZ["IDZ"], dZ["Klient_ID"], dZ["Czolg_ID"], dZ["Ilosc"], dZ["Dostarczono"], dZ["Kwota"]))
                    con.commit()
                except: print("error: ID sie powtarza")
