from crewai.tools import BaseTool
import sqlite3
import os
from datetime import datetime

class SQLiteTool(BaseTool):
    name: str = "SQLite Tool"
    description: str = "Persiste e consulta dados em um banco SQLite local. Use 'save_moedas' para salvar dados de moedas, 'save_sentimento' para sentimentos, ou 'query' para consultas SQL."

    def __init__(self, db_path=None):
        super().__init__()
        self._db_path = db_path or os.path.join(os.path.dirname(__file__), '../../../../data/crypto_trend.db')
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._ensure_tables()

    def _ensure_tables(self):
        try:
            conn = sqlite3.connect(self._db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS moedas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                name TEXT,
                price REAL,
                volume REAL,
                change_24h REAL,
                date TEXT
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS sentimento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                sentiment TEXT,
                score REAL,
                news_count INTEGER,
                date TEXT
            )''')
            conn.commit()
            conn.close()
            print(f"Banco SQLite inicializado em: {self._db_path}")
        except Exception as e:
            print(f"Erro ao inicializar banco SQLite: {e}")

    def _run(self, action: str, data: str = None) -> str:
        try:
            if action.lower() == "save_moedas":
                return self._save_moedas(data)
            elif action.lower() == "save_sentimento":
                return self._save_sentimento(data)
            elif action.lower() == "query":
                return self._execute_query(data)
            elif action.lower() == "get_moedas":
                return self._get_moedas()
            elif action.lower() == "get_sentimentos":
                return self._get_sentimentos()
            else:
                return f"Ação '{action}' não suportada. Use: save_moedas, save_sentimento, query, get_moedas, get_sentimentos"
        except Exception as e:
            return f"Erro no SQLite: {e}"

    def _save_moedas(self, data_str: str) -> str:
        try:
            # Parsear dados das moedas (formato: "BTC - Bitcoin ($45000)")
            lines = data_str.strip().split('\n')
            saved_count = 0
            
            conn = sqlite3.connect(self._db_path)
            c = conn.cursor()
            
            for line in lines:
                if ' - ' in line and '$' in line:
                    # Extrair informações da linha
                    parts = line.split(' - ')
                    symbol = parts[0].strip()
                    name_price = parts[1].strip()
                    
                    # Extrair nome e preço
                    if '(' in name_price and ')' in name_price:
                        name = name_price.split('(')[0].strip()
                        price_str = name_price.split('(')[1].split(')')[0].replace('$', '').replace(',', '')
                        try:
                            price = float(price_str)
                        except:
                            price = 0.0
                        
                        # Salvar no banco
                        c.execute('''INSERT INTO moedas (symbol, name, price, date) 
                                   VALUES (?, ?, ?, ?)''', 
                                   (symbol, name, price, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        saved_count += 1
            
            conn.commit()
            conn.close()
            return f"Salvas {saved_count} moedas no banco de dados."
            
        except Exception as e:
            return f"Erro ao salvar moedas: {e}"

    def _save_sentimento(self, data_str: str) -> str:
        try:
            # Parsear dados de sentimento (formato: "Notícias recentes sobre BTC: - título1 - título2")
            lines = data_str.strip().split('\n')
            symbol = "UNKNOWN"
            news_count = 0
            
            # Extrair símbolo da primeira linha
            if lines and 'sobre' in lines[0]:
                symbol = lines[0].split('sobre')[1].split(':')[0].strip()
            
            # Contar notícias
            news_count = len([line for line in lines if line.strip().startswith('-')])
            
            # Calcular score simples baseado na quantidade de notícias
            score = min(news_count * 0.1, 1.0)  # Score de 0 a 1 baseado na quantidade de notícias
            sentiment = "positivo" if score > 0.5 else "neutro" if score > 0.2 else "negativo"
            
            conn = sqlite3.connect(self._db_path)
            c = conn.cursor()
            c.execute('''INSERT INTO sentimento (symbol, sentiment, score, news_count, date) 
                       VALUES (?, ?, ?, ?, ?)''', 
                       (symbol, sentiment, score, news_count, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            conn.close()
            
            return f"Salvo sentimento para {symbol}: {sentiment} (score: {score:.2f}, {news_count} notícias)"
            
        except Exception as e:
            return f"Erro ao salvar sentimento: {e}"

    def _execute_query(self, query: str) -> str:
        try:
            conn = sqlite3.connect(self._db_path)
            c = conn.cursor()
            if query.lower().startswith('select'):
                c.execute(query)
                result = c.fetchall()
                conn.close()
                return str(result)
            else:
                c.execute(query)
                conn.commit()
                conn.close()
                return "Operação realizada com sucesso."
        except Exception as e:
            return f"Erro na query: {e}"

    def _get_moedas(self) -> str:
        try:
            conn = sqlite3.connect(self._db_path)
            c = conn.cursor()
            c.execute("SELECT symbol, name, price, date FROM moedas ORDER BY date DESC LIMIT 50")
            result = c.fetchall()
            conn.close()
            return f"Moedas encontradas: {len(result)}\n" + "\n".join([f"{r[0]} - {r[1]} (${r[2]}) - {r[3]}" for r in result])
        except Exception as e:
            return f"Erro ao buscar moedas: {e}"

    def _get_sentimentos(self) -> str:
        try:
            conn = sqlite3.connect(self._db_path)
            c = conn.cursor()
            c.execute("SELECT symbol, sentiment, score, news_count, date FROM sentimento ORDER BY date DESC LIMIT 50")
            result = c.fetchall()
            conn.close()
            return f"Sentimentos encontrados: {len(result)}\n" + "\n".join([f"{r[0]} - {r[1]} (score: {r[2]:.2f}, {r[3]} notícias) - {r[4]}" for r in result])
        except Exception as e:
            return f"Erro ao buscar sentimentos: {e}"
