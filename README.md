![CrewAI](https://img.shields.io/badge/CrewAI-FF5A50.svg?style=for-the-badge&logo=CrewAI&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=Python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57.svg?style=for-the-badge&logo=SQLite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED.svg?style=for-the-badge&logo=Docker&logoColor=white)

# Crypto Trend Crew AI

Sistema Multiagente de Análise de Tendência em Criptoativos com CrewAI.

## Configuração

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
# ou
pip install beautifulsoup4 crewai requests streamlit pyyaml
```

2. **Configurar API Key da OpenAI:**
```bash
# Copiar o arquivo de exemplo
cp env.example .env

# Editar o arquivo .env e adicionar sua API key
nano .env
```

Adicione sua chave da OpenAI no arquivo `.env`:
```
MODEL=gpt-4o-mini
OPENAI_API_KEY=sua_chave_da_openai_aqui
```

## Como usar

### Executar o pipeline completo:
```bash
make crew
```

### Executar o dashboard:
```bash
make dashboard
```

### Ver comandos disponíveis:
```bash
make help
```

## Estrutura do Projeto

- `agents.yaml` - Configuração dos agentes
- `tasks.yaml` - Configuração das tarefas  
- `project/src/project/crew.py` - Orquestração do sistema
- `project/src/project/tools/` - Ferramentas dos agentes
- `dashboard/app.py` - Dashboard Streamlit
- `data/` - Banco SQLite com dados
