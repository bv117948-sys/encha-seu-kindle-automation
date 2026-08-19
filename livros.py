import re
import time

from playwright.sync_api import (
    Locator,
    Page,
)

from config import (
    TIMEOUT_CONFIRMACAO,
)


def normalizar_preco(
    preco: str,
) -> str:

    return (
        preco
        .replace("\xa0", " ")
        .replace(" ", "")
        .strip()
    )


def eh_compra_gratuita(
    preco: str | None,
) -> bool:

    if preco is None:

        return False

    return (
        normalizar_preco(
            preco
        )
        == "R$0,00"
    )


def obter_titulo_produto(
    page: Page,
    fallback: str,
) -> str:

    seletores = [
        "#productTitle",
        "h1 span",
        "h1",
    ]

    for seletor in seletores:

        elemento = page.locator(
            seletor
        )

        if elemento.count() == 0:
            continue

        try:

            titulo = (
                elemento
                .first
                .inner_text()
                .strip()
            )

            if titulo:

                return titulo

        except Exception:

            continue

    return fallback


def localizar_bloco_kindle(
    page: Page,
) -> Locator | None:

    seletores = [
        '[data-cel-widget="tmm-grid-swatch-KINDLE"]',
        '[data-cel-widget*="KINDLE"]',
        "#tmm-grid-swatch-KINDLE",
    ]

    for seletor in seletores:

        bloco = page.locator(
            seletor
        )

        if bloco.count() > 0:

            return bloco.first

    return None


def obter_preco_real_compra(
    page: Page,
) -> str | None:

    bloco = localizar_bloco_kindle(
        page
    )

    if bloco is None:

        print(
            "Bloco Kindle nao encontrado."
        )

        return None

    try:

        texto = (
            bloco
            .inner_text()
            .replace(
                "\xa0",
                " ",
            )
        )

    except Exception:

        return None


    # ========================================================
    # PRIMEIRA OPCAO
    # ========================================================

    resultado_compra = re.search(
        r"R\$\s*"
        r"\d{1,3}"
        r"(?:\.\d{3})*,\d{2}"
        r"\s*para comprar",
        texto,
        re.IGNORECASE,
    )

    if resultado_compra:

        preco = re.search(
            r"R\$\s*"
            r"\d{1,3}"
            r"(?:\.\d{3})*,\d{2}",
            resultado_compra.group(0),
        )

        if preco:

            return (
                preco
                .group(0)
                .strip()
            )


    # ========================================================
    # FALLBACK SOMENTE NO BLOCO KINDLE
    # ========================================================

    precos = bloco.locator(
        '.slot-price [aria-label^="R$"], '
        '.a-price [aria-hidden="true"], '
        '.a-color-price'
    )

    for indice in range(
        precos.count()
    ):

        elemento = precos.nth(
            indice
        )

        try:

            valor = (
                elemento
                .get_attribute(
                    "aria-label"
                )
                or
                elemento.inner_text()
                or ""
            )

        except Exception:

            continue

        resultado = re.search(
            r"R\$\s*"
            r"\d{1,3}"
            r"(?:\.\d{3})*,\d{2}",
            valor.replace(
                "\xa0",
                " ",
            ),
        )

        if resultado:

            return (
                resultado
                .group(0)
                .strip()
            )

    return None


def localizar_botao_compra(
    page: Page,
) -> Locator | None:

    seletores = [
        "#one-click-button",
        'input[name="submit.buy-now"]',
    ]

    for seletor in seletores:

        botao = page.locator(
            seletor
        )

        if botao.count() == 0:
            continue

        try:

            if botao.first.is_visible():

                return botao.first

        except Exception:

            continue

    return None


def pode_adquirir(
    page: Page,
) -> bool:

    return (
        localizar_botao_compra(
            page
        )
        is not None
    )


def confirmar_aquisicao(
    page: Page,
) -> bool:

    padroes = [
        r"ler agora",
        r"obrigad[oa]",
    ]

    for padrao in padroes:

        locator = page.get_by_text(
            re.compile(
                padrao,
                re.IGNORECASE,
            )
        )

        try:

            locator.first.wait_for(
                state="visible",
                timeout=TIMEOUT_CONFIRMACAO,
            )

            return True

        except Exception:

            continue

    return False


def adquirir_livro(
    page: Page,
) -> tuple[bool, str]:

    # O preco e verificado NOVAMENTE
    # imediatamente antes do clique.

    preco = obter_preco_real_compra(
        page
    )

    print(
        "Preco final para comprar:",
        preco,
    )

    if not eh_compra_gratuita(
        preco
    ):

        return (
            False,
            "preco_nao_gratuito",
        )

    botao = localizar_botao_compra(
        page
    )

    if botao is None:

        return (
            False,
            "botao_nao_encontrado",
        )

    try:

        botao.click(
            timeout=15000,
        )

    except Exception as erro:

        return (
            False,
            f"erro_no_clique: {erro}",
        )

    time.sleep(
        1.0
    )

    if confirmar_aquisicao(
        page
    ):

        return (
            True,
            "adquirido",
        )

    return (
        False,
        "confirmacao_nao_encontrada",
    )