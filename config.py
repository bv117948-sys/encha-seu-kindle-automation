from pathlib import Path


# ============================================================
# AMAZON
# ============================================================

BASE_URL = "https://www.amazon.com.br"


# ============================================================
# IDENTIFICACAO DO EVENTO
# ============================================================

# Mude este nome a cada nova edicao.
#
# Exemplo:
# NOME_EVENTO = "esk_outubro_2026"

NOME_EVENTO = "livros_kindle"


# Cole aqui o link da edicao ATUAL.
#
# Fora do periodo do evento, deixe vazio:
#
# URL_EVENTO = ""
# link abaixo apenas para testes
URL_EVENTO = "https://www.amazon.com.br/s?k=ebooks+gratis+hoje&__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&ref=nb_sb_noss"


# Links adicionais opcionais da edicao atual.
#
# Exemplo:
#
# URLS_EXTRAS = [
#     "https://link.amazon/OUTRO_LINK",
# ]

URLS_EXTRAS: list[str] = []


# ============================================================
# LINKS HISTORICOS / EXEMPLOS
# ============================================================

# Links usados durante o desenvolvimento do projeto.
#
# Eles podem estar expirados e NAO sao usados automaticamente.

# Antiga vitrine/listas:
# https://link.amazon/B0imHZ0IC

# Antiga pagina do ESK:
# https://link.amazon/B0iRPRvta


# ============================================================
# ARQUIVOS
# ============================================================

ARQUIVO_SESSAO = Path("auth.json")

DIRETORIO_DADOS = Path(
    "dados_execucao"
)

ARQUIVO_CANDIDATOS = (
    DIRETORIO_DADOS
    / f"candidatos_{NOME_EVENTO}.json"
)

ARQUIVO_LIVROS_GRATIS = (
    DIRETORIO_DADOS
    / f"livros_gratis_{NOME_EVENTO}.json"
)

ARQUIVO_RELATORIO = (
    DIRETORIO_DADOS
    / f"relatorio_{NOME_EVENTO}.json"
)

ARQUIVO_PROGRESSO = (
    DIRETORIO_DADOS
    / f"progresso_{NOME_EVENTO}.json"
)


# ============================================================
# FILTROS
# ============================================================

# Primeiro tenta descobrir automaticamente
# as categorias existentes na pagina.

DESCOBRIR_CATEGORIAS = True


# Caso a descoberta automatica falhe,
# usa estas categorias como fallback.

CATEGORIAS_FALLBACK = [
    "Romance",
    "Jovens e Adolescentes",
    "Fantasia",
    "Suspense",
    "Horror",
    "Ficção",
    "Não Ficção",
    "Outros",
    "Romances Hot",
]


# "Todos" normalmente repete produtos
# encontrados nas demais categorias.

INCLUIR_CATEGORIA_TODOS = False


# ============================================================
# MODOS DE EXECUCAO
# ============================================================

# PRIMEIRO TESTE DE CADA NOVA EDICAO:
#
# True:
# percorre filtros, usa Carregar mais
# e salva os candidatos.
#
# Nao abre cada livro individualmente.

MODO_COLETA_APENAS = False


# Deve permanecer False no GitHub.
#
# So ative depois de testar a nova edicao.

AUTO_ADQUIRIR = True


# ============================================================
# TESTE RAPIDO
# ============================================================

MODO_TESTE = False

LIMITE_CATEGORIAS_TESTE = 2

LIMITE_LIVROS_TESTE = 20


# ============================================================
# CARREGAR MAIS
# ============================================================

MAX_CLIQUES_CARREGAR_MAIS = 200

MAX_TENTATIVAS_SEM_CRESCIMENTO = 3


# ============================================================
# TEMPOS
# ============================================================

TEMPO_APOS_FILTRO = 1.5

TEMPO_APOS_CARREGAR_MAIS = 1.0

TEMPO_ENTRE_LIVROS = 1.0

TEMPO_ENTRE_TENTATIVAS = 3.0


# ============================================================
# TIMEOUTS
# ============================================================

TIMEOUT_PADRAO = 12000

TIMEOUT_NAVEGACAO = 25000

TIMEOUT_CONFIRMACAO = 12000

MAX_TENTATIVAS_NAVEGACAO = 3