# src/generate_dataset.py
"""
Gerador do dataset do ChatLitera 2.0.

Gera o arquivo data/feiras_literarias.csv com ~1000 interacoes sinteticas
cobrindo os principais temas: datas, locais, enderecos, autores convidados,
autores homenageados, ingressos, programacao e perguntas fora de escopo.

TRATAMENTO DE ACENTOS NO CSV:
    O CSV e salvo em UTF-8 para preservar os acentos originais nas respostas
    (ex: "Sao Paulo", "programacao", "Conceicao Evaristo"). Isso garante que
    o texto exibido ao usuario seja legivel e correto em portugues.
    O pre-processamento (remocao de acentos via unidecode) e feito apenas
    no momento da comparacao de similaridade, nunca nos textos armazenados.

Execute uma unica vez antes de iniciar o chatbot:
    python src/generate_dataset.py
"""

import csv
import os
import random

random.seed(42)

# ---------------------------------------------------------------------------
# Dados base: cada feira e um dicionario com todas as informacoes necessarias
# para gerar as perguntas e respostas dinamicamente.
# ---------------------------------------------------------------------------

FEIRAS = [
    {
        "nome": "Bienal Internacional do Livro de Sao Paulo",
        "sigla": "Bienal do Livro SP",
        "local": "Sao Paulo (SP) - Pavilhao do Anhembi",
        "endereco": "Av. Olavo Fontoura, 1209 - Santana, Sao Paulo (SP) - CEP 02012-021 (Pavilhao do Anhembi)",
        "mes": "julho",
        "site": "www.bienaldolivro.com.br",
        "descricao": (
            "um dos maiores eventos literarios da America Latina, "
            "reunindo editoras, autores e leitores do mundo inteiro"
        ),
        # Autores que receberam homenagem oficial do evento
        "homenageados": ["Clarice Lispector", "Jorge Amado", "Ariano Suassuna"],
        # Autores que ja participaram como convidados
        "convidados_exemplos": [
            "Milton Hatoum", "Djamila Ribeiro", "Itamar Vieira Junior",
            "Ailton Krenak", "Conceicao Evaristo",
        ],
    },
    {
        "nome": "Bienal do Rio de Janeiro",
        "sigla": "Bienal Rio",
        "local": "Rio de Janeiro (RJ) - Riocentro",
        "endereco": "Av. Salvador Allende, 6555 - Barra da Tijuca, Rio de Janeiro (RJ) - CEP 22783-127 (Riocentro, Pavilhao 3)",
        "mes": "setembro",
        "site": "www.bienaldorio.com.br",
        "descricao": (
            "um dos eventos mais aguardados do Rio, com lancamentos exclusivos "
            "e encontros com grandes autores brasileiros e internacionais"
        ),
        "homenageados": ["Machado de Assis", "Clarice Lispector", "Graciliano Ramos"],
        "convidados_exemplos": [
            "Conceicao Evaristo", "Djamila Ribeiro", "Milton Hatoum",
            "Lygia Fagundes Telles", "Ailton Krenak",
        ],
    },
    {
        "nome": "FLIP - Festa Literaria Internacional de Paraty",
        "sigla": "FLIP",
        "local": "Paraty (RJ)",
        "endereco": "Praca da Matriz, s/n - Centro Historico, Paraty (RJ) - CEP 23970-000 (Casa da Cultura de Paraty e espacos do centro historico)",
        "mes": "julho/agosto",
        "site": "www.flip.org.br",
        "descricao": (
            "um festival intimista e sofisticado realizado na historica cidade de Paraty, "
            "reconhecido internacionalmente pela qualidade de sua programacao"
        ),
        "homenageados": [
            "Guimaraes Rosa", "Cora Coralina", "Lima Barreto",
            "Hilda Hilst", "Manoel de Barros", "Carlos Drummond de Andrade",
        ],
        "convidados_exemplos": [
            "Conceicao Evaristo", "Djamila Ribeiro", "Ailton Krenak",
            "Itamar Vieira Junior", "Milton Hatoum", "Lygia Fagundes Telles",
        ],
    },
    {
        "nome": "FLIC - Festa Literaria de Belo Horizonte",
        "sigla": "FLIC",
        "local": "Belo Horizonte (MG)",
        "endereco": "Praca da Liberdade, s/n - Funcionarios, Belo Horizonte (MG) - CEP 30140-010 (Circuito Liberdade)",
        "mes": "junho",
        "site": "www.flicbh.com.br",
        "descricao": (
            "um festival mineiro com forte identidade cultural, "
            "promovendo debates, oficinas e lancamentos de livros"
        ),
        "homenageados": ["Drummond de Andrade", "Guimaraes Rosa", "Conceicao Evaristo"],
        "convidados_exemplos": [
            "Itamar Vieira Junior", "Djamila Ribeiro", "Ailton Krenak", "Milton Hatoum",
        ],
    },
    {
        "nome": "Festa Literaria de Porto Alegre",
        "sigla": "Festa Literaria POA",
        "local": "Porto Alegre (RS)",
        "endereco": "Usina do Gasometro - Av. Presidente Joao Goulart, 551 - Centro Historico, Porto Alegre (RS) - CEP 90010-310",
        "mes": "novembro",
        "site": "festaliterariaportaalegre.com.br",
        "descricao": (
            "um dos principais eventos literarios do Sul do Brasil, "
            "com intensa programacao de autores regionais e nacionais"
        ),
        "homenageados": ["Erico Verissimo", "Moacyr Scliar", "Rubem Braga"],
        "convidados_exemplos": [
            "Milton Hatoum", "Conceicao Evaristo", "Djamila Ribeiro", "Ailton Krenak",
        ],
    },
    {
        "nome": "Feira do Livro de Porto Alegre",
        "sigla": "Feira do Livro POA",
        "local": "Porto Alegre (RS) - Praca da Alfandega",
        "endereco": "Praca da Alfandega, s/n - Centro Historico, Porto Alegre (RS) - CEP 90010-150",
        "mes": "outubro/novembro",
        "site": "www.feiradolivro.com.br",
        "descricao": (
            "a mais antiga feira literaria do Brasil, realizada ao ar livre "
            "na iconica Praca da Alfandega desde 1955"
        ),
        "homenageados": [
            "Erico Verissimo", "Moacyr Scliar", "Josue Guimaraes", "Lya Luft", "Rubem Alves",
        ],
        "convidados_exemplos": [
            "Conceicao Evaristo", "Ailton Krenak", "Djamila Ribeiro",
            "Itamar Vieira Junior", "Milton Hatoum",
        ],
    },
    {
        "nome": "FLOR - Feira Literaria do Orgulho e Resistencia",
        "sigla": "FLOR",
        "local": "Sao Paulo (SP)",
        "endereco": "Largo do Arouche, s/n - Republica, Sao Paulo (SP) - CEP 01219-010 (Largo do Arouche e adjacencias)",
        "mes": "junho",
        "site": "www.feiraflor.com.br",
        "descricao": (
            "uma feira literaria dedicada a vozes LGBTQIA+, perifericas e de resistencia, "
            "celebrando a diversidade e o poder transformador da literatura"
        ),
        "homenageados": ["Caio Fernando Abreu", "Cassandra Rios", "Joao Silverio Trevisan"],
        "convidados_exemplos": [
            "Djamila Ribeiro", "Ailton Krenak", "Conceicao Evaristo", "Itamar Vieira Junior",
        ],
    },
    {
        "nome": "Bienal do Livro Bahia",
        "sigla": "Bienal Bahia",
        "local": "Salvador (BA) - Centro de Convencoes",
        "endereco": "Centro de Convencoes da Bahia - Av. Antonio Carlos Magalhaes, s/n - Stiep, Salvador (BA) - CEP 41770-019",
        "mes": "outubro",
        "site": "www.bienaldolivrobahia.com.br",
        "descricao": (
            "um dos maiores eventos literarios do Nordeste, reunindo autores, editoras "
            "e leitores em Salvador com forte identidade cultural baiana"
        ),
        "homenageados": ["Jorge Amado", "Ariano Suassuna", "Conceicao Evaristo"],
        "convidados_exemplos": [
            "Itamar Vieira Junior", "Djamila Ribeiro", "Ailton Krenak", "Milton Hatoum",
        ],
    },
    {
        "nome": "Bienal Internacional do Livro de Pernambuco",
        "sigla": "Bienal PE",
        "local": "Recife (PE) - Centro de Convencoes",
        "endereco": "Centro de Convencoes de Pernambuco - Complexo Viario Via Expressa, s/n - Camaragibe (PE) - CEP 54768-000",
        "mes": "outubro",
        "site": "www.bienaldolivrope.com.br",
        "descricao": (
            "um dos grandes festivais do livro no coracao do Nordeste, destacando autores "
            "regionais e internacionais com rica programacao cultural"
        ),
        "homenageados": ["Ariano Suassuna", "Joao Cabral de Melo Neto", "Clarice Lispector"],
        "convidados_exemplos": [
            "Conceicao Evaristo", "Itamar Vieira Junior", "Djamila Ribeiro", "Ailton Krenak",
        ],
    },
    {
        "nome": "Feira do Livro da Unesp",
        "sigla": "Feira Unesp",
        "local": "Sao Paulo (SP) - Campus da Unesp",
        "endereco": "Rua Quirino de Andrade, 215 - Centro, Sao Paulo (SP) - CEP 01049-010 (Editora Unesp / Livraria da Unesp)",
        "mes": "outubro",
        "site": "www.livraria.unesp.br",
        "descricao": (
            "uma feira academica e literaria promovida pela Editora Unesp, "
            "com forte presenca de titulos universitarios, tecnicos e de divulgacao cientifica"
        ),
        "homenageados": ["Mario de Andrade", "Paulo Freire", "Florestan Fernandes"],
        "convidados_exemplos": [
            "Ailton Krenak", "Djamila Ribeiro", "Milton Hatoum", "Conceicao Evaristo",
        ],
    },
    {
        "nome": "Flipocos - Festa Literaria de Pocos de Caldas",
        "sigla": "Flipocos",
        "local": "Pocos de Caldas (MG)",
        "endereco": "Thermas Antonio Carlos - Av. Francisco Salles, 544 - Centro, Pocos de Caldas (MG) - CEP 37701-366",
        "mes": "agosto",
        "site": "www.flipocos.com.br",
        "descricao": (
            "um festival literario encantador na cidade das aguas, com programacao "
            "intimista e diversificada para leitores de todas as idades"
        ),
        "homenageados": ["Guimaraes Rosa", "Lygia Fagundes Telles", "Rubem Braga"],
        "convidados_exemplos": [
            "Milton Hatoum", "Conceicao Evaristo", "Djamila Ribeiro", "Itamar Vieira Junior",
        ],
    },
    {
        "nome": "Festival Literario Catarinense",
        "sigla": "Festival Literario SC",
        "local": "Florianopolis (SC)",
        "endereco": "Centro Integrado de Cultura - Av. Irineu Bornhausen, 5600 - Agronomica, Florianopolis (SC) - CEP 88034-100 (CIC Florianopolis)",
        "mes": "setembro",
        "site": "www.festivalliterariosc.com.br",
        "descricao": (
            "um dos principais festivais do Sul do Brasil, celebrando a literatura "
            "catarinense e nacional com debates, lancamentos e oficinas"
        ),
        "homenageados": ["Cruz e Sousa", "Antonieta de Barros", "Salim Miguel"],
        "convidados_exemplos": [
            "Conceicao Evaristo", "Ailton Krenak", "Milton Hatoum", "Djamila Ribeiro",
        ],
    },
]

# Lista auxiliar de autores para uso em perguntas gerais
AUTORES = [
    "Machado de Assis", "Clarice Lispector", "Jorge Amado",
    "Jose de Alencar", "Cora Coralina", "Guimaraes Rosa",
    "Graciliano Ramos", "Lygia Fagundes Telles", "Rubem Braga",
    "Ariano Suassuna", "Milton Hatoum", "Conceicao Evaristo",
    "Ailton Krenak", "Djamila Ribeiro", "Itamar Vieira Junior",
]

# Generos literarios para perguntas de recomendacao
GENEROS = [
    "romance", "poesia", "conto", "cronica", "literatura infantil",
    "ficcao cientifica", "thriller", "nao-ficcao", "biografia", "ensaio",
]


# ---------------------------------------------------------------------------
# Templates estaticos: pares (lista_de_perguntas, resposta)
# Usados para saudacoes, despedidas e agradecimentos.
# ---------------------------------------------------------------------------

TEMPLATES = [
    # Saudacoes
    (
        [
            "oi", "ola", "oi tudo bem", "ola, tudo bem?", "bom dia", "boa tarde",
            "boa noite", "hey", "salve", "eai", "e ai", "opa",
        ],
        "Ola! Sou o ChatLitera, seu guia sobre feiras literarias brasileiras. "
        "Posso ajudar com datas, locais, programacao, ingressos e muito mais. O que voce quer saber?",
    ),
    # Despedidas
    (
        [
            "tchau", "ate logo", "ate mais", "obrigado tchau", "valeu, tchau",
            "foi otimo obrigado", "ate", "xau", "flw", "falou",
        ],
        "Ate logo! Espero ter ajudado. Continue participando das feiras literarias do Brasil!",
    ),
    # Agradecimentos
    (
        [
            "obrigado", "obrigada", "valeu", "muito obrigado", "thanks",
            "grato", "grata", "agradeco",
        ],
        "Fico feliz em ajudar! Se tiver mais duvidas sobre feiras literarias, e so perguntar.",
    ),
]


# ---------------------------------------------------------------------------
# Templates dinamicos: gerados para cada feira da lista FEIRAS.
# Cada item e (lista_de_templates_de_pergunta, template_de_resposta).
# Os placeholders {sigla}, {nome}, {mes}, etc. sao preenchidos por feira.
# ---------------------------------------------------------------------------

DYNAMIC_TEMPLATES = [
    # Datas
    (
        [
            "quando e a {sigla}?",
            "qual a data da {sigla}?",
            "em que mes acontece a {sigla}?",
            "quando vai ser a {sigla} esse ano?",
            "qual o periodo da {sigla}?",
            "em que epoca do ano rola a {sigla}?",
            "quais as datas da {nome}?",
            "quando ocorre a {nome}?",
        ],
        "A {nome} geralmente acontece em {mes}. "
        "Para as datas exatas desta edicao, consulte {site}.",
    ),
    # Local / cidade
    (
        [
            "onde fica a {sigla}?",
            "onde acontece a {sigla}?",
            "qual e o local da {sigla}?",
            "em que cidade e a {sigla}?",
            "onde e realizada a {nome}?",
            "qual a cidade da {sigla}?",
            "a {sigla} e em qual cidade?",
        ],
        "A {nome} e realizada em {local}.",
    ),
    # Endereco completo
    (
        [
            "qual o endereco da {sigla}?",
            "qual o endereco da {nome}?",
            "onde exatamente fica a {sigla}?",
            "me da o endereco da {sigla}",
            "qual o endereco completo da {sigla}?",
            "em que rua fica a {sigla}?",
            "como chegar na {sigla}?",
            "qual o local exato da {sigla}?",
        ],
        "O endereco da {nome} e: {endereco}. "
        "Para informacoes de transporte e estacionamento, consulte {site}.",
    ),
    # O que e
    (
        [
            "o que e a {sigla}?",
            "me fale sobre a {sigla}",
            "me conta sobre a {nome}",
            "o que e a {nome}?",
            "qual a historia da {sigla}?",
            "me explica o que e a {sigla}",
            "fala sobre a {sigla}",
        ],
        "A {nome} e {descricao}. "
        "Acesse {site} para mais informacoes.",
    ),
    # Ingresso
    (
        [
            "quanto custa o ingresso da {sigla}?",
            "qual o preco do ingresso para a {sigla}?",
            "a {sigla} e paga?",
            "precisa pagar para entrar na {sigla}?",
            "tem entrada gratuita na {sigla}?",
            "quanto e o ticket da {sigla}?",
            "a {nome} cobra entrada?",
        ],
        "Os precos dos ingressos da {nome} variam a cada edicao. "
        "Em geral, ha ingressos simbolicos (a partir de R$ 20,00) e costumam existir dias ou atividades de entrada gratuita. "
        "Verifique os valores atuais em {site}.",
    ),
    # Programacao
    (
        [
            "qual a programacao da {sigla}?",
            "quais as atividades da {sigla}?",
            "o que tem na {sigla}?",
            "quais eventos tem na {sigla}?",
            "o que acontece na {sigla}?",
            "tem bate-papo com autores na {sigla}?",
            "tem oficinas na {sigla}?",
        ],
        "A {nome} costuma oferecer: bate-papos com autores, mesas de debate, "
        "lancamentos de livros, oficinas literarias e espacos para criancas. "
        "A programacao completa e divulgada em {site} proximo ao evento.",
    ),
    # Autores CONVIDADOS (ja estiveram no evento como participantes)
    (
        [
            "quais autores ja foram convidados para a {sigla}?",
            "quem ja participou da {sigla}?",
            "quais escritores ja estiveram na {sigla}?",
            "quem ja foi convidado para a {sigla}?",
            "quais autores participam da {nome}?",
            "quais escritores costumam ir a {sigla}?",
            "me diz autores que ja foram na {sigla}",
        ],
        "A {nome} ja recebeu como convidados nomes como {conv1}, {conv2} e {conv3}, "
        "entre outros autores brasileiros e internacionais. "
        "Os convidados de cada nova edicao sao anunciados em {site}.",
    ),
    # Autores HOMENAGEADOS (receberam homenagem oficial do evento)
    (
        [
            "quem foi homenageado na {sigla}?",
            "quem sao os homenageados da {sigla}?",
            "quais autores foram homenageados na {sigla}?",
            "a {sigla} ja homenageou quais autores?",
            "quem recebeu homenagem na {nome}?",
            "quais escritores foram homenageados pela {sigla}?",
            "quem e o homenageado da {sigla}?",
        ],
        "A {nome} ja prestou homenagem a grandes nomes da literatura, como {hom1}, {hom2} e {hom3}. "
        "O autor ou autora homenageado(a) de cada edicao e anunciado(a) em {site}.",
    ),
    # Importancia
    (
        [
            "por que a {sigla} e importante?",
            "qual a importancia da {sigla}?",
            "qual o impacto da {sigla}?",
            "por que devo ir a {sigla}?",
            "vale a pena ir na {sigla}?",
        ],
        "A {nome} e fundamental para fomentar a leitura e a cultura no Brasil, "
        "conectando autores, editoras e leitores de todo o pais. "
        "E uma experiencia enriquecedora para qualquer amante da literatura.",
    ),
]


# ---------------------------------------------------------------------------
# Perguntas gerais: nao estao vinculadas a uma feira especifica.
# ---------------------------------------------------------------------------

GENERAL_QA = [
    (
        "quais sao as principais feiras literarias do Brasil?",
        "As principais feiras literarias do Brasil sao: Bienal Internacional do Livro de SP, "
        "Bienal do Rio, FLIP (Paraty), FLIC (Belo Horizonte), Festa Literaria POA, "
        "Feira do Livro de Porto Alegre, FLOR (Sao Paulo), Bienal Bahia, Bienal PE (Recife), "
        "Feira Unesp, Flipocos (Pocos de Caldas) e Festival Literario Catarinense. "
        "Cada uma tem sua identidade unica.",
    ),
    (
        "qual a maior feira literaria do Brasil?",
        "A Bienal Internacional do Livro de Sao Paulo e considerada a maior feira literaria do Brasil "
        "e uma das maiores da America Latina, recebendo milhoes de visitantes por edicao.",
    ),
    (
        "qual a mais antiga feira literaria do Brasil?",
        "A Feira do Livro de Porto Alegre, realizada desde 1955 na Praca da Alfandega, "
        "e a mais antiga feira literaria do Brasil. Uma tradicao de mais de 60 anos.",
    ),
    (
        "tem feira literaria perto de mim?",
        "Isso depende de onde voce mora! As principais feiras acontecem em Sao Paulo, Rio de Janeiro, "
        "Paraty (RJ), Belo Horizonte (MG) e Porto Alegre (RS). Qual cidade fica mais proxima de voce?",
    ),
    (
        "quais feiras literarias tem atividades para criancas?",
        "A maioria das grandes feiras tem espacos dedicados ao publico infantil. "
        "Bienal do Livro SP, Bienal Rio e FLIP costumam ter programacao especial para criancas, "
        "com contacao de historias e oficinas criativas.",
    ),
    (
        "posso comprar livros nas feiras literarias?",
        "Sim! As feiras literarias sao otimos locais para comprar livros, geralmente com descontos "
        "e promocoes especiais. Muitas editoras oferecem precos diferenciados durante os eventos.",
    ),
    (
        "qual a diferenca entre bienal e feira literaria?",
        "A principal diferenca e a frequencia: bienal significa que o evento ocorre a cada dois anos, "
        "enquanto feira pode ser anual. No conteudo, ambas vendem livros e promovem encontros culturais, "
        "mas as bienais costumam ser maiores em escala.",
    ),
    (
        "tem alguma feira literaria em julho?",
        "Sim! Julho e um mes cheio de feiras literarias. A FLIP (Paraty) e a Bienal do Livro SP "
        "costumam ocorrer nessa epoca. E uma otima opcao para as ferias escolares.",
    ),
    (
        "me recomende uma feira para iniciantes em literatura",
        "Para quem esta comecando, a Bienal Internacional do Livro de Sao Paulo e excelente: "
        "tem uma enorme variedade de titulos, precos acessiveis e programacao para todos os gostos. "
        "A Feira do Livro de Porto Alegre tambem e muito acolhedora.",
    ),
    (
        "tem feira literaria no nordeste?",
        "Sim! O Nordeste tem eventos literarios de peso: a Bienal do Livro Bahia (Salvador) "
        "e a Bienal Internacional do Livro de Pernambuco (Recife) sao os maiores. "
        "A cena literaria nordestina e rica e crescente.",
    ),
    (
        "qual feira tem melhor programacao musical?",
        "A FLIP de Paraty e famosa por combinar literatura com shows musicais e o charme da cidade historica. "
        "E uma mistura de cultura que vai alem dos livros.",
    ),
    (
        "feiras literarias sao apenas para adultos?",
        "Nao! As principais feiras tem programacao para todas as idades. "
        "Ha sessoes infantis, juvenis e adultas, tornando-as otimas opcoes de passeio em familia.",
    ),
    (
        "como me inscrever em uma oficina de feira literaria?",
        "As inscricoes para oficinas costumam ser feitas pelo site oficial de cada feira, "
        "geralmente com vagas limitadas. Fique de olho nos sites com antecedencia "
        "pois as oficinas tem alta demanda.",
    ),
    (
        "as feiras literarias sao acessiveis para pessoas com deficiencia?",
        "As grandes feiras, como a Bienal do Livro SP e a FLIP, tem se preocupado cada vez mais "
        "com acessibilidade, oferecendo rampas, interpretes de Libras e materiais em Braille. "
        "Consulte os sites oficiais para detalhes de cada edicao.",
    ),
]


# ---------------------------------------------------------------------------
# Perguntas genericas (sem especificar cidade/edicao):
# retornam conceitos + pedido de especificacao para desambiguar.
# ---------------------------------------------------------------------------

_RESP_BIENAL_GENERICA = (
    "A Bienal do Livro e um grande festival cultural e literario que reune editoras, "
    "livrarias, autores e leitores para celebrar a leitura. "
    "No Brasil temos varias: Bienal de Sao Paulo, Bienal do Rio de Janeiro, "
    "Bienal Bahia (Salvador) e Bienal de Pernambuco (Recife). "
    "Sobre qual delas voce gostaria de saber mais?"
)

_RESP_BIENAL_DATA_GENERICA = (
    "Temos varias Bienais do Livro no Brasil, cada uma com seu calendario proprio: "
    "Sao Paulo (julho), Rio de Janeiro (setembro), Bahia (outubro) e Pernambuco (outubro). "
    "Sobre qual delas voce quer saber a data exata?"
)

_RESP_BIENAL_LOCAL_GENERICA = (
    "Existem Bienais do Livro em diferentes cidades brasileiras: "
    "Sao Paulo (Pavilhao do Anhembi - Av. Olavo Fontoura, 1209), "
    "Rio de Janeiro (Riocentro - Av. Salvador Allende, 6555), "
    "Salvador/BA (Centro de Convencoes da Bahia - Av. ACM, s/n) e "
    "Recife/PE (Centro de Convencoes de Pernambuco). Qual delas voce quer conhecer?"
)

GENERIC_TYPE_QA = [
    # Conceito de bienal sem especificar cidade
    ("o que e a bienal do livro?",           _RESP_BIENAL_GENERICA),
    ("o que e bienal do livro?",             _RESP_BIENAL_GENERICA),
    ("o que e bienal do livro",              _RESP_BIENAL_GENERICA),
    ("me fala sobre a bienal do livro",      _RESP_BIENAL_GENERICA),
    ("me conta sobre a bienal do livro",     _RESP_BIENAL_GENERICA),
    ("fala sobre a bienal do livro",         _RESP_BIENAL_GENERICA),
    ("quero saber sobre a bienal do livro",  _RESP_BIENAL_GENERICA),
    ("o que e a bienal?",                    _RESP_BIENAL_GENERICA),
    ("o que e uma bienal literaria?",        _RESP_BIENAL_GENERICA),
    ("o que sao as bienais do livro?",       _RESP_BIENAL_GENERICA),
    ("quais sao as bienais do livro no brasil?",  _RESP_BIENAL_GENERICA),
    ("quantas bienais do livro existem no brasil?", _RESP_BIENAL_GENERICA),
    ("bienal do livro o que e?",             _RESP_BIENAL_GENERICA),
    ("me explica o que e a bienal do livro", _RESP_BIENAL_GENERICA),

    # Data generica sem cidade
    ("quando e a bienal do livro?",          _RESP_BIENAL_DATA_GENERICA),
    ("qual a data da bienal do livro?",      _RESP_BIENAL_DATA_GENERICA),
    ("em que mes acontece a bienal do livro?", _RESP_BIENAL_DATA_GENERICA),
    ("quando vai ser a bienal do livro?",    _RESP_BIENAL_DATA_GENERICA),

    # Local generico sem cidade
    ("onde acontece a bienal do livro?",     _RESP_BIENAL_LOCAL_GENERICA),
    ("onde e a bienal do livro?",            _RESP_BIENAL_LOCAL_GENERICA),
    ("em que cidade e a bienal do livro?",   _RESP_BIENAL_LOCAL_GENERICA),

    # Conceito de festival literario
    (
        "o que e um festival literario?",
        "Um festival literario e um evento cultural dedicado a celebracao da leitura e da literatura, "
        "reunindo autores, editoras, livreiros e leitores. Costumam incluir debates, lancamentos de livros, "
        "oficinas e atividades culturais. No Brasil se destacam: FLIP (Paraty), FLIC (BH), FLOR (SP), "
        "Flipocos (Pocos de Caldas) e Festival Literario Catarinense.",
    ),
    (
        "o que e um festival literario brasileiro?",
        "Os festivais literarios brasileiros sao eventos culturais que celebram a leitura e reunem "
        "autores, editoras e leitores. Vao desde grandes bienais (SP, Rio, Bahia, Pernambuco) ate "
        "festivais intimistas como FLIP, FLIC e FLOR. Cada um tem sua identidade unica.",
    ),

    # Conceito de feira literaria
    (
        "o que e uma feira literaria?",
        "Uma feira literaria e um espaco de encontro entre leitores, autores e editoras "
        "para vender, lancar e debater livros. Podem durar dias ou semanas, com programacao "
        "cultural variada. As mais famosas no Brasil: Bienal SP, FLIP, FLIC, FLOR, "
        "Bienal Bahia, Bienal PE e Feira do Livro de Porto Alegre.",
    ),
    (
        "o que sao feiras literarias?",
        "Feiras literarias sao eventos culturais voltados para livros, leitura e literatura. "
        "Reunem editoras, autores e leitores em um so lugar, com debates, lancamentos, oficinas e vendas. "
        "No Brasil ha feiras em todas as regioes do pais.",
    ),
]


# ---------------------------------------------------------------------------
# Recomendacoes por genero literario.
# ---------------------------------------------------------------------------

GENRE_QA = [
    (
        f"voce recomenda alguma feira para quem gosta de {genero}?",
        f"Para quem aprecia {genero}, a Bienal do Livro SP costuma ter a maior variedade de titulos "
        f"e lancamentos nesse estilo. A FLIP tambem tem mesas tematicas e debates sobre diferentes "
        f"correntes literarias. Vale conferir a programacao antes de ir.",
    )
    for genero in GENEROS
]


# ---------------------------------------------------------------------------
# Perguntas fora do escopo do chatbot.
# ---------------------------------------------------------------------------

OUT_OF_SCOPE_QA = [
    (
        "qual o resultado do jogo de ontem?",
        "Desculpe, meu foco sao as feiras literarias brasileiras! "
        "Posso ajudar com datas, autores, ingressos e programacao de eventos literarios.",
    ),
    (
        "quanto vale um dolar hoje?",
        "Isso foge do meu dominio! Sou especialista em feiras literarias do Brasil. "
        "Posso ajudar com informacoes sobre Bienal, FLIP, FLIC e outros eventos.",
    ),
    (
        "me recomende um restaurante",
        "Restaurantes nao sao a minha especialidade, mas feiras literarias sim! "
        "Que tal saber mais sobre algum evento literario?",
    ),
    (
        "como fazer um bolo de chocolate?",
        "Receitas estao fora do meu alcance, mas se voce quiser, posso indicar "
        "livros de culinaria presentes nas feiras literarias.",
    ),
    (
        "qual o melhor time de futebol do brasil?",
        "Isso e muito controverso e foge do meu dominio! "
        "Mas posso dizer com certeza qual e o melhor evento literario para voce visitar. O que acha?",
    ),
]


# ---------------------------------------------------------------------------
# Afunilamento: respostas que pedem mais detalhes ao usuario.
# ---------------------------------------------------------------------------

FUNNEL_QA = [
    (
        "me fala mais sobre feiras literarias",
        "Claro! Sobre qual aspecto voce quer saber mais?\n"
        "- Datas e edicoes\n"
        "- Locais e cidades\n"
        "- Autores participantes\n"
        "- Ingressos e precos\n"
        "- Programacao e atividades",
    ),
    (
        "quero informacoes sobre feiras",
        "Posso ajudar! Voce quer saber sobre qual feira especificamente? "
        "Temos: Bienal SP, Bienal Rio, FLIP, FLIC, Feira POA, FLOR, "
        "Bienal Bahia, Bienal PE, Feira Unesp, Flipocos e Festival Literario SC, entre outras.",
    ),
    (
        "preciso de ajuda",
        "Claro! Sou especialista em feiras literarias brasileiras. "
        "Posso informar sobre datas, locais, programacao, ingressos e autores. O que deseja saber?",
    ),
]


# ---------------------------------------------------------------------------
# Aliases: variacoes coloquiais com nomes compostos parecidos (Bienal Rio vs SP).
# Garante cobertura explicita no dataset para os casos mais criticos.
# ---------------------------------------------------------------------------

# Referencias diretas aos dicionarios das feiras mais confundidas
_BIENAL_RIO = next(f for f in FEIRAS if f["sigla"] == "Bienal Rio")
_BIENAL_SP  = next(f for f in FEIRAS if f["sigla"] == "Bienal do Livro SP")

ALIAS_QA = [
    # Bienal do Livro do Rio (variacoes coloquiais)
    (
        "qual o endereco da Bienal do Livro do Rio?",
        f"O endereco da {_BIENAL_RIO['nome']} e: {_BIENAL_RIO['endereco']}. "
        f"Para informacoes de transporte e estacionamento, consulte {_BIENAL_RIO['site']}.",
    ),
    (
        "qual o endereco da Bienal do Livro do Rio de Janeiro?",
        f"O endereco da {_BIENAL_RIO['nome']} e: {_BIENAL_RIO['endereco']}. "
        f"Para informacoes de transporte e estacionamento, consulte {_BIENAL_RIO['site']}.",
    ),
    (
        "onde fica a Bienal do Livro do Rio?",
        f"A {_BIENAL_RIO['nome']} e realizada em {_BIENAL_RIO['local']}. "
        f"Endereco completo: {_BIENAL_RIO['endereco']}.",
    ),
    (
        "onde fica a Bienal do Livro do Rio de Janeiro?",
        f"A {_BIENAL_RIO['nome']} e realizada em {_BIENAL_RIO['local']}. "
        f"Endereco completo: {_BIENAL_RIO['endereco']}.",
    ),
    (
        "onde e a Bienal do Rio de Janeiro?",
        f"A {_BIENAL_RIO['nome']} acontece em {_BIENAL_RIO['local']} ({_BIENAL_RIO['endereco']}).",
    ),
    (
        "onde fica a Bienal do Rio de Janeiro?",
        f"A {_BIENAL_RIO['nome']} e realizada em {_BIENAL_RIO['local']}. "
        f"Endereco: {_BIENAL_RIO['endereco']}.",
    ),
    (
        "quando e a Bienal do Livro do Rio?",
        f"A {_BIENAL_RIO['nome']} geralmente acontece em {_BIENAL_RIO['mes']}. "
        f"Consulte {_BIENAL_RIO['site']} para as datas exatas.",
    ),
    (
        "quando e a Bienal do Livro do Rio de Janeiro?",
        f"A {_BIENAL_RIO['nome']} geralmente acontece em {_BIENAL_RIO['mes']}. "
        f"Consulte {_BIENAL_RIO['site']} para as datas exatas.",
    ),
    (
        "o que e a Bienal do Livro do Rio?",
        f"A {_BIENAL_RIO['nome']} e {_BIENAL_RIO['descricao']}. "
        f"Acontece em {_BIENAL_RIO['local']} no mes de {_BIENAL_RIO['mes']}. "
        f"Acesse {_BIENAL_RIO['site']} para mais informacoes.",
    ),
    (
        "quais autores ja foram convidados para a Bienal do Livro do Rio?",
        f"A {_BIENAL_RIO['nome']} ja recebeu como convidados nomes como "
        f"{_BIENAL_RIO['convidados_exemplos'][0]}, {_BIENAL_RIO['convidados_exemplos'][1]} e "
        f"{_BIENAL_RIO['convidados_exemplos'][2]}, entre outros. "
        f"Os convidados de cada edicao sao anunciados em {_BIENAL_RIO['site']}.",
    ),
    (
        "quem ja foi homenageado na Bienal do Livro do Rio?",
        f"A {_BIENAL_RIO['nome']} ja prestou homenagem a autores como "
        f"{_BIENAL_RIO['homenageados'][0]}, {_BIENAL_RIO['homenageados'][1]} e "
        f"{_BIENAL_RIO['homenageados'][2]}. "
        f"O homenageado de cada edicao e anunciado em {_BIENAL_RIO['site']}.",
    ),

    # Bienal do Livro de SP (variacoes com "de SP" / "Sao Paulo")
    (
        "onde fica a Bienal do Livro de Sao Paulo?",
        f"A {_BIENAL_SP['nome']} acontece em {_BIENAL_SP['local']}. "
        f"Endereco: {_BIENAL_SP['endereco']}.",
    ),
    (
        "qual o endereco da Bienal do Livro de Sao Paulo?",
        f"O endereco da {_BIENAL_SP['nome']} e: {_BIENAL_SP['endereco']}. "
        f"Para informacoes de transporte e estacionamento, consulte {_BIENAL_SP['site']}.",
    ),
    (
        "quando e a Bienal do Livro de Sao Paulo?",
        f"A {_BIENAL_SP['nome']} geralmente acontece em {_BIENAL_SP['mes']}. "
        f"Consulte {_BIENAL_SP['site']} para as datas exatas.",
    ),
]


# ---------------------------------------------------------------------------
# Geracao do CSV
# ---------------------------------------------------------------------------

def gerar_linhas() -> list:
    """
    Compila todas as listas de pares (pergunta, resposta) em uma unica lista.
    Ordem das etapas:
        1. Templates estaticos (saudacoes, despedidas, agradecimentos)
        2. Templates dinamicos expandidos por cada feira
        3. Perguntas gerais
        4. Perguntas genericas sem feira especifica
        5. Recomendacoes por genero
        6. Perguntas fora de escopo
        7. Afunilamento
        8. Aliases / variacoes coloquiais
    """
    linhas = []

    # 1. Templates estaticos
    for inputs, response in TEMPLATES:
        for user_input in inputs:
            linhas.append((user_input, response))

    # 2. Templates dinamicos: expande cada template para cada feira
    for feira in FEIRAS:
        for templates_input, template_resp in DYNAMIC_TEMPLATES:
            for tpl in templates_input:
                user_input = tpl.format(
                    sigla=feira["sigla"],
                    nome=feira["nome"],
                )
                # Sorteia homenageados e convidados para variar o dataset
                hom  = random.sample(feira["homenageados"],        min(3, len(feira["homenageados"])))
                conv = random.sample(feira["convidados_exemplos"], min(3, len(feira["convidados_exemplos"])))

                response = template_resp.format(
                    nome=feira["nome"],
                    sigla=feira["sigla"],
                    local=feira["local"],
                    endereco=feira["endereco"],
                    mes=feira["mes"],
                    site=feira["site"],
                    descricao=feira["descricao"],
                    hom1=hom[0],
                    hom2=hom[1] if len(hom) > 1 else hom[0],
                    hom3=hom[2] if len(hom) > 2 else hom[0],
                    conv1=conv[0],
                    conv2=conv[1] if len(conv) > 1 else conv[0],
                    conv3=conv[2] if len(conv) > 2 else conv[0],
                )
                linhas.append((user_input, response))

    # 3. Perguntas gerais
    linhas.extend(GENERAL_QA)

    # 4. Perguntas genericas sem feira especifica
    linhas.extend(GENERIC_TYPE_QA)

    # 5. Recomendacoes por genero
    linhas.extend(GENRE_QA)

    # 6. Fora de escopo
    linhas.extend(OUT_OF_SCOPE_QA)

    # 7. Afunilamento
    linhas.extend(FUNNEL_QA)

    # 8. Aliases / variacoes coloquiais criticas
    linhas.extend(ALIAS_QA)

    return linhas


def gerar_dataset(output_path: str = "data/feiras_literarias.csv", n_target: int = 1000):
    """
    Gera o arquivo CSV com os pares (user_input, response).

    Args:
        output_path: caminho de saida do CSV
        n_target:    numero minimo de linhas desejado no dataset.
                     Se necessario, completa com variacoes aleatorias.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    linhas = gerar_linhas()

    # Completa com variacoes aleatorias se abaixo do minimo desejado
    while len(linhas) < n_target:
        feira = random.choice(FEIRAS)
        conv  = random.sample(feira["convidados_exemplos"], min(2, len(feira["convidados_exemplos"])))

        variacao = random.choice([
            (
                f"tem como me informar sobre a {feira['sigla']}?",
                f"Claro! A {feira['nome']} acontece em {feira['mes']}, em {feira['local']}. "
                f"Para mais detalhes, acesse {feira['site']}.",
            ),
            (
                f"quero saber tudo sobre a {feira['sigla']}",
                f"A {feira['nome']} e {feira['descricao']}. "
                f"Ocorre em {feira['mes']} em {feira['local']}. "
                f"Mais informacoes em {feira['site']}.",
            ),
            (
                f"vale a pena ir na {feira['sigla']}?",
                f"Com certeza! A {feira['nome']} e {feira['descricao']}. "
                f"Confira a programacao em {feira['site']} e planeje sua visita.",
            ),
            (
                f"qual o endereco da {feira['sigla']}?",
                f"A {feira['nome']} acontece em: {feira['endereco']}. "
                f"Mais detalhes logisticos em {feira['site']}.",
            ),
            (
                f"quais autores ja foram convidados para a {feira['sigla']}?",
                f"A {feira['nome']} ja recebeu como convidados nomes como {conv[0]} e {conv[1]}, "
                f"entre outros autores. Os convidados de cada nova edicao sao anunciados em {feira['site']}.",
            ),
        ])
        linhas.append(variacao)

    # Embaralha para distribuir os tipos uniformemente no CSV
    random.shuffle(linhas)

    # Salva em UTF-8 para preservar acentos nas respostas
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["user_input", "response"])
        writer.writerows(linhas)

    print(f"Dataset gerado com {len(linhas)} linhas em '{output_path}'.")


if __name__ == "__main__":
    gerar_dataset()
