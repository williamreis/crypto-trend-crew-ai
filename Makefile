# Makefile

.PHONY: help dashboard crew setup

help:
	@echo "Comandos disponíveis:"
	@echo "  make setup      # Cria diretórios e inicializa banco de dados"
	@echo "  make dashboard  # Executa o dashboard Streamlit"
	@echo "  make crew       # Executa o pipeline multiagente CrewAI"

setup:
	@echo "Criando diretório data..."
	mkdir -p data
	@echo "Inicializando banco SQLite..."
	python3 -c "from project.src.project.tools.sqlite_tool import SQLiteTool; SQLiteTool()"
	@echo "Setup concluído!"

dashboard:
	streamlit run dashboard/app.py

crew: setup
	python3 project/src/project/main.py
