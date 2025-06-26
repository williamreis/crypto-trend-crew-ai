import sqlite3
import os
import json
import ast
from crewai.tools import BaseTool
from datetime import datetime
from typing import Type
from pydantic import BaseModel, Field


class SQLiteToolInput(BaseModel):
    """
    Argumentos de entrada para a ferramenta CoinGecko
    """
    action: str = Field(description="Ação a ser executada no banco SQLite. Use 'save_moedas' para salvar dados de moedas, 'save_sentimento' para sentimentos, ou 'query' para consultas SQL.")
    data: str = Field(default=None, description="Dados a serem processados pela ação. Pode ser uma string JSON ou texto formatado.")


class SQLiteTool(BaseTool):
    name: str = "SQLite Tool"
    description: str = "Persiste e consulta dados em um banco SQLite local. Use 'save_moedas' para salvar dados de moedas, 'save_sentimento' para sentimentos, ou 'query' para consultas SQL."
    args_schema: Type[BaseTool] = SQLiteToolInput

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
            print(f"SQLiteTool: Executando ação '{action}' com dados: {data[:200] if data else 'None'}...")

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
            print(f"Erro no SQLiteTool: {e}")
            return f"Erro no SQLite: {e}"

    def _save_moedas(self, data_str: str) -> str:
        try:
            if not data_str:
                return "Nenhum dado fornecido para salvar moedas"
            print(f"Processando dados de moedas: {data_str[:500]}...")
            # Tentar processar como JSON
            data = None
            try:
                data = json.loads(data_str)
            except Exception:
                try:
                    data = ast.literal_eval(data_str)
                except Exception:
                    data = None
            if isinstance(data, dict) and 'coins' in data:
                data = data['coins']
            if isinstance(data, list):
                return f"Salvas {self._save_moedas_from_json(data)} moedas no banco de dados (formato lista)."
            # Processar como texto (formato: "BTC - Bitcoin ($45000)")
            lines = data_str.strip().split('\n')
            saved_count = 0
            conn = sqlite3.connect(self._db_path)
            c = conn.cursor()
            for line in lines:
                line = line.strip()
                if not line or line.startswith('Top 50') or line.startswith('#'):
                    continue
                print(f"Processando linha: {line}")
                if ' - ' in line and '$' in line:
                    parts = line.split(' - ')
                    if len(parts) >= 2:
                        symbol = parts[0].strip()
                        name_price = parts[1].strip()
                        if '(' in name_price and ')' in name_price:
                            name = name_price.split('(')[0].strip()
                            price_str = name_price.split('(')[1].split(')')[0].replace('$', '').replace(',', '')
                            try:
                                price = float(price_str)
                                c.execute('''INSERT INTO moedas (symbol, name, price, date) 
                                           VALUES (?, ?, ?, ?)''',
                                          (symbol, name, price, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                                saved_count += 1
                                print(f"Salvou: {symbol} - {name} (${price})")
                            except ValueError as ve:
                                print(f"Erro ao converter preço '{price_str}' para {symbol}: {ve}")
                                continue
            conn.commit()
            conn.close()
            print(f"Total de moedas salvas: {saved_count}")
            return f"Salvas {saved_count} moedas no banco de dados."
        except Exception as e:
            print(f"Erro ao salvar moedas: {e}")
            return f"Erro ao salvar moedas: {e}"

    def _save_moedas_from_json(self, data_json: list) -> int:
        """Salva moedas a partir de dados JSON"""
        saved_count = 0
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()

        for coin in data_json:
            try:
                # Mapear campos dos dados recebidos para as colunas da tabela
                symbol = coin.get('simbolo', coin.get('symbol', '')).upper()
                name = coin.get('nome', coin.get('name', ''))

                # Tentar extrair preço de diferentes campos
                price = 0.0
                if 'market_cap' in coin and coin['market_cap'] != 'N/A':
                    try:
                        price_str = str(coin['market_cap']).replace('$', '').replace(',', '')
                        price = float(price_str)
                    except:
                        price = 0.0
                elif 'current_price' in coin:
                    price = float(coin['current_price'])

                # Extrair variação percentual se disponível
                change_24h = 0.0
                if 'variacao_percentual_24h' in coin:
                    try:
                        change_str = str(coin['variacao_percentual_24h']).replace('%', '')
                        change_24h = float(change_str)
                    except:
                        change_24h = 0.0
                elif 'price_change_percentage_24h' in coin:
                    change_24h = float(coin['price_change_percentage_24h'])

                # Extrair volume se disponível
                volume = 0.0
                if 'volume_negociacao' in coin and coin['volume_negociacao'] != 'N/A':
                    try:
                        volume_str = str(coin['volume_negociacao']).replace('$', '').replace(',', '')
                        volume = float(volume_str)
                    except:
                        volume = 0.0
                elif 'total_volume' in coin:
                    volume = float(coin['total_volume'])

                if symbol and name:
                    c.execute('''INSERT INTO moedas (symbol, name, price, volume, change_24h, date) 
                               VALUES (?, ?, ?, ?, ?, ?)''',
                              (symbol, name, price, volume, change_24h, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    saved_count += 1
                    print(f"Salvou JSON: {symbol} - {name} (${price}, {change_24h}%)")
            except Exception as e:
                print(f"Erro ao salvar moeda JSON {coin}: {e}")
                continue

        conn.commit()
        conn.close()
        return saved_count

    def _save_sentimento(self, data_str: str) -> str:
        try:
            if not data_str:
                return "Nenhum dado fornecido para salvar sentimento"

            print(f"Processando dados de sentimento: {data_str[:500]}...")

            # Parsear dados de sentimento (formato: "Notícias recentes sobre BTC: - título1 - título2")
            lines = data_str.strip().split('\n')
            symbol = "UNKNOWN"
            news_count = 0

            # Extrair símbolo da primeira linha
            if lines and 'sobre' in lines[0]:
                symbol_part = lines[0].split('sobre')
                if len(symbol_part) > 1:
                    symbol = symbol_part[1].split(':')[0].strip()

            # Contar notícias
            news_count = len([line for line in lines if line.strip().startswith('-')])

            # Calcular score simples baseado na quantidade de notícias
            score = min(news_count * 0.1, 1.0)  # Score de 0 a 1 baseado na quantidade de notícias
            sentiment = "positivo" if score > 0.5 else "neutro" if score > 0.2 else "negativo"

            print(f"Salvando sentimento para {symbol}: {sentiment} (score: {score:.2f}, {news_count} notícias)")

            conn = sqlite3.connect(self._db_path)
            c = conn.cursor()
            c.execute('''INSERT INTO sentimento (symbol, sentiment, score, news_count, date) 
                       VALUES (?, ?, ?, ?, ?)''',
                      (symbol, sentiment, score, news_count, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            conn.close()

            return f"Salvo sentimento para {symbol}: {sentiment} (score: {score:.2f}, {news_count} notícias)"

        except Exception as e:
            print(f"Erro ao salvar sentimento: {e}")
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
            return f"Moedas encontradas: {len(result)}\n" + "\n".join(
                [f"{r[0]} - {r[1]} (${r[2]}) - {r[3]}" for r in result])
        except Exception as e:
            return f"Erro ao buscar moedas: {e}"

    def _get_sentimentos(self) -> str:
        try:
            conn = sqlite3.connect(self._db_path)
            c = conn.cursor()
            c.execute("SELECT symbol, sentiment, score, news_count, date FROM sentimento ORDER BY date DESC LIMIT 50")
            result = c.fetchall()
            conn.close()
            return f"Sentimentos encontrados: {len(result)}\n" + "\n".join(
                [f"{r[0]} - {r[1]} (score: {r[2]:.2f}, {r[3]} notícias) - {r[4]}" for r in result])
        except Exception as e:
            return f"Erro ao buscar sentimentos: {e}"
