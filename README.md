# ChatLitera 2.0

Chatbot especializado em feiras literarias brasileiras.
Roda 100% localmente, sem conexao com APIs externas.

## O que mudou da versão 1.0

| Item | Versao 1.0 | Versao 2.0 |
|---|---|---|
| Biblioteca | scikit-learn (CountVectorizer) | text-similarity-br 0.8.1 |
| Algoritmo | Bag of Words + cosseno simples | Hibrido: TF-IDF + Levenshtein + Fonetica PT-BR + Entidades |
| Preprocessing | unidecode + normalizacao manual | Feito internamente pela biblioteca |
| Threshold padrao | 0.2 | 0.40 |

## Biblioteca text-similarity-br

Biblioteca brasileira especializada em comparacao de similaridade de textos
em Portugues Brasileiro. O Comparator.smart() combina:

- TF-IDF + Cosseno: frequencia e raridade das palavras
- Levenshtein:      distancia de edicao (captura erros de digitacao)
- Fonetica PT-BR:   trata sons equivalentes ("caza" e "casa")
- Entidades:        deteccao de valores monetarios, datas, modelos de produto

## Estrutura do projeto

    chatbot-chatlitera-2.0/
        main.py                    ponto de entrada do chatbot
        requirements.txt           dependencias
        .gitignore
        data/
            feiras_literarias.csv  dataset (incluido no zip)
        src/
            __init__.py
            generate_dataset.py    gera o CSV (so rodar se quiser regenerar)
            preprocess.py          aliases criticos de dominio
            vectorizer.py          text-similarity-br Comparator
            chatbot.py             logica principal

## Instalação e uso

    pip install -r requirements.txt
    python main.py

Na primeira execucao o modelo pode demorar alguns segundos para carregar.
Das proximas vezes sera instantaneo (cache em disco automatico da biblioteca).

## Exemplo de uso

    Voce: onde fica a bienal do rio de janeiro?
    ChatLitera: A Bienal do Rio de Janeiro e realizada em Rio de Janeiro (RJ) - Riocentro.

    Voce: qual o endereco da FLIP?
    ChatLitera: O endereco da FLIP e: Praca da Matriz, s/n - Centro Historico, Paraty (RJ).

    Voce: quem ja foi homenageado na FLIP?
    ChatLitera: A FLIP ja prestou homenagem a grandes nomes como Guimaraes Rosa e Cora Coralina.

    Voce: sair
    ChatLitera: Ate logo. Continue participando das feiras literarias!

## Segurança

- Nenhuma informacao do usuario e enviada a servicos externos
- O modelo roda inteiramente offline apos instalacao
- Nao ha armazenamento de historico de conversas
- Palavras-chave fora do dominio literario sao filtradas antes da vetorizacao
