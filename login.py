from playwright.sync_api import sync_playwright, Playwright


def run(playwright: Playwright):
    chromium = playwright.chromium
    browser = chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.amazon.com.br")

    input("Faça o login e pressione Enter no terminal para continuar...")

    context.storage_state(path="auth.json")
    print("Sessão salva com sucesso!")

    input("Pressione Enter para fechar o navegador...")
    browser.close()


with sync_playwright() as playwright:
    run(playwright)