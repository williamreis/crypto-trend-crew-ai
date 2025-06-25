import streamlit as st
import sqlite3
import os
from datetime import datetime, timedelta

# Caminho do banco de dados
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/crypto_trend.db'))


# Função para rodar o pipeline CrewAI
def rodar_crew():
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../project/src')))
    from project.crew import CryptoTrendCrew
    crew = CryptoTrendCrew().crew().kickoff()


# Botão para executar os agentes
st.sidebar.title('Execução do Pipeline')
if st.sidebar.button('Executar Análise Multiagente'):
    with st.spinner('Executando agentes do CrewAI...'):
        rodar_crew()
    st.success('Execução concluída! Atualize os painéis para ver os novos resultados.')


def get_connection():
    return sqlite3.connect(DB_PATH)


def ensure_tables():
    """Cria as tabelas se não existirem"""
    conn = get_connection()
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


def get_moedas():
    try:
        ensure_tables()
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT symbol, name, price, date FROM moedas ORDER BY date DESC LIMIT 50")
        data = c.fetchall()
        conn.close()
        return data
    except Exception as e:
        st.error(f"Erro ao buscar moedas: {e}")
        return []


def get_sentimentos():
    try:
        ensure_tables()
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT symbol, sentiment, score, date FROM sentimento ORDER BY date DESC LIMIT 50")
        data = c.fetchall()
        conn.close()
        return data
    except Exception as e:
        st.error(f"Erro ao buscar sentimentos: {e}")
        return []


def get_tendencias():
    try:
        ensure_tables()
        # Exemplo simples: moedas com score de sentimento > 0.5
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT symbol, AVG(score) as avg_score FROM sentimento WHERE date >= ? GROUP BY symbol ORDER BY avg_score DESC LIMIT 10",
            ((datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),))
        data = c.fetchall()
        conn.close()
        return data
    except Exception as e:
        st.error(f"Erro ao buscar tendências: {e}")
        return []


st.set_page_config(page_title="Crypto Trend Crew Dashboard", layout="wide")
st.title("📈 Crypto Trend Crew - Dashboard de Tendências")

st.header("Top 50 Moedas em Evidência (últimas 24h)")
moedas = get_moedas()
if moedas:
    st.dataframe([
        {"Símbolo": m[0], "Nome": m[1], "Preço (USD)": m[2], "Data": m[3]} for m in moedas
    ])
else:
    st.info("Nenhuma moeda encontrada no banco de dados. Execute o pipeline primeiro!")

st.header("Análise de Sentimento (últimas 24h)")
sentimentos = get_sentimentos()
if sentimentos:
    st.dataframe([
        {"Símbolo": s[0], "Sentimento": s[1], "Score": s[2], "Data": s[3]} for s in sentimentos
    ])
else:
    st.info("Nenhuma análise de sentimento encontrada. Execute o pipeline primeiro!")

st.header("Tendências de Alta (baseado em sentimento)")
tendencias = get_tendencias()
if tendencias:
    st.dataframe([
        {"Símbolo": t[0], "Score Médio": t[1]} for t in tendencias
    ])
else:
    st.info("Nenhuma tendência detectada. Execute o pipeline primeiro!")

st.markdown("---")
st.subheader("Recomendações e Conclusões")
st.write("As recomendações e conclusões são geradas automaticamente pelo sistema multiagente com base nos dados mais recentes.")
