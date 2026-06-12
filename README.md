
# ChatLitera 2.0
### Chatbot Local sobre Feiras Literárias Brasileiras

---

## Descrição

O **ChatLitera** é um chatbot que responde perguntas sobre as principais feiras literárias do Brasil — como datas, locais, programação, ingressos e autores participantes — usando apenas um arquivo CSV e text-similarity-br 0.8.1.

---

## Feiras Cobertas

| Feira | Cidade | Período |
|-------|--------|---------|
| Bienal Internacional do Livro de SP | São Paulo (SP) | Julho |
| Bienal do Rio de Janeiro | Rio de Janeiro (RJ) | Setembro |
| FLIP – Festa Literária Internacional de Paraty | Paraty (RJ) | Julho/Agosto |
| FLIC – Festa Literária de Belo Horizonte | Belo Horizonte (MG) | Junho |
| Festa Literária de Porto Alegre | Porto Alegre (RS) | Novembro |
| Feira do Livro de Porto Alegre | Porto Alegre (RS) | Out./Nov. |
| FLOR – Feira Literária do Orgulho e Resistência | São Paulo (SP) | Junho |
| Bienal do Livro Bahia | Salvador (BA) | Outubro |
| Bienal Internacional do Livro de Pernambuco | Recife (PE) | Outubro |
| Feira do Livro da Unesp | São Paulo (SP) | Outubro |
| Flipoços – Festa Literária de Poços de Caldas | Poços de Caldas (MG) | Agosto |
| Festival Literário Catarinense | Florianópolis (SC) | Setembro |

---

## Requisitos

- Python 3.8 ou superior

---

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


## Instalação

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Gere o dataset (necessário apenas na primeira execução)

```bash
python src/generate_dataset.py
```

Isso cria o arquivo `data/feiras_literarias.csv` com ~1000 interações.

### 3. Execute o chatbot

```bash
python main.py
```

## Exemplo de uso

    Voce: onde fica a bienal do rio de janeiro?
    ChatLitera: A Bienal do Rio de Janeiro e realizada em Rio de Janeiro (RJ) - Riocentro.

    Voce: qual o endereco da FLIP?
    ChatLitera: O endereco da FLIP e: Praca da Matriz, s/n - Centro Historico, Paraty (RJ).

    Voce: quem ja foi homenageado na FLIP?
    ChatLitera: A FLIP ja prestou homenagem a grandes nomes como Guimaraes Rosa e Cora Coralina.

    Você: Quando é a FLIP?
    ChatLitera: A FLIP – Festa Literária Internacional de Paraty é realizada 
    geralmente em julho/agosto. Para as datas exatas desta edição, 
    consulte www.flip.org.br. 

    Você: Quanto custa o ingresso da Bienal do Rio?
    ChatLitera: Os preços dos ingressos da Bienal do Rio de Janeiro variam a cada 
    edição. Em geral, há ingressos simbólicos (a partir de R$ 20,00) e costumam 
    existir dias ou atividades de entrada gratuita. Verifique em www.bienaldorio.com.br 

    Voce: sair
    ChatLitera: Ate logo. Continue participando das feiras literarias!

## Segurança

- Nenhuma informação do usuário é enviada a serviços externos
- O modelo roda inteiramente offline após a instalação
- Não há armazenamento de histórico de conversas
- Palavras-chave fora do domínio literário são filtradas antes da vetorização


## Licença

MIT — livre para uso, modificação e distribuição.
