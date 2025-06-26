import requests
import urllib.parse
from crewai.tools import BaseTool
from bs4 import BeautifulSoup
from typing import Type
from pydantic import BaseModel, Field


class NewsToolInput(BaseModel):
    """
    Argumentos de entrada para a ferramenta CoinGecko
    """
    query: str = Field(description="Query para buscar notícias sobre criptomoedas. Exemplo: 'Bitcoin', 'Ethereum', etc.")


class NewsTool(BaseTool):
    name: str = "News Tool"
    description: str = "Busca notícias relevantes sobre criptomoedas usando Google News (gratuito, sem API token)."
    args_schema: Type[BaseTool] = NewsToolInput

    def _run(self, query: str) -> str:
        try:
            # Buscar notícias no Google News
            search_query = f"{query} cryptocurrency news"
            encoded_query = urllib.parse.quote(search_query)
            url = f"https://news.google.com/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extrair notícias (estrutura pode variar, então vamos ser genéricos)
            articles = []
            article_elements = soup.find_all('article')[:5]  # Limitar a 5 notícias

            if not article_elements:
                # Fallback: procurar por links de notícias
                links = soup.find_all('a', href=True)
                news_links = [link for link in links if 'news' in link.get('href', '')][:5]

                for link in news_links:
                    title = link.get_text(strip=True)
                    if title and len(title) > 10:  # Filtrar títulos muito curtos
                        articles.append(f"- {title}")
            else:
                for article in article_elements:
                    title_elem = article.find('h3') or article.find('h2') or article.find('a')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        if title and len(title) > 10:
                            articles.append(f"- {title}")

            if articles:
                return f"Notícias recentes sobre {query}:\n" + "\n".join(articles)
            else:
                return f"Nenhuma notícia encontrada para {query}. Tente buscar por termos mais específicos."

        except Exception as e:
            return f"Erro ao buscar notícias: {e}"
