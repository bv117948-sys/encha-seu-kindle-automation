from pathlib import Path
from playwright.sync_api import sync_playwright

ARQUIVO_SESSAO = Path("auth.json")


def run():
    if not ARQUIVO_SESSAO.exists():
        print("Arquivo auth.json não encontrado.")
        print("Execute primeiro: python login.py")
        return

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)

        context = browser.new_context(
            storage_state=str(ARQUIVO_SESSAO))

        page = context.new_page()
        page.set_default_timeout(10000)

        page.goto(
            "https://www.amazon.com.br",
            wait_until="domcontentloaded"
        )

        pesquisa = page.get_by_role("searchbox")
        pesquisa.fill("livros romance kindle grátis")
        pesquisa.press("Enter")

        page.wait_for_load_state("domcontentloaded")

        resultados = page.locator(
            'div[data-component-type="s-search-result"]'
        )

        print("Resultados encontrados:", resultados.count())
        quantidade = resultados.count()
        for i in range(quantidade):
            resultado = resultados.nth(i)

            titulo = resultado.locator("h2").get_attribute("aria-label")
            link = resultado.locator("a").first.get_attribute("href")
            preco = resultado.locator("span.a-price span.a-offscreen")

            if preco.count() > 0:
                preco = preco.first.inner_text()
            else:
                preco = "Preço não disponível"
            if preco == "R$ 0,00":
                print(f"gratis: {titulo}")
                print(f"Link: {link}")

            print(f"{i + 1}. {titulo} - {link} - {preco}")

        print("Pesquisa realizada!")

        input("Confira os resultados e pressione Enter para fechar...")

        browser.close()


run()