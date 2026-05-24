# SecureMail

SecureMail is a command-line tool that analyzes emails and estimates
the probability that each one is spam or legitimate.

It takes `.eml` files as input, runs them through a full pipeline
(parsing → feature extraction → ML model), and outputs a spam
probability score for each email.

## How it works

SecureMail runs in three stages:

### 1. Parsing

Each `.eml` file is parsed to extract all useful information from its
source code: basic mail metadata (sender, recipient, date, subject,
content), but also deeper data — links, attachments, and email
authentication signatures (SPF, DKIM). Each link and attachment is
individually enriched with additional information (RDAP lookups,
redirect checks, file type verification).

All of this is stored in a structured SQLite database with three tables:
`mails`, `links`, and `attachments`.

### 2. Feature Engineering

From the parsed database, threat indicators are computed for each email.
Each feature describes one specific signal of malicious intent — on the
mail itself, its links, and its attachments.

Since an email can contain multiple links and attachments, link and
attachment features are aggregated per email as both a **sum** and a
**mean**, giving the model richer signal than a single value would.

The result is a flat feature table, one row per email, ready for the model.

### 3. Prediction

A neural network trained on a dataset of ~36,000 emails (spam and
legitimate, recent and older) is applied to the normalized feature table.
The model reaches **96% accuracy** on its test set.

For each email, SecureMail outputs a spam probability score.

## Project Structure

```
SecureMail/
├── main.py                  # Entry point
├── menu.py                  # Main CLI menu
├── requirements.txt
├── mailbox/
│   └── inbox/               # Place your .eml files here
├── storage/                 # Generated databases (auto-created)
├── ingestion/               # Stage 1 — Parsing
│   ├── pipeline/
│   │   ├── database.py      # Database schema & initialization
│   │   └── operations.py    # Core parsing logic
│   └── services/
│       ├── email_service.py       # Mail header parsing
│       ├── enrichment_service.py  # Link enrichment (RDAP, redirects)
│       ├── link_service.py        # Link extraction
│       └── attachment_service.py  # Attachment analysis
├── feature_engineering/     # Stage 2 — Feature extraction
│   ├── etl/                 # Load, normalize, schema
│   ├── featuring/           # Threat indicator functions
│   └── data/                # Reference lists (spam words, domains...)
└── model/                   # Stage 3 — Prediction
    ├── securemail_net.py    # Neural network architecture
    ├── train.py             # Training script
    └── predict.py           # Inference on new emails
```

## Installation

**Requirements** — Python 3.15+

Clone the repository and install the dependencies:

```bash
git clone <repo_url>
cd SecureMail
pip install -r requirements.txt
```

> Warning : `torch` can take a few minutes to install depending on your connection.

## Usage

Place your `.eml` files in `mailbox/inbox/`, then run:

```bash
python main.py
```

This opens an interactive menu with the following options:

**1. Ingestion** — Parses your `.eml` files and populates the database.
You will be asked whether to add new emails on top of existing data or
restart from scratch, and whether to enrich links (RDAP lookups,
redirect checks).

> Warning : Link enrichment can take a significant amount of time depending
> on the number of emails and links.

**2. Feature Engineering** — Extracts threat indicators from the parsed
database and builds the feature table.

**3. Prediction** — Normalizes the feature table and runs the model to
output a spam probability score for each email.

**4. Full Pipeline** — Runs all three stages sequentially without
interruption. You only need to choose whether to add to existing data
or restart from scratch — everything else is automatic.

**5. Reset Databases** — Clears all data and compacts the databases
to free up disk space.

## Known Limitations

**Dataset quality** — The training dataset is heavily biased toward old
emails (2002–2007) and recent ones (2020–2024), with a large gap in
between. Since the tool is meant to analyze current emails, this affects
the model's reliability on modern spam patterns. The feature engineering
handles this by distinguishing old and recent emails, but it remains a
structural weakness.

**Lack of threat variety** — The dataset contains almost exclusively
phishing and identity spoofing attempts. Other threat types like Nigerian
scam emails or attachment-based attacks are barely represented, which
limits the model's ability to detect them.

**Parsing speed** — Link enrichment (RDAP lookups, redirect checks) has
no persistent cache between runs, meaning every run re-fetches everything
from scratch. Even with a concurrency limit of 3, rate limiting is
frequent and slows the process down significantly.

**Arbitrary feature values** — Some threat indicator scores were set
manually based on intuition rather than statistical analysis. They work
reasonably well but could be improved with a more rigorous approach.

## Tech Stack

- **Python 3.15**
- **SQLite3** — structured storage for parsed emails, links and attachments
- **Pandas** — data manipulation and feature table construction
- **PyTorch** — neural network architecture and training
- **Scikit-learn** — data normalization (StandardScaler)
- **aiohttp / asyncwhois** — asynchronous link enrichment (RDAP lookups, redirects)
- **RapidFuzz** — Jaro-Winkler similarity for identity spoofing detection
- **gibberish-detector** — nonsense string detection in domains and mailer headers
