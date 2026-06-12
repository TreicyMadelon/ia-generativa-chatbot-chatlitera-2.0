# main.py
"""
Ponto de entrada do ChatLitera 2.0.

Uso:
    python main.py

Pre-requisito: o dataset CSV deve existir em data/feiras_literarias.csv.
Se nao existir, execute primeiro:
    python src/generate_dataset.py
"""

import sys
import os

# Garante que o diretorio raiz do projeto esteja no path do Python,
# permitindo imports como 'from src.chatbot import ChatLitera'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.chatbot import ChatLitera


# Comandos que encerram o chat
EXIT_COMMANDS = {"sair", "exit", "quit", "q"}


def main():
    """
    Loop principal do ChatLitera 2.0.
    Inicializa o bot e entra em loop de leitura de mensagens ate o usuario sair.
    """
    # Caminho absoluto para o CSV, relativo ao diretorio deste arquivo
    csv_path = os.path.join(os.path.dirname(__file__), "data", "feiras_literarias.csv")

    # Verifica se o dataset existe antes de inicializar o bot
    if not os.path.exists(csv_path):
        print("Arquivo de dados nao encontrado.")
        print("Execute primeiro o gerador de dataset:")
        print("    python src/generate_dataset.py")
        sys.exit(1)

    # Inicializa o chatbot (carrega CSV e modelo de embeddings)
    bot = ChatLitera(csv_path, similarity_threshold=0.5)

    # Cabecalho da interface de linha de comando
    print()
    print("=" * 60)
    print("  ChatLitera 2.0 - Feiras Literarias Brasileiras")
    print("=" * 60)
    print("  Pergunte sobre datas, locais, programacao,")
    print("  ingressos e autores das principais feiras do Brasil.")
    print("  Digite 'sair' para encerrar.")
    print()
    print("  Experimente comecar com:")
    print('     "O que e a bienal do livro?"')
    print('     "Qual o endereco da FLIP?"')
    print()

    # Loop de conversacao
    while True:
        try:
            user_input = input("Voce: ").strip()
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C ou fim de input: encerra graciosamente
            print("\nChatLitera: Ate logo.")
            break

        # Ignora linhas em branco
        if not user_input:
            continue

        # Verifica comandos de saida
        if user_input.lower() in EXIT_COMMANDS:
            print("ChatLitera: Ate logo. Continue participando das feiras literarias!")
            break

        # Processa e exibe a resposta
        response = bot.get_response(user_input)
        print(f"ChatLitera: {response}\n")


if __name__ == "__main__":
    main()
