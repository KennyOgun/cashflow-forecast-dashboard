# Cashflow Forecast & Working Capital Dashboard

**Portfolio project** —  **NHS finance, cashflow modelling, scenario analysis and dashboard delivery** using real-world data.

---

## What this project demonstrates

- **Problem framing**: Recurring operating deficit, cash squeeze and working capital strain in an NHS Foundation Trust (*Metropolitan NHS Foundation Trust*).
- **Solution**: A Streamlit dashboard with month-by-month cashflow forecast (Apr 25 – Mar 26), working capital metrics, **scenario modelling** (Best / Base / Worst / Do nothing), documented assumptions and recommendations.
- **Data**: Derived from published **NHS Foundation Trust 2024/25** financial statements (P&L, SFP, Cash Flow, notes).

---

## Features

| Feature | Description |
|--------|-------------|
| **Executive summary** | Problem scenario, what the organisation needed, solution delivered |
| **12-month forecast** | Income, expenses, operating cash flow, capex, financing and closing cash by month |
| **Working capital** | Receivables, payables, cash and current ratio from balance sheet |
| **Scenario modelling** | Best (+4% income, cost discipline, PDC injection), Base (+2% / +3%), Worst (−1% / +5%), Do nothing (flat income, +5% costs) |
| **Assumptions** | Revenue, expenses, capital and finance assumptions with rationale |
| **Recommendations** | Liquidity, working capital, cost control, capital and reporting |

---

## Tech stack

- **Python 3**
- **Streamlit** — dashboard UI
- **Pandas** — data and forecast logic
- **Plotly** — interactive charts

---

## Run locally

```bash
cd cashflow-forecast
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`).

---


## Licence and data

- Code: use as you like for portfolio and real-world applications.
- Financial data: based on publicly available NHS accounts; trust name and identifiers anonymised. Not for commercial or regulatory use without appropriate checks.
