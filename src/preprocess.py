# src/preprocess.py
"""
Pre-processamento de texto para o ChatLitera 2.0.

Com text-similarity-br, a biblioteca ja cuida internamente de:
  - Remocao de acentos
  - Expansao de contracoes ("vc" -> "voce", "fds" -> "fim de semana")
  - Tokenizacao
  - Remocao de stopwords do PT-BR
  - Fonetica PT-BR

Este modulo cuida apenas dos ALIASES CRITICOS de dominio:
normalizacoes especificas do vocabulario das feiras literarias que
a biblioteca nao teria como inferir automaticamente.

Exemplo critico:
  "Bienal do Livro do Rio" e "Bienal do Livro do Rio de Janeiro"
  sao variacoes coloquiais que o usuario digita, mas o dataset tem
  entradas com "Bienal Rio" ou "Bienal do Rio de Janeiro".
  Sem o alias, a similaridade lexical seria diluida pelo token extra "Livro".
"""

import re


# ---------------------------------------------------------------------------
# Aliases criticos: normalizacoes de dominio especificas das feiras literarias.
# Cada tupla e (regex_pattern, replacement).
# Ordem importa: padroes mais especificos primeiro.
# ---------------------------------------------------------------------------
ALIASES = [
    # "Bienal do Livro do Rio [de Janeiro]" -> "bienal do rio de janeiro"
    (r'\bbienal(?: internacional)? do livro do rio(?: de janeiro)?\b',
     'bienal do rio de janeiro'),

    # "Bienal do Livro de SP / Sao Paulo / São Paulo" -> "bienal do livro de sao paulo"
    (r'\bbienal(?: internacional)? do livro (?:de )?s[aã]o paulo\b',
     'bienal do livro de sao paulo'),
    (r'\bbienal(?: internacional)? do livro sp\b',
     'bienal do livro de sao paulo'),

    # "Bienal do Livro da/de Bahia" -> "bienal do livro bahia"
    (r'\bbienal(?: internacional)? do livro (?:da |de )?bahia\b',
     'bienal do livro bahia'),

    # "Bienal do Livro de/da Pernambuco / PE" -> "bienal de pernambuco"
    (r'\bbienal(?: internacional)? do livro (?:de )?pernambuco\b',
     'bienal de pernambuco'),
    (r'\bbienal(?: internacional)? do livro pe\b',
     'bienal de pernambuco'),

    # "Bienal de SP" / "Bienal de Sao Paulo" (sem a palavra "livro")
    (r'\bbienal (?:de )?s[aã]o paulo\b',
     'bienal do livro de sao paulo'),
    (r'\bbienal de sp\b',
     'bienal do livro de sao paulo'),
]


def apply_aliases(text: str) -> str:
    """
    Aplica os aliases criticos de dominio sobre o texto em minusculas.
    Deve ser chamado antes de passar o texto ao Comparator.

    Args:
        text: texto ja em minusculas

    Returns:
        texto com aliases substituidos
    """
    for pattern, replacement in ALIASES:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def preprocess(text: str) -> str:
    """
    Pipeline de pre-processamento do ChatLitera 2.0:
        1. Converte para minusculas
        2. Aplica aliases criticos de dominio

    A normalizacao linguistica completa (acentos, stopwords, fonetica)
    e feita internamente pelo text-similarity-br ao chamar compare_batch().

    Args:
        text: mensagem original do usuario

    Returns:
        texto pronto para ser passado ao Comparator
    """
    text = text.lower()
    text = apply_aliases(text)
    return text
