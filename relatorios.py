import json
from pathlib import Path
from typing import cast

from config import (
    ARQUIVO_PROGRESSO,
    ARQUIVO_RELATORIO,
    DIRETORIO_DADOS,
)


def garantir_diretorio_dados() -> None:

    DIRETORIO_DADOS.mkdir(
        parents=True,
        exist_ok=True,
    )


def salvar_json(
    caminho: Path,
    dados: object,
) -> None:

    garantir_diretorio_dados()

    with caminho.open(
        "w",
        encoding="utf-8",
    ) as arquivo:

        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )


def carregar_progresso() -> set[str]:

    if not ARQUIVO_PROGRESSO.exists():
        return set()

    try:

        with ARQUIVO_PROGRESSO.open(
            "r",
            encoding="utf-8",
        ) as arquivo:

            dados = cast(
                object,
                json.load(
                    arquivo
                ),
            )

    except (
        json.JSONDecodeError,
        OSError,
    ):

        return set()

    if not isinstance(
        dados,
        list,
    ):

        return set()

    itens = cast(
        list[object],
        dados,
    )

    processados: set[str] = set()

    for item in itens:

        if isinstance(
            item,
            str,
        ):

            processados.add(
                item
            )

    return processados


def salvar_progresso(
    processados: set[str],
) -> None:

    salvar_json(
        ARQUIVO_PROGRESSO,
        sorted(
            processados
        ),
    )


def salvar_relatorio(
    relatorio: dict[
        str,
        list[dict[str, str]]
    ],
) -> None:

    salvar_json(
        ARQUIVO_RELATORIO,
        relatorio,
    )