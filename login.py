from playwright.sync_api import (
    Playwright,
    sync_playwright,
)

from config import (
    BASE_URL,
)


def run(
    playwright: Playwright,
) -> None:

    browser = (
        playwright
        .chromium
        .launch(
            headless=False
        )
    )

    context = (
        browser
        .new_context()
    )

    page = context.new_page()

    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
    )

    print(
        "\nFaca o login normalmente "
        "na sua conta Amazon."
    )

    input(
        "\nQuando o login estiver concluido, "
        "pressione Enter no terminal..."
    )

    context.storage_state(
        path="auth.json"
    )

    print(
        "\nSessao salva em auth.json."
    )

    browser.close()


if __name__ == "__main__":

    with sync_playwright() as playwright:

        run(
            playwright
        )