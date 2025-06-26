import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class RetornaCoinGeckoToolInput(BaseModel):
    """
    Argumentos de entrada para a ferramenta CoinGecko
    """
    coin: str = Field(description="Selecionar a coin na Coingecko")


class CoinGeckoTool(BaseTool):
    name: str = "CoinGecko Tool"
    description: str = "Busca as 50 criptomoedas mais relevantes nas últimas 24h usando a API da CoinGecko."
    args_schema: Type[BaseTool] = RetornaCoinGeckoToolInput

    def _run(self, coin: str = None) -> str:
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'volume_desc',
                'per_page': 50,
                'page': 1,
                'sparkline': 'false'
            }
            response = requests.get(url, params=params)
            data = response.json()
            moedas = [f"{coin['symbol'].upper()} - {coin['name']} (${coin['current_price']})" for coin in data]
            return "Top 50 moedas nas últimas 24h:\n" + "\n".join(moedas)
        except Exception as e:
            return f"Erro ao consultar CoinGecko: {e}"
