# src/chatbot.py
"""
Modulo principal do ChatLitera 2.0.

Responsabilidades:
  - Carregar o dataset CSV com pares (user_input, response)
  - Pre-processar a mensagem do usuario (aliases de dominio)
  - Consultar o TextSimilarityVectorizer (text-similarity-br)
  - Retornar a resposta mais adequada ou uma mensagem de fallback
  - Filtrar mensagens fora do dominio literario

Fluxo de uma mensagem:
  1. Validacao basica (mensagem vazia)
  2. Filtro rapido por palavras-chave fora do dominio
  3. Pre-processamento: lowercase + aliases de dominio
  4. Busca hibrida via text-similarity-br (TF-IDF + Levenshtein + fonetica)
  5. Retorno da resposta ou fallback se score abaixo do limiar
"""

import csv
import logging

from src.preprocess import preprocess
from src.vectorizer import TextSimilarityVectorizer


# Configuracao de log: INFO para producao, DEBUG para depuracao detalhada
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ChatLitera")


# ---------------------------------------------------------------------------
# Palavras-chave de rejeicao rapida: verificadas ANTES da vetorizacao
# para economizar processamento em mensagens claramente fora do dominio.
# ---------------------------------------------------------------------------
OUT_OF_SCOPE_KEYWORDS = [
    "crime", "assassinato", "matar", "droga", "trafico",
    "partido", "eleicao", "futebol", "esporte",
    "investimento", "bolsa de valores",
    "namorado", "relacionamento",
    "receita", "culinaria",
    "briga", "violencia",
]

# Mensagem para perguntas fora do escopo do chatbot
_MSG_OUT_OF_SCOPE = (
    "Sou especializado apenas em feiras literarias brasileiras. "
    "Posso ajudar com informacoes sobre eventos, autores, datas, programacao, "
    "ingressos e curiosidades literarias do Brasil."
)

# Mensagem de fallback quando nenhuma resposta supera o limiar de similaridade
_MSG_FALLBACK = (
    "Nao entendi bem a pergunta. Voce pode me perguntar sobre:\n"
    "- Datas e edicoes de feiras\n"
    "- Locais e enderecos\n"
    "- Autores convidados e homenageados\n"
    "- Ingressos e precos\n"
    "- Programacao e atividades\n\n"
    "Exemplo: 'Quando e a Bienal do Rio?' ou 'Qual o endereco da FLIP?'"
)


class ChatLitera:
    """
    Chatbot especializado em feiras literarias brasileiras.

    Usa text-similarity-br (Comparator.smart) para busca hibrida:
    combina similaridade lexical (TF-IDF + cosseno), distancia de edicao
    (Levenshtein), fonetica PT-BR e extracao de entidades.
    """

    def __init__(self, csv_path: str, similarity_threshold: float = 0.40):
        """
        Carrega o dataset e inicializa o vetorizador.

        Args:
            csv_path:             caminho para o CSV com colunas user_input, response
            similarity_threshold: score minimo do text-similarity-br para aceitar
                                  uma resposta. Escala 0.0 a 1.0.
                                  Referencia da biblioteca:
                                    >= 0.85 -> match muito forte
                                    >= 0.60 -> match provavel
                                    >= 0.35 -> match incerto
                                  Usamos 0.40 como ponto de corte conservador.
        """
        self.csv_path = csv_path
        self.threshold = similarity_threshold

        # Listas paralelas: indice i corresponde ao mesmo par em ambas
        self.user_inputs: list = []   # textos pre-processados (para o vectorizer)
        self.responses: list = []     # respostas correspondentes

        self._load_data()

        # Inicializa o vetorizador com os inputs pre-processados do corpus
        self.vectorizer = TextSimilarityVectorizer(self.user_inputs, self.responses)

    def _load_data(self):
        """
        Le o CSV e popula as listas de inputs e respostas.
        Aplica pre-processamento (aliases) nos user_inputs para que
        o mapeamento interno do vectorizer seja consistente com as queries.
        Linhas com campos vazios sao ignoradas.
        """
        raw_inputs: list = []
        raw_responses: list = []

        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_input = row["user_input"].strip()
                response   = row["response"].strip()

                # Ignora linhas incompletas
                if not user_input or not response:
                    continue

                raw_inputs.append(user_input)
                raw_responses.append(response)

        # Pre-processa os user_inputs (aliases) para consistencia com as queries
        self.user_inputs = [preprocess(q) for q in raw_inputs]
        self.responses   = raw_responses

        logger.info("Carregadas %d interacoes do dataset.", len(self.responses))

    def _is_out_of_scope(self, message: str) -> bool:
        """
        Verifica se a mensagem contem palavras-chave fora do dominio literario.
        Verificacao rapida feita ANTES da vetorizacao para economizar recursos.

        Args:
            message: mensagem original do usuario (sera lowercased internamente)

        Returns:
            True se a mensagem for fora do escopo
        """
        msg_lower = message.lower()
        return any(kw in msg_lower for kw in OUT_OF_SCOPE_KEYWORDS)

    def get_response(self, user_message: str) -> str:
        """
        Processa a mensagem do usuario e retorna a resposta mais adequada.

        Args:
            user_message: texto digitado pelo usuario

        Returns:
            string com a resposta do chatbot
        """
        # Rejeita mensagens vazias
        if not user_message.strip():
            return "Por favor, envie uma mensagem para que eu possa ajudar."

        # Filtro rapido de conteudo fora do dominio
        if self._is_out_of_scope(user_message):
            return _MSG_OUT_OF_SCOPE

        # Pre-processamento: lowercase + aliases de dominio
        # (text-similarity-br cuida do restante internamente)
        processed_query = preprocess(user_message)

        # Busca a resposta mais similar usando text-similarity-br
        response, score = self.vectorizer.get_most_similar(
            processed_query, self.threshold
        )

        logger.debug("Query: '%s' | Score: %.4f", processed_query, score)

        # Score abaixo do limiar: exibe fallback com orientacoes
        if response is None:
            return _MSG_FALLBACK

        return response
