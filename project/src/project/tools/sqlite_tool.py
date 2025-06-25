from crewai.tools import BaseTool
import sqlite3
import os

class SQLiteTool(BaseTool):
    name: str = "SQLite Tool"
    description: str = "Persiste e consulta dados em um banco SQLite local."

    def __init__(self, db_path=None):
        super().__init__()
        # Definir o caminho do banco como atributo da classe
        self._db_path = db_path or os.path.join(os.path.dirname(__file__), '../../../data/crypto_trend.db')
        self._ensure_tables()

    def _ensure_tables(self):
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS moedas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            name TEXT,
            price REAL,
            date TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS sentimento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            sentiment TEXT,
            score REAL,
            date TEXT
        )''')
        conn.commit()
        conn.close()

    def _run(self, query: str, params: dict = None) -> str:
        try:
            conn = sqlite3.connect(self._db_path)
            c = conn.cursor()
            if query.lower().startswith('select'):
                c.execute(query, params or {})
                result = c.fetchall()
                conn.close()
                return str(result)
            else:
                c.execute(query, params or {})
                conn.commit()
                conn.close()
                return "Operação realizada com sucesso."
        except Exception as e:
            return f"Erro no SQLite: {e}"
