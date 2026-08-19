import time
from urllib.parse import urljoin

from playwright.sync_api import Page

from config import (
    BASE_URL,
    MAX_TENTATIVAS_NAVEGACAO,
    TEMPO_ENTRE_TENTATIVAS,
    TIMEOUT_NAVEGACAO,
)


def criar_url_completa(
    url: str,
) -> str:

    if not url:
        return BASE_URL

    return urljoin(
        BASE_URL,
        url,
    )


def navegar_com_tentativas(
    page: Page,
    url: str,
    max_tentativas: int = MAX_TENTATIVAS_NAVEGACAO,
) -> bool:

    destino = criar_url_completa(
        url
    )

    for tentativa in range(
        1,
        max_tentativas + 1,
    ):

        try:

            print(
                f"Tentativa de carregamento "
                f"{tentativa}/{max_tentativas}"
            )

            page.goto(
                destino,
                wait_until="domcontentloaded",
                timeout=TIMEOUT_NAVEGACAO,
            )

            return True

        except Exception as erro:

            print(
                "Falha ao carregar a pagina:",
                erro,
            )

            if tentativa < max_tentativas:

                time.sleep(
                    TEMPO_ENTRE_TENTATIVAS
                )

    return False