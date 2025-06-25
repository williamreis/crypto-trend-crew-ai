from crewai_tools import BaseTool
import requests

class CryptoPanicTool(BaseTool):
    name = "CryptoPanic Tool"
    description = "Busca e resume notícias relevantes de criptomoedas usando a API do CryptoPanic."

    def _run(self, query: str) -> str:
        try:
            url = "https://cryptopanic.com/api/v1/posts/"
            params = {
                'auth_token': '',  # Insira seu token se necessário
                'currencies': query.lower(),
                'public': 'true',
                'kind': 'news',
                'filter': 'hot',
                'regions': 'en',
            }
            response = requests.get(url, params=params)
            data = response.json()
            if 'results' not in data or not data['results']:
                return f"Nenhuma notícia encontrada para {query}."
            noticias = [f"- {item['title']} ({item['url']})" for item in data['results'][:5]]
            return f"Notícias recentes para {query}:\n" + "\n".join(noticias)
        except Exception as e:
            return f"Erro ao consultar CryptoPanic: {e}" 