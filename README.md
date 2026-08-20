# 📚 Encha Seu Kindle Automation

A Python automation project built with Playwright to collect, filter, validate, and optionally acquire free Kindle eBooks during Amazon's **Encha Seu Kindle (ESK)** events.

The project was originally created as a personal automation experiment and later redesigned as a reusable and modular application that can be adapted to future editions of the event.

> **Note:** Encha Seu Kindle is a periodic event. When no event is active, the project can be tested using regular Amazon search pages configured in `config.py`.

---

## ✨ Features

The automation can:

- Access the configured event or testing page
- Automatically detect available book categories
- Navigate through category filters
- Click **"Load more"** repeatedly to expand the product list
- Collect Kindle eBook candidates from product cards
- Identify products using their ASIN
- Remove duplicate books found across multiple categories
- Avoid collecting unrelated products from areas such as the shopping cart
- Open each candidate's product page
- Identify the Kindle purchase price
- Detect books whose purchase price is exactly **R$ 0,00**
- Ignore products that are not free
- Detect books that have already been acquired
- Save execution progress
- Generate execution reports
- Resume processing without repeating completed items
- Optionally acquire eligible free eBooks automatically

---

## 🛠️ Technologies

- Python
- Playwright
- JSON
- Regular Expressions
- Git
- GitHub

---

## 📁 Project Structure

```text
encha-seu-kindle-automation/
│
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

### Main modules

**`main.py`**  
Controls the complete workflow, including collection, validation, progress tracking, and optional acquisition.

**`config.py`**  
Contains event URLs, execution modes, category fallback settings, limits, delays, and timeouts.

**`coleta.py`**  
Handles category detection, product collection, ASIN extraction, duplicate removal, and the **Load more** workflow.

**`livros.py`**  
Handles Kindle price validation, purchase-button detection, and optional acquisition.

**`navegação.py`**  
Provides navigation helpers with retries and timeout handling.

**`relatorios.py`**  
Manages JSON reports and execution progress.

**`login.py`**  
Creates a local authenticated browser session that can be reused by the automation.

---

## ⚙️ Installation

Clone the repository:

```bash
git clone <repository-url>
cd encha-seu-kindle-automation
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Install Chromium for Playwright:

```bash
python -m playwright install chromium
```

---

## 🔐 Authentication

Before running the complete automation for the first time, execute:

```bash
python login.py
```

A browser window will open.

Log in to Amazon normally and, once the login is complete, return to the terminal and press **Enter**.

The program will create:

```text
auth.json
```

This file stores browser session information locally.

### Important

`auth.json` must never be committed or shared.

It is already included in `.gitignore`.

---

## 🔗 Configuring an ESK Edition

The main configuration is located in `config.py`.

When a new Encha Seu Kindle edition becomes available, configure an identifier for the event:

```python
NOME_EVENTO = "esk_example_2026"
```

Then add the current event URL:

```python
URL_EVENTO = "CURRENT_EVENT_URL"
```

Optional additional sources can be configured with:

```python
URLS_EXTRAS = [
    "ADDITIONAL_URL_1",
    "ADDITIONAL_URL_2",
]
```

Each event receives its own progress and report files, preventing previous editions from interfering with future runs.

---

## 🧪 Testing Outside an Active ESK Event

Because Encha Seu Kindle is a periodic event, an official event page may not always be available.

For development and testing, `URL_EVENTO` can temporarily point to a regular Amazon search page containing free eBooks.

Example:

```python
URL_EVENTO = (
    "https://www.amazon.com.br/"
    "s?k=ebooks+gratis+hoje"
)
```

This makes it possible to test parts of the collection and validation workflow even when no ESK edition is currently active.

The testing URL should not be interpreted as an official event page.

---

## 🧪 Safe Testing Mode

Before using the project with a new event edition, it is recommended to test the page structure first.

In `config.py`:

```python
MODO_COLETA_APENAS = True
AUTO_ADQUIRIR = False
```

Then run:

```bash
python main.py
```

In collection-only mode, the automation can inspect the configured source and save candidates without attempting acquisitions.

A smaller test can also be enabled with:

```python
MODO_TESTE = True
```

The number of categories and books processed during this mode can be configured separately.

---

## 📚 Category Detection

When the configured page provides ESK category filters, the automation attempts to detect them automatically.

Examples may include categories such as:

- Romance
- Fantasy
- Suspense
- Horror
- Fiction
- Non-fiction
- Young Adult

If automatic category discovery fails, the project can use the fallback category list defined in `config.py`.

The exact categories may vary between event editions.

---

## ➕ Load More Workflow

Some ESK pages do not display every available book immediately.

For each detected category, the automation searches for the **Load more** control and repeatedly activates it while new products continue to appear.

The process stops when:

- the button is no longer available;
- no new products are detected after the configured number of attempts; or
- the maximum number of clicks is reached.

This allows the collector to inspect more than the initially displayed products.

---

## 🔎 Product Collection

The collector uses Amazon product cards containing an ASIN instead of collecting every product link available on the page.

For a candidate to be accepted:

1. A valid product card must contain an ASIN.
2. A product link must exist inside that card.
3. The ASIN extracted from the link must match the card's ASIN.

This reduces the chance of unrelated products from other page sections — such as shopping-cart items, recommendations, or banners — being included in the collection.

---

## ♻️ Duplicate Removal

A book may appear in multiple categories.

The automation extracts the product's **ASIN** and uses it as a unique identifier.

Candidates are deduplicated before further processing, preventing the same product from being handled repeatedly.

---

## 💰 Kindle Price Validation

The automation does not treat every occurrence of a free price on the page as evidence that the Kindle edition is free.

Instead, it searches specifically for the Kindle purchase section.

A book is considered eligible only when the detected Kindle purchase price is exactly:

```text
R$ 0,00
```

If the price cannot be identified, the item is not treated as free.

If the price is different from `R$ 0,00`, the item is ignored.

When automatic acquisition is enabled, the price is checked again immediately before the acquisition attempt.

---

## 🛡️ Automatic Acquisition

Automatic acquisition is disabled by default:

```python
AUTO_ADQUIRIR = False
```

It should only be enabled after confirming that the current event structure is compatible with the automation:

```python
AUTO_ADQUIRIR = True
```

The acquisition workflow includes a final price validation before interacting with the purchase button.

---

## 💾 Progress and Reports

Execution data is stored locally inside:

```text
dados_execucao/
```

File names are generated according to the configured event name.

Examples:

```text
candidatos_esk_example_2026.json
livros_gratis_esk_example_2026.json
progresso_esk_example_2026.json
relatorio_esk_example_2026.json
```

This architecture separates different ESK editions and prevents an old progress file from automatically causing books in a future edition to be skipped.

Generated execution data is excluded from Git.

---

## 🌐 Connection Failure Handling

Web automation can be affected by:

- slow internet connections;
- temporary Amazon loading problems;
- browser delays;
- network interruptions.

Navigation therefore includes retry handling.

If a page cannot be loaded after the configured attempts, the failure can be registered while the remaining workflow continues.

---

## ⚠️ Limitations

Amazon may change its page structure at any time.

Future ESK editions may therefore require updates to selectors used for:

- categories;
- product cards;
- the **Load more** button;
- Kindle pricing;
- acquisition controls;
- confirmation messages.

The project is designed to be reusable, but compatibility with future editions cannot be guaranteed without testing.

---

## 🔒 Security

The project follows several conservative rules:

- Automatic acquisition is disabled by default
- Unknown prices are never treated as free
- A product must have a Kindle price of exactly `R$ 0,00`
- The price is checked again before an acquisition attempt
- Session information is stored locally
- `auth.json` is excluded from Git
- Execution data is excluded from Git
- Product collection is restricted to validated product cards

---

## 🎯 Project Goals

This project was developed to practice and demonstrate:

- Python programming
- Browser automation
- Playwright
- Modular software design
- Web data collection
- Data filtering
- Regular expressions
- URL handling
- Product identification using ASINs
- Deduplication
- JSON persistence
- Exception handling
- Retry strategies
- Execution-state management
- Git and GitHub version control

It also demonstrates the process of evolving a working personal script into a more organized, reusable, and documented software project.

---

## 📌 Disclaimer

This project was created for educational and portfolio purposes.

It is not affiliated with or endorsed by Amazon.

Website structures and event mechanics may change over time, and future versions of the event may require code adjustments.

Users are responsible for how they use the automation and for complying with the applicable platform terms and policies.