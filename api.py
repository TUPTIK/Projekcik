import sqlite3

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
                "INSERT INTO Klient (Nazwa, Wydatki) VALUES (?, ?)",
                (nazwa, 0)
            )
            conn.commit()

    def nowy_czolg(self, nazwa: str) -> None:
        with self._polaczenie() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Czolg (Nazwa, Wyprodukowano) VALUES (?, ?)",
                (nazwa, 0)
            )
            conn.commit()

    def zamow(self, klient_ID: int, czolg_ID: int, ilosc: int, kwota: int,):
        with self._polaczenie() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Zamowienia (Klient_ID, Czolg_ID, Ilosc, Dostarczono,Kwota) VALUES (?, ?, ?, ?, ?)",
                (klient_ID, czolg_ID, ilosc, 0, kwota)
            )
            conn.commit()
    
    def list_zamowienia_klienta(self, klient_id: int) -> list[dict]:
        with self._polaczenie() as con:
            cursor = con.cursor()
            cursor.execute("""
                SELECT Nazwa, Ilosc, Dostarczono, Kwota
                FROM Zamowienia, Czolg
                WHERE Klient_ID = ? AND IDC = Czolg_ID
            """, (klient_id,))
            return [dict(r) for r in cursor.fetchall()]


    def realizuj(self):
        pass

    def inf_klient(self):
        pass

    def inf_czołg(self):
        pass


basa = API()

print(basa.list_zamowienia_klienta(1))

