# Cashflow Forecast & Working Capital Dashboard

**Portfolio project** —  **NHS finance, cashflow modelling, scenario analysis and dashboard delivery** using real-world data.

---

## What this project demonstrates

- **Problem**: Recurring operating deficit, cash squeeze and working capital strain in an NHS Foundation Trust (*Metropolitan NHS Foundation Trust*).
  
- **Solution**: A Streamlit dashboard with month-by-month cashflow forecast (Apr 25 – Mar 26), working capital metrics, **scenario modelling** (Best / Base / Worst / Do nothing), documented assumptions and recommendations.
  
- **Data**: Derived from published **NHS Foundation Trust 2024/25** financial statements (P&L, SFP, Cash Flow, notes).

---

## Features

| Feature | Description |
|--------|-------------|

## 1.0 | **Executive summary** | Problem scenario, what the organisation needed, solution delivered |

<img width="1487" height="168" alt="image" src="https://github.com/user-attachments/assets/210a02be-6801-4147-87f1-f1e012a9e97b" />


## 2.0 | **12-month forecast** | Income, expenses, operating cash flow, capex, financing and closing cash by month |

<img width="1501" height="713" alt="image" src="https://github.com/user-attachments/assets/e7e62810-a0aa-44f9-bb05-1f262bc5bd96" />

<img width="1572" height="650" alt="image" src="https://github.com/user-attachments/assets/5e91b765-dcfd-431b-ba45-f3c9c6a8c96a" />


## 3.0 | **Working capital** | Receivables, payables, cash and current ratio from balance sheet |

<img width="1523" height="402" alt="image" src="https://github.com/user-attachments/assets/07266cf0-89a5-4b0d-a4d7-f0af7e1387a4" />


## 4.0 | **Scenario modelling** | Best (+4% income, cost discipline, PDC injection), Base (+2% / +3%), Worst (−1% / +5%), Do nothing (flat income, +5% costs) |

<img width="1535" height="660" alt="image" src="https://github.com/user-attachments/assets/0616b74e-53fc-4071-bcb8-17e8f644d554" />


## 5.0 | **Assumptions** | Revenue, expenses, capital and finance assumptions with rationale |

<img width="800" height="408" alt="image" src="https://github.com/user-attachments/assets/6df2c121-7018-46b6-8a25-f1089333b56e" />


## 6.0 | **Recommendations** | Liquidity, working capital, cost control, capital and reporting |

<img width="1032" height="240" alt="image" src="https://github.com/user-attachments/assets/3866cd11-25e7-460d-96c5-29367c734bc7" />




![Uploading image.png…]()



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
