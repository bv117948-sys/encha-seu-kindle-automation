import re
import time
from urllib.parse import urljoin

from playwright.sync_api import (
    Locator,
    Page,
)

from config import (
    BASE_URL,
    CATEGORIAS_FALLBACK,
    DESCOBRIR_CATEGORIAS,
    INCLUIR_CATEGORIA_TODOS,
    LIMITE_CATEGORIAS_TESTE,
    MAX_CLIQUES_CARREGAR_MAIS,
    MAX_TENTATIVAS_SEM_CRESCIMENTO,
    MODO_TESTE,
    TEMPO_APOS_CARREGAR_MAIS,
    TEMPO_APOS_FILTRO,
)


# ============================================================
# ASIN
# ============================================================


def extrair_asin(
    link: str,
) -> str | None:

    if not link:
        return None

    padroes = [
        r"/dp/([A-Z0-9]{10})",
        r"/gp/product/([A-Z0-9]{10})",
        r"[?&]asin=([A-Z0-9]{10})",
        r"[?&]ASIN\.1=([A-Z0-9]{10})",
    ]

    for padrao in padroes:

        resultado = re.search(
            padrao,
            link,
            re.IGNORECASE,
        )

        if resultado:

            return (
                resultado
                .group(1)
                .upper()
            )

    return None


def chave_livro(
    link: str,
) -> str:

    asin = extrair_asin(
        link
    )

    if asin:

        return asin

    return urljoin(
        BASE_URL,
        link,
    )


# ============================================================
# DUPLICADOS
# ============================================================


def remover_duplicados(
    livros: list[dict[str, str]],
) -> list[dict[str, str]]:

    resultado: list[
        dict[str, str]
    ] = []

    vistos: set[str] = set()

    for livro in livros:

        link = livro.get(
            "link",
            "",
        )

        if not link:
            continue

        chave = chave_livro(
            link
        )

        if chave in vistos:
            continue

        vistos.add(
            chave
        )

        resultado.append(
            livro
        )

    return resultado


# ============================================================
# FILTROS
# ============================================================


def localizar_radios_categoria(
    page: Page,
) -> Locator:

    return page.locator(
        'input[type="radio"]'
        '[name="dcl-refinement-category"]'
    )


def descobrir_categorias(
    page: Page,
) -> list[str]:

    radios = localizar_radios_categoria(
        page
    )

    categorias: list[str] = []

    for indice in range(
        radios.count()
    ):

        radio = radios.nth(
            indice
        )

        try:

            nome = (
                radio
                .get_attribute(
                    "aria-label"
                )
                or ""
            ).strip()

        except Exception:

            continue

        if not nome:
            continue

        if (
            not INCLUIR_CATEGORIA_TODOS
            and nome.casefold() == "todos"
        ):

            continue

        if nome not in categorias:

            categorias.append(
                nome
            )

    return categorias


def obter_categorias(
    page: Page,
) -> list[str]:

    categorias: list[str] = []

    if DESCOBRIR_CATEGORIAS:

        categorias = descobrir_categorias(
            page
        )

    if not categorias:

        print(
            "Descoberta automatica falhou."
        )

        print(
            "Usando categorias de fallback."
        )

        categorias = list(
            CATEGORIAS_FALLBACK
        )

    if MODO_TESTE:

        categorias = categorias[
            :LIMITE_CATEGORIAS_TESTE
        ]

    print(
        "\nCategorias encontradas:",
        len(categorias),
    )

    for categoria in categorias:

        print(
            "-",
            categoria,
        )

    return categorias


def localizar_categoria(
    page: Page,
    categoria: str,
) -> Locator | None:

    radios = localizar_radios_categoria(
        page
    )

    alvo = (
        categoria
        .strip()
        .casefold()
    )

    for indice in range(
        radios.count()
    ):

        radio = radios.nth(
            indice
        )

        try:

            nome = (
                radio
                .get_attribute(
                    "aria-label"
                )
                or ""
            ).strip()

        except Exception:

            continue

        if nome.casefold() == alvo:

            return radio

    return None


def selecionar_categoria(
    page: Page,
    categoria: str,
) -> bool:

    radio = localizar_categoria(
        page,
        categoria,
    )

    if radio is None:

        print(
            "Categoria nao encontrada:",
            categoria,
        )

        return False

    try:

        radio.scroll_into_view_if_needed()

        radio.check(
            force=True,
            timeout=10000,
        )

        print(
            "\nFiltro selecionado:",
            categoria,
        )

        time.sleep(
            TEMPO_APOS_FILTRO
        )

        return True

    except Exception as erro:

        print(
            "Falha ao selecionar categoria:",
            categoria,
        )

        print(
            erro
        )

        return False


# ============================================================
# CARDS DE PRODUTOS
# ============================================================


def localizar_cards_produtos(
    page: Page,
) -> Locator:

    # IMPORTANTE:
    #
    # Nao coletamos mais todos os links /dp/
    # da pagina inteira.
    #
    # Isso evita:
    # - carrinho
    # - recomendacoes
    # - historico
    # - produtos de banners
    #
    # So consideramos elementos que possuem
    # um data-asin valido.

    return page.locator(
        '[data-asin]:not([data-asin=""])'
    )


def obter_asin_card(
    card: Locator,
) -> str | None:

    try:

        asin = (
            card
            .get_attribute(
                "data-asin"
            )
            or ""
        ).strip().upper()

    except Exception:

        return None

    if not asin:
        return None

    if len(asin) != 10:
        return None

    return asin


def localizar_link_produto_card(
    card: Locator,
    asin: str,
) -> Locator | None:

    links = card.locator(
        'a[href*="/dp/"], '
        'a[href*="/gp/product/"]'
    )

    quantidade = links.count()

    for indice in range(
        quantidade
    ):

        link = links.nth(
            indice
        )

        try:

            href = (
                link
                .get_attribute(
                    "href"
                )
            )

        except Exception:

            continue

        if not href:
            continue

        asin_link = extrair_asin(
            href
        )

        if asin_link is None:
            continue

        # O link precisa ser do MESMO produto
        # indicado pelo data-asin do card.

        if asin_link.upper() == asin:

            return link

    return None


# ============================================================
# CONTAGEM DE PRODUTOS
# ============================================================


def quantidade_produtos(
    page: Page,
) -> int:

    cards = localizar_cards_produtos(
        page
    )

    asins: set[str] = set()

    for indice in range(
        cards.count()
    ):

        card = cards.nth(
            indice
        )

        asin = obter_asin_card(
            card
        )

        if asin is None:
            continue

        link = localizar_link_produto_card(
            card,
            asin,
        )

        if link is None:
            continue

        asins.add(
            asin
        )

    return len(
        asins
    )


# ============================================================
# CARREGAR MAIS
# ============================================================


def localizar_carregar_mais(
    page: Page,
) -> Locator | None:

    # Seletor encontrado no HTML real
    # da pagina do ESK.

    seletores = [
        (
            '[data-action="dcl-load-more"] '
            'input.a-button-input'
        ),
        '[data-action="dcl-load-more"]',
    ]

    for seletor in seletores:

        locator = page.locator(
            seletor
        )

        if locator.count() == 0:
            continue

        try:

            if locator.first.is_visible():

                return locator.first

        except Exception:

            continue

    return None


def carregar_todos_resultados(
    page: Page,
) -> None:

    print(
        "\nCarregando todos os resultados..."
    )

    sem_crescimento = 0

    for numero in range(
        1,
        MAX_CLIQUES_CARREGAR_MAIS + 1,
    ):

        botao = localizar_carregar_mais(
            page
        )

        if botao is None:

            print(
                "Nao ha mais botao "
                "'Carregar mais'."
            )

            break

        antes = quantidade_produtos(
            page
        )

        print(
            f"Carregar mais #{numero}"
        )

        print(
            "Produtos antes:",
            antes,
        )

        try:

            botao.scroll_into_view_if_needed()

            time.sleep(
                0.3
            )

            botao.click(
                timeout=10000,
            )

        except Exception as erro:

            print(
                "Falha ao clicar "
                "em Carregar mais:"
            )

            print(
                erro
            )

            break

        time.sleep(
            TEMPO_APOS_CARREGAR_MAIS
        )

        depois = quantidade_produtos(
            page
        )

        print(
            "Produtos depois:",
            depois,
        )

        if depois > antes:

            sem_crescimento = 0

        else:

            sem_crescimento += 1

            print(
                "Nenhum produto novo "
                "detectado."
            )

        if (
            sem_crescimento
            >= MAX_TENTATIVAS_SEM_CRESCIMENTO
        ):

            print(
                "A pagina parou de adicionar "
                "novos produtos."
            )

            break


# ============================================================
# TITULO
# ============================================================


def extrair_titulo_card(
    card: Locator,
    link: Locator,
    asin: str,
) -> str:

    seletores = [
        '[data-cy="title-recipe"] h2',
        '[data-cy="title-recipe"]',
        ".product-title-text",
        "h2",
        "h3",
    ]

    for seletor in seletores:

        elemento = card.locator(
            seletor
        )

        if elemento.count() == 0:
            continue

        try:

            titulo = (
                elemento
                .first
                .get_attribute(
                    "aria-label"
                )
                or
                elemento
                .first
                .inner_text()
                or ""
            ).strip()

        except Exception:

            continue

        if titulo:

            return titulo

    # ========================================================
    # LINK
    # ========================================================

    for atributo in [
        "aria-label",
        "title",
    ]:

        try:

            titulo = (
                link
                .get_attribute(
                    atributo
                )
                or ""
            ).strip()

        except Exception:

            titulo = ""

        if titulo:

            return titulo

    try:

        titulo = (
            link
            .inner_text()
            .strip()
        )

        if titulo:

            return titulo

    except Exception:

        pass

    return (
        f"Produto {asin}"
    )


# ============================================================
# COLETAR PRODUTOS
# ============================================================


def coletar_produtos_visiveis(
    page: Page,
    origem: str,
) -> list[dict[str, str]]:

    livros: list[
        dict[str, str]
    ] = []

    vistos: set[str] = set()

    cards = localizar_cards_produtos(
        page
    )

    print(
        "\nCards com data-asin encontrados:",
        cards.count(),
    )

    for indice in range(
        cards.count()
    ):

        card = cards.nth(
            indice
        )

        asin = obter_asin_card(
            card
        )

        if asin is None:
            continue

        if asin in vistos:
            continue

        link = localizar_link_produto_card(
            card,
            asin,
        )

        if link is None:
            continue

        try:

            href = (
                link
                .get_attribute(
                    "href"
                )
            )

        except Exception:

            continue

        if not href:
            continue

        # Segunda verificacao.
        asin_link = extrair_asin(
            href
        )

        if asin_link is None:
            continue

        if asin_link.upper() != asin:
            continue

        titulo = extrair_titulo_card(
            card,
            link,
            asin,
        )

        vistos.add(
            asin
        )

        livros.append(
            {
                "titulo": titulo,
                "link": urljoin(
                    BASE_URL,
                    href,
                ),
                "origem": origem,
            }
        )

    livros = remover_duplicados(
        livros
    )

    print(
        "Produtos validos coletados:",
        len(livros),
    )

    return livros


# ============================================================
# UMA CATEGORIA
# ============================================================


def coletar_categoria(
    page: Page,
    categoria: str,
) -> list[dict[str, str]]:

    print(
        "\n================================"
    )

    print(
        "CATEGORIA:",
        categoria,
    )

    print(
        "================================"
    )

    selecionou = selecionar_categoria(
        page,
        categoria,
    )

    if not selecionou:
        return []

    carregar_todos_resultados(
        page
    )

    livros = coletar_produtos_visiveis(
        page,
        origem=f"esk_{categoria}",
    )

    print(
        categoria,
        ":",
        len(livros),
        "produtos",
    )

    return livros


# ============================================================
# TODAS AS CATEGORIAS
# ============================================================


def coletar_todas_categorias_esk(
    page: Page,
) -> list[dict[str, str]]:

    categorias = obter_categorias(
        page
    )

    todos: list[
        dict[str, str]
    ] = []

    for indice, categoria in enumerate(
        categorias,
        start=1,
    ):

        print(
            "\n--------------------------------"
        )

        print(
            f"Categoria "
            f"{indice}/"
            f"{len(categorias)}"
        )

        livros = coletar_categoria(
            page,
            categoria,
        )

        todos.extend(
            livros
        )

        todos = remover_duplicados(
            todos
        )

        print(
            "\nTotal unico acumulado:",
            len(todos),
        )

    print(
        "\n================================"
    )

    print(
        "COLETA FINALIZADA"
    )

    print(
        "Total unico:",
        len(todos),
    )

    print(
        "================================"
    )

    return remover_duplicados(
        todos
    )


# ============================================================
# PAGINAS SEM FILTROS
# ============================================================


def coletar_pagina_sem_filtros(
    page: Page,
    origem: str,
) -> list[dict[str, str]]:

    print(
        "\nPagina sem filtros do ESK."
    )

    carregar_todos_resultados(
        page
    )

    livros = coletar_produtos_visiveis(
        page,
        origem=origem,
    )

    return remover_duplicados(
        livros
    )