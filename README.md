# Investment Portfolio Advisor

A top-down portfolio recommendation system for individual investors, built as a Claude Code agent. Takes a user's investment profile (budget, horizon, risk tolerance) and produces 3 risk-differentiated portfolio options (aggressive / moderate / conservative) with HTML dashboard and DOCX investment memo output.

## Features

- **Multi-asset coverage**: US equities/ETFs, KR equities/ETFs, bonds, cash equivalents
- **12-step pipeline**: Environment assessment (macro, political, fundamentals, sentiment) followed by portfolio construction
- **3 portfolio options**: Differentiated by risk level with distinct investment logic
- **Dual output**: Interactive HTML dashboard (TailwindCSS + Chart.js) and DOCX investment memo
- **Data quality**: Source tagging, confidence grading (A/B/C/D), blank-over-wrong principle
- **Bilingual**: Auto-detects Korean or English input, responds accordingly

## Prerequisites

- Python 3.11+
- Claude Code CLI

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd investment-portfolio-advisor

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Start a Claude Code session in the project directory:

```bash
claude
```

Then describe your investment goals:

```
50M KRW, 1 year, moderate risk tolerance - recommend a portfolio
```

or in English:

```
$100K, 3 years, aggressive - recommend a portfolio
```

The system will run the full 12-step pipeline and deliver:
1. A chat summary with key findings
2. An HTML dashboard at `output/reports/portfolio_{lang}_{date}.html`
3. A DOCX investment memo at `output/reports/portfolio_{lang}_{date}.docx`

## Architecture

The system is orchestrated by `CLAUDE.md` and uses:
- **3 sub-agents**: environment-researcher, portfolio-analyst, critic
- **12 skills**: staleness-checker, query-interpreter, 4 collectors, data-validator, environment-scorer, quality-gate, dashboard-generator, memo-generator, data-manager
- **8 Python scripts**: Deterministic computation (validation, allocation, return estimation, quality checks)

See `investment-portfolio-advisor-design-v2-en.md` for the full design specification.

## Running Tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

## Disclaimer

This is not investment advice. For informational purposes only.
