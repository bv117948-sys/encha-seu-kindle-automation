import time

from playwright.sync_api import (
    Page,
    sync_playwright,
)

from config import (
    ARQUIVO_CANDIDATOS,
    ARQUIVO_LIVROS_GRATIS,
    ARQUIVO_SESSAO,
    AUTO_ADQUIRIR,
    LIMITE_LIVROS_TESTE,
    MODO_COLETA_APENAS,
    MODO_TESTE,
    TEMPO_ENTRE_LIVROS,
    TIMEOUT_PADRAO,
    URL_EVENTO,
    URLS_EXTRAS,
)

from coleta import (
    chave_livro,
    coletar_pagina_sem_filtros,
    coletar_todas_categorias_esk,
    localizar_radios_categoria,
    remover_duplicados,
)

from livros import (
    adquirir_livro,
    eh_compra_gratuita,
    obter_preco_real_compra,
    obter_titulo_produto,
    pode_adquirir,
)

from navegação import (
    navegar_com_tentativas,
)

from relatorios import (
    carregar_progresso,
    salvar_json,
    salvar_progresso,
    salvar_relatorio,
)


def criar_relatorio() -> dict[
    str,
    list[dict[str, str]]
]:

    return {
        "gratuitos_reais": [],
        "adquiridos": [],
        "pagos_ignorados": [],
        "ja_adquiridos": [],
        "preco_nao_identificado": [],
        "falhas_conexao": [],
        "falhas_aquisicao": [],
    }


# ============================================================
# VALIDACAO
# ============================================================


def validar_configuracao() -> bool:

    if not URL_EVENTO.strip():

        print(
            "\nNenhum ESK ativo foi configurado."
        )

        print(
            "Quando uma nova edicao estiver "
            "disponivel, cole o link em "
            "URL_EVENTO no config.py."
        )

        return False

    if not ARQUIVO_SESSAO.exists():

        print(
            "\nauth.json nao encontrado."
        )

        print(
            "Execute primeiro:"
        )

        print(
            "python login.py"
        )

        return False

    return True


# ============================================================
# COLETA DE UMA FONTE
# ============================================================


def coletar_fonte(
    page: Page,
    url: str,
    origem: str,
) -> list[dict[str, str]]:

    print(
        f"\nAbrindo fonte: {origem}"
    )

    if not navegar_com_tentativas(
        page,
        url,
    ):

        return []

    filtros = localizar_radios_categoria(
        page
    )

    if filtros.count() > 0:

        print(
            "Filtros detectados:",
            filtros.count(),
        )

        return (
            coletar_todas_categorias_esk(
                page
            )
        )

    print(
        "Nenhum filtro de categoria "
        "detectado."
    )

    print(
        "Coletando a pagina "
        "como uma lista unica."
    )

    return coletar_pagina_sem_filtros(
        page,
        origem=origem,
    )


# ============================================================
# EXECUCAO
# ============================================================


def run() -> None:

    if not validar_configuracao():

        return

    processados = (
        carregar_progresso()
    )

    relatorio = criar_relatorio()

    print(
        "\nItens ja processados nesta edicao:",
        len(processados),
    )

    with sync_playwright() as playwright:

        browser = (
            playwright
            .chromium
            .launch(
                headless=False
            )
        )

        context = browser.new_context(
            storage_state=str(
                ARQUIVO_SESSAO
            )
        )

        page = context.new_page()

        page.set_default_timeout(
            TIMEOUT_PADRAO
        )


        # ====================================================
        # COLETA PRINCIPAL
        # ====================================================

        candidatos: list[
            dict[str, str]
        ] = []

        candidatos.extend(
            coletar_fonte(
                page,
                URL_EVENTO,
                origem="evento_principal",
            )
        )


        # ====================================================
        # FONTES EXTRAS
        # ====================================================

        for indice, url_extra in enumerate(
            URLS_EXTRAS,
            start=1,
        ):

            if not url_extra.strip():
                continue

            candidatos.extend(
                coletar_fonte(
                    page,
                    url_extra,
                    origem=(
                        f"fonte_extra_{indice}"
                    ),
                )
            )


        # ====================================================
        # DEDUPLICACAO
        # ====================================================

        candidatos = remover_duplicados(
            candidatos
        )

        if MODO_TESTE:

            candidatos = candidatos[
                :LIMITE_LIVROS_TESTE
            ]

        salvar_json(
            ARQUIVO_CANDIDATOS,
            candidatos,
        )

        print(
            "\n================================"
        )

        print(
            "TOTAL UNICO DE CANDIDATOS:",
            len(candidatos),
        )

        print(
            "================================"
        )


        # ====================================================
        # MODO COLETA
        # ====================================================

        if MODO_COLETA_APENAS:

            print(
                "\nMODO_COLETA_APENAS = True"
            )

            print(
                "Nenhum livro sera aberto "
                "ou adquirido."
            )

            print(
                "Candidatos salvos em:",
                ARQUIVO_CANDIDATOS,
            )

            context.close()

            browser.close()

            return


        # ====================================================
        # VALIDACAO / AQUISICAO
        # ====================================================

        gratuitos: list[
            dict[str, str]
        ] = []

        for indice, livro in enumerate(
            candidatos,
            start=1,
        ):

            chave = chave_livro(
                livro["link"]
            )

            if chave in processados:

                print(
                    f"\n{indice}/"
                    f"{len(candidatos)} "
                    "- ja concluido "
                    "nesta edicao."
                )

                continue

            print(
                "\n--------------------------------"
            )

            print(
                f"PROCESSANDO "
                f"{indice}/"
                f"{len(candidatos)}"
            )

            print(
                livro["titulo"]
            )


            # ================================================
            # ABRIR LIVRO
            # ================================================

            if not navegar_com_tentativas(
                page,
                livro["link"],
            ):

                relatorio[
                    "falhas_conexao"
                ].append(
                    livro
                )

                salvar_relatorio(
                    relatorio
                )

                continue


            # ================================================
            # TITULO
            # ================================================

            livro["titulo"] = (
                obter_titulo_produto(
                    page,
                    livro["titulo"],
                )
            )


            # ================================================
            # PRECO
            # ================================================

            preco = (
                obter_preco_real_compra(
                    page
                )
            )

            print(
                "Preco de compra Kindle:",
                preco,
            )


            # ================================================
            # PRECO DESCONHECIDO
            # ================================================

            if preco is None:

                relatorio[
                    "preco_nao_identificado"
                ].append(
                    livro
                )

                salvar_relatorio(
                    relatorio
                )

                continue


            # ================================================
            # PAGO
            # ================================================

            if not eh_compra_gratuita(
                preco
            ):

                relatorio[
                    "pagos_ignorados"
                ].append(
                    {
                        **livro,
                        "preco": preco,
                    }
                )

                # Nao marcamos como processado
                # permanentemente.
                #
                # O preco pode mudar depois.

                salvar_relatorio(
                    relatorio
                )

                continue


            # ================================================
            # GRATUITO
            # ================================================

            item = {
                **livro,
                "preco": preco,
            }

            gratuitos.append(
                item
            )

            relatorio[
                "gratuitos_reais"
            ].append(
                item
            )


            # ================================================
            # JA ADQUIRIDO
            # ================================================

            if not pode_adquirir(
                page
            ):

                relatorio[
                    "ja_adquiridos"
                ].append(
                    item
                )

                processados.add(
                    chave
                )

                salvar_progresso(
                    processados
                )

                salvar_relatorio(
                    relatorio
                )

                continue


            # ================================================
            # AQUISICAO
            # ================================================

            if AUTO_ADQUIRIR:

                sucesso, motivo = (
                    adquirir_livro(
                        page
                    )
                )

                if sucesso:

                    relatorio[
                        "adquiridos"
                    ].append(
                        item
                    )

                    processados.add(
                        chave
                    )

                    salvar_progresso(
                        processados
                    )

                    print(
                        "ADQUIRIDO."
                    )

                else:

                    relatorio[
                        "falhas_aquisicao"
                    ].append(
                        {
                            **item,
                            "motivo": motivo,
                        }
                    )

                    print(
                        "Falha:",
                        motivo,
                    )

            salvar_relatorio(
                relatorio
            )

            time.sleep(
                TEMPO_ENTRE_LIVROS
            )


        # ====================================================
        # FINAL
        # ====================================================

        salvar_json(
            ARQUIVO_LIVROS_GRATIS,
            gratuitos,
        )

        salvar_relatorio(
            relatorio
        )

        salvar_progresso(
            processados
        )

        print(
            "\n================================"
        )

        print(
            "EXECUCAO FINALIZADA"
        )

        print(
            "================================"
        )

        print(
            "Candidatos:",
            len(candidatos),
        )

        print(
            "Gratuitos:",
            len(
                relatorio[
                    "gratuitos_reais"
                ]
            ),
        )

        print(
            "Adquiridos:",
            len(
                relatorio[
                    "adquiridos"
                ]
            ),
        )

        print(
            "Pagos ignorados:",
            len(
                relatorio[
                    "pagos_ignorados"
                ]
            ),
        )

        print(
            "Ja adquiridos:",
            len(
                relatorio[
                    "ja_adquiridos"
                ]
            ),
        )

        print(
            "preço não identificado:",
            len(
                relatorio[
                    "preço_nâo_identificado"
                ]
            ),
        )

        print(
            "Falhas de conexao:",
            len(
                relatorio[
                    "falhas_conexao"
                ]
            ),
        )

        print(
            "falhas de aquisicao:",
            len(
                relatorio[
                    "falhas_aquisicao"
                ]
            ),
        )

        context.close()

        browser.close()


if __name__ == "__main__":

    run()