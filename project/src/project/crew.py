from dotenv import load_dotenv

_ = load_dotenv()

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from project.src.project.tools.coingecko_tool import CoinGeckoTool
from project.src.project.tools.news_tool import NewsTool
from project.src.project.tools.sqlite_tool import SQLiteTool

# import agentops
# agentops.init()

# Instanciar as tools
coingecko_tool = CoinGeckoTool()
news_tool = NewsTool()
sqlite_tool = SQLiteTool()


@CrewBase
class CryptoTrendCrew():
    # Carregar configurações de agentes e tarefas
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def agente_coingecko(self) -> Agent:
        return Agent(
            config=self.agents_config['agente_coingecko'],
            tools=[coingecko_tool, sqlite_tool],
            verbose=True
        )

    @agent
    def agente_sentimento(self) -> Agent:
        return Agent(
            config=self.agents_config['agente_sentimento'],
            tools=[news_tool, sqlite_tool],
            verbose=True
        )

    @agent
    def agente_persistencia(self) -> Agent:
        return Agent(
            config=self.agents_config['agente_persistencia'],
            tools=[sqlite_tool],
            verbose=True
        )

    @agent
    def agente_tendencias(self) -> Agent:
        return Agent(
            config=self.agents_config['agente_tendencias'],
            tools=[sqlite_tool],
            verbose=True
        )

    @agent
    def agente_comparador(self) -> Agent:
        return Agent(
            config=self.agents_config['agente_comparador'],
            tools=[sqlite_tool],
            verbose=True
        )

    @agent
    def agente_relatorios(self) -> Agent:
        return Agent(
            config=self.agents_config['agente_relatorios'],
            tools=[sqlite_tool],
            verbose=True
        )

    @task
    def identificar_moedas_em_evidencia(self) -> Task:
        return Task(
            config=self.tasks_config['identificar_moedas_em_evidencia'],
            verbose=True
        )

    @task
    def analisar_sentimento_de_mercado(self) -> Task:
        return Task(
            config=self.tasks_config['analisar_sentimento_de_mercado'],
            verbose=True
        )

    @task
    def armazenar_dados_em_sqlite(self) -> Task:
        return Task(
            config=self.tasks_config['armazenar_dados_em_sqlite'],
            verbose=True
        )

    @task
    def detectar_tendencias_em_dados(self) -> Task:
        return Task(
            config=self.tasks_config['detectar_tendencias_em_dados'],
            verbose=True
        )

    @task
    def comparar_dados_temporais(self) -> Task:
        return Task(
            config=self.tasks_config['comparar_dados_temporais'],
            verbose=True
        )

    @task
    def gerar_relatorio_geral(self) -> Task:
        return Task(
            config=self.tasks_config['gerar_relatorio_geral'],
            verbose=True
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CreateBlogpostWTools crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
