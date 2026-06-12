# src/vectorizer.py
"""
Vetorizador do ChatLitera 2.0 usando text-similarity-br.

MUDANCA EM RELACAO A VERSAO 1.0:
  Versao 1.0: CountVectorizer (Bag of Words) + similaridade de cosseno simples.
              Contava palavras em comum — frases com vocabulario diferente
              mas mesmo significado tinham score baixo.

  Versao 2.0: text-similarity-br com Comparator.smart(), que combina:
    - Cosseno (TF-IDF): frequencia e raridade das palavras
    - Levenshtein:      distancia de edicao (captura erros de digitacao)
    - Fonetica PT-BR:   trata "cassaa" e "caca" como similares
    - Entidades:        deteccao de valores monetarios, datas, modelos

  A similaridade de cosseno ainda e usada internamente pelo text-similarity-br
  como parte do pipeline hibrido, mas agora combinada com os outros algoritmos.

INTERPRETACAO DOS SCORES (conforme documentacao da biblioteca):
  >= 0.85  -> match muito forte (provavel duplicata ou variacao minima)
  0.60-0.84 -> match provavel (mesmo item com descricao diferente)
  0.35-0.59 -> match incerto (requer revisao)
  < 0.35   -> sem relacao semantica relevante

  Para o chatbot, usamos threshold=0.40 como ponto de corte.
"""

import logging

from text_similarity.api import Comparator


logger = logging.getLogger("ChatLitera.Vectorizer")


class TextSimilarityVectorizer:
    """
    Encapsula o Comparator.smart() do text-similarity-br para busca
    do par mais similar no corpus do dataset.
    """

    def __init__(self, corpus_sentences: list, responses: list):
        """
        Inicializa o Comparator e constroi o mapeamento input -> response.

        Args:
            corpus_sentences: lista de user_inputs do CSV (ja pre-processados)
            responses:        lista de respostas correspondentes (indices paralelos)
        """
        # Mapeamento direto: texto do user_input -> resposta correspondente.
        # Em caso de user_inputs duplicados no CSV, a ultima ocorrencia prevalece.
        self._response_map: dict = {
            q: r for q, r in zip(corpus_sentences, responses)
        }

        # Mantemos a lista para passar ao compare_batch
        self.corpus_sentences = corpus_sentences

        logger.info("Inicializando Comparator text-similarity-br (smart mode)...")

        # Comparator.smart() ativa:
        #   - TF-IDF + cosseno (filtragem rapida por vocabulario)
        #   - Levenshtein (erros de digitacao)
        #   - Fonetica PT-BR (sons equivalentes)
        #   - Extracao de entidades (dinheiro, datas, modelos de produto)
        self.comp = Comparator.smart()

        logger.info("Comparator pronto. Corpus com %d entradas.", len(corpus_sentences))

    def get_most_similar(self, query: str, threshold: float = 0.40):
        """
        Busca a entrada do corpus mais similar a query usando text-similarity-br.

        Internamente, compare_batch:
          1. Pre-processa query e candidatos (limpeza, stopwords, fonetica)
          2. Filtra por TF-IDF minimo (min_cosine=0.0 para nao descartar nada)
          3. Calcula score hibrido (cosseno + levenshtein + fonetica + entidade)
          4. Retorna os top_n resultados ordenados por score

        Args:
            query:     texto pre-processado da pergunta do usuario
            threshold: score minimo para aceitar a resposta (0.0 a 1.0)

        Returns:
            (response_str, score) se score >= threshold
            (None,         score) se nenhum resultado superar o limiar
        """
        # Compara query contra todo o corpus e retorna o melhor match
        # top_n=1: queremos apenas o resultado mais similar
        # min_cosine=0.0: sem filtro de corte por TF-IDF — deixamos o
        #                 score hibrido final fazer o corte via threshold
        results = self.comp.compare_batch(
            query,
            self.corpus_sentences,
            top_n=1,
            min_cosine=0.0,
        )

        # Sem resultados (corpus vazio ou erro interno)
        if not results:
            logger.warning("compare_batch retornou lista vazia para query: '%s'", query)
            return None, 0.0

        best = results[0]
        score: float = best["score"]
        candidate: str = best["candidate"]

        logger.debug("Query: '%s' | Melhor match: '%s' | Score: %.4f", query, candidate, score)

        # Score abaixo do limiar: retorna fallback
        if score < threshold:
            return None, score

        # Recupera a resposta correspondente ao candidato
        response = self._response_map.get(candidate)
        if response is None:
            logger.warning("Candidato encontrado mas sem resposta no mapa: '%s'", candidate)
            return None, score

        return response, score
