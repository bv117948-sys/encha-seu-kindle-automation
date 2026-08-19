# Encha Seu Kindle Automation

Automação desenvolvida em Python e Playwright para auxiliar na coleta, identificação e, opcionalmente, aquisição de eBooks gratuitos durante eventos Encha Seu Kindle (ESK).

O projeto surgiu como uma automação pessoal e posteriormente foi estruturado para ser reutilizado em futuras edições do evento e apresentado como projeto de portfólio.

## Funcionalidades

O projeto é capaz de:

- acessar a página configurada para uma edição do ESK;
- identificar automaticamente as categorias disponíveis;
- percorrer os filtros da página;
- utilizar repetidamente o botão "Carregar mais";
- coletar os produtos exibidos na listagem;
- evitar a coleta de produtos de outras áreas da Amazon, como o carrinho;
- identificar produtos pelo ASIN;
- remover livros duplicados encontrados em diferentes categorias;
- acessar individualmente as páginas dos livros;
- identificar o preço de compra da edição Kindle;
- reconhecer livros com preço de compra igual a R$ 0,00;
- ignorar livros que não estejam gratuitos;
- identificar livros que já foram adquiridos;
- registrar relatórios da execução;
- salvar o progresso separadamente para cada edição do evento;
- continuar a execução sem repetir itens já concluídos;
- opcionalmente realizar a aquisição automática de livros gratuitos.

## Tecnologias utilizadas

- Python
- Playwright
- JSON
- Git
- GitHub

## Estrutura do projeto

```text
Encha-seu-Kindle/
├── config.py
├── coleta.py
├── livros.py
├── login.py
├── main.py
├── navegação.py
├── relatorios.py
├── requirements.txt
├── README.md
└── .gitignore
```

Durante a execução, o programa também pode criar arquivos locais de sessão, progresso e relatório. Esses arquivos não são enviados ao repositório.

## Instalação

Clone o repositório e instale as dependências:

```bash
pip install -r requirements.txt
```

Depois instale o navegador utilizado pelo Playwright:

```bash
python -m playwright install chromium
```

## Login

Antes da primeira execução, utilize:

```bash
python login.py
```

Faça o login normalmente na Amazon.

Depois da confirmação no terminal, o programa cria o arquivo:

```text
auth.json
```

Esse arquivo contém informações da sessão e está incluído no `.gitignore`.

Nunca compartilhe ou envie o `auth.json` para o GitHub.

## Configurando uma nova edição do ESK

As configurações principais ficam em `config.py`.

Quando uma nova edição estiver disponível, altere:

```python
NOME_EVENTO = "esk_nome_da_edicao"
URL_EVENTO = "LINK_DA_NOVA_EDICAO"
```

Por exemplo:

```python
NOME_EVENTO = "esk_outubro_2026"
URL_EVENTO = "https://link.amazon/EXEMPLO"
```

Links adicionais podem ser adicionados em:

```python
URLS_EXTRAS = [
    "LINK_ADICIONAL_1",
    "LINK_ADICIONAL_2",
]
```

Links de edições anteriores podem permanecer comentados no código apenas como referência histórica.

## Testando uma nova edição

Como a estrutura das páginas da Amazon pode mudar, recomenda-se testar a coleta antes de habilitar qualquer aquisição.

No `config.py`, utilize:

```python
MODO_COLETA_APENAS = True
AUTO_ADQUIRIR = False
```

Execute:

```bash
python main.py
```

Nesse modo, o programa percorre a página e salva os candidatos encontrados sem realizar aquisições.

Também é possível utilizar:

```python
MODO_TESTE = True
```

para limitar a quantidade de categorias e livros durante os testes.

## Execução completa

Depois de confirmar que a página da nova edição continua compatível com a automação:

```python
MODO_COLETA_APENAS = False
```

A aquisição automática permanece desativada por padrão:

```python
AUTO_ADQUIRIR = False
```

Ela só deve ser habilitada depois da validação da nova edição:

```python
AUTO_ADQUIRIR = True
```

Em seguida:

```bash
python main.py
```

## Validação de preço

Antes de considerar um livro gratuito, o programa procura o preço de compra referente à edição Kindle.

A compra só é considerada gratuita quando o preço identificado corresponde exatamente a:

```text
R$ 0,00
```

Quando a aquisição automática está habilitada, o preço é verificado novamente imediatamente antes da tentativa de aquisição.

## Categorias e "Carregar mais"

Quando a página do evento disponibiliza filtros, o programa tenta identificá-los automaticamente.

Para cada categoria, a automação utiliza o botão "Carregar mais" enquanto novos resultados continuarem sendo exibidos.

Caso a descoberta automática das categorias falhe, existe uma lista de categorias de fallback em `config.py`.

## Deduplicação

Um mesmo livro pode aparecer em diferentes categorias.

Para evitar processamento repetido, o projeto utiliza o ASIN dos produtos como identificador e remove duplicidades antes das etapas seguintes.

## Progresso e relatórios

Os arquivos gerados durante a execução são armazenados em:

```text
dados_execucao/
```

Cada edição utiliza arquivos próprios com base em `NOME_EVENTO`.

Isso permite separar o progresso de diferentes edições do ESK e evita que o histórico de uma edição anterior faça o programa ignorar livros de uma edição futura.

## Tratamento de falhas

A navegação possui novas tentativas automáticas em caso de falha de carregamento.

Problemas de conexão, falhas de aquisição e preços que não puderam ser identificados são registrados no relatório da execução para análise posterior.

## Segurança

O projeto foi estruturado para utilizar uma abordagem conservadora:

- a aquisição automática é desativada por padrão;
- itens sem preço identificado não são adquiridos;
- itens cujo preço não seja exatamente R$ 0,00 não são adquiridos;
- o preço é verificado novamente antes da aquisição;
- dados de sessão não são versionados pelo Git.

## Limitações

A estrutura das páginas da Amazon pode mudar entre diferentes edições do evento.

Por isso, seletores utilizados para identificar categorias, produtos, preços ou botões podem precisar de ajustes no futuro.

Problemas de conexão ou lentidão também podem causar falhas pontuais durante uma execução.

## Objetivo do projeto

Este projeto foi desenvolvido como exercício prático de automação web e posteriormente estruturado como projeto de portfólio.

Durante o desenvolvimento foram aplicados conceitos como:

- automação de navegador;
- modularização em Python;
- coleta e filtragem de dados;
- manipulação de URLs;
- expressões regulares;
- deduplicação por identificadores;
- persistência de dados em JSON;
- tratamento de exceções;
- controle de progresso;
- tentativas de recuperação após falhas;
- versionamento com Git.

## Aviso

Este projeto possui finalidade educacional e de portfólio.

O funcionamento depende da estrutura das páginas utilizadas e pode exigir adaptações em futuras edições.

O usuário é responsável pelo uso da automação e pelo cumprimento dos termos e políticas das plataformas envolvidas.