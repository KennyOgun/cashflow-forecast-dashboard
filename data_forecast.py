"""
Cashflow Forecast & Working Capital - Data & Forecast Logic
Based on anonymised NHS Foundation Trust financials (2024/25).
Trust name masked; figures derived from published accounts.
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Generic trust name for portfolio / CV
TRUST_NAME = "Metropolitan NHS Foundation Trust"

# --- Historical P&L (£000) - 5 years ---
HISTORICAL_PL = {
    "year": ["2020/21", "2021/22", "2022/23", "2023/24", "2024/25"],
    "patient_care_income": [356990, 410365, 447757, 450871, 498706],
    "other_operating_income": [53163, 29126, 30582, 33355, 31999],
    "total_income": [410153, 439491, 478339, 484226, 530705],
    "operating_expenses": [-417415, -439547, -475701, -502251, -535966],
    "operating_surplus_deficit": [-7262, -56, 2638, -18025, -5261],
    "net_finance_costs": [-2359, -2701, -3550, -2825, -3656],
    "surplus_deficit_year": [-9913, -1071, 2834, -24833, -8947],
}

# --- 2024/25 Cash Flow Statement (£000) ---
CASHFLOW_2024_25 = {
    "operating_cash_flow": 6707,   # Group
    "investing_cash_flow": -7595,
    "financing_cash_flow": -4396,
    "net_change_cash": -5284,
    "cash_opening": 15930,
    "cash_closing": 10646,
}

# Trust-only cash (from statement)
CASH_TRUST_OPEN_31MAR25 = 7965   # 31 Mar 25 per SFP
CASH_GROUP_OPEN_31MAR25 = 10646  # Group

# --- 2024/25 Operating detail (£000) for monthly split ---
INCOME_2024_25 = {
    "patient_care": 498706,
    "other_operating": 31999,
    "total_operating_income": 530705,
}
# Expense breakdown from Note 9.1 (Staff, Drugs, Clinical supplies, Other)
EXPENSES_2024_25 = 535966
EXPENSE_BREAKDOWN_2024_25 = {
    "staff_costs": 386011,
    "drugs": 26669,
    "clinical_supplies": 33177,
    "other_operating": 535966 - 386011 - 26669 - 33177 - 172,  # NED 172
}
OPERATING_DEFICIT_2024_25 = -5261

# Receivables: assume £8m of 2024/25 outstanding collected in Best case over 12 months (straight line)
RECEIVABLES_COLLECTION_BEST_CASE_000 = 8000
RECEIVABLES_INSTALLMENTS = 12
RECEIVABLES_MONTHLY_000 = RECEIVABLES_COLLECTION_BEST_CASE_000 / RECEIVABLES_INSTALLMENTS  # £8m/12 per month

# Monthly seasonality (NHS: winter pressure, year-end timing). Index 1.0 = average month.
# Slight uplift Dec-Feb (winter), lower summer, year-end spike March.
MONTHLY_SEASONALITY = {
    "Apr": 0.98, "May": 0.99, "Jun": 0.97, "Jul": 0.96, "Aug": 0.95,
    "Sep": 1.00, "Oct": 1.02, "Nov": 1.03, "Dec": 1.05, "Jan": 1.06,
    "Feb": 1.04, "Mar": 1.10,  # March often has catch-up / accruals
}

MONTHS_ORDER = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]


def get_historical_pl_df():
    return pd.DataFrame(HISTORICAL_PL)


def get_monthly_forecast_base(fy_label="2025/26"):
    """Base case: monthly forecast Apr 25 - Mar 26 using 2024/25 run-rate + 2% income growth, 3% cost growth (cost pressure)."""
    monthly_income = (INCOME_2024_25["total_operating_income"] / 12) * 1.02
    monthly_expenses = (EXPENSES_2024_25 / 12) * 1.03
    # Apply seasonality
    income_by_month = [
        monthly_income * MONTHLY_SEASONALITY[m] for m in MONTHS_ORDER
    ]
    expenses_by_month = [
        monthly_expenses * MONTHLY_SEASONALITY[m] for m in MONTHS_ORDER
    ]
    operating_cf = [i - e for i, e in zip(income_by_month, expenses_by_month)]
    # Finance: interest and PDC dividend spread evenly (from 2024/25: net finance ~£3,656k, PDC div £3,488k)
    monthly_finance_out = (3656 + 3488) / 12
    # Capex: from 2024/25 investing (£7,595k net out), spread with Q4 bias
    capex_pattern = [0.06, 0.06, 0.08, 0.08, 0.08, 0.08, 0.09, 0.09, 0.10, 0.10, 0.09, 0.09]
    annual_capex = 7595  # maintain similar level
    capex_by_month = [annual_capex * p for p in capex_pattern]
    # Financing inflow: assume no new PDC in base; principal repayments as per 2024/25
    principal_repay = (4147 + 5289) / 12  # loans + leases
    pdc_dividend_monthly = 3954 / 12  # PDC dividend paid
    financing_flow = [-principal_repay - pdc_dividend_monthly] * 12
    financing_flow[0] += 0   # no new PDC in base
    # Interest received ~£1,567/12 per month
    interest_in = 1567 / 12
    cash_start = CASH_GROUP_OPEN_31MAR25
    cash = [cash_start]
    for i in range(12):
        cf_oper = operating_cf[i]
        cf_inv = -capex_by_month[i] + interest_in
        cf_fin = financing_flow[i]
        cash.append(cash[-1] + cf_oper + cf_inv + cf_fin)
    periods = _periods_list()
    return pd.DataFrame({
        "period": periods,
        "income_000": np.round(income_by_month, 0),
        "expenses_000": np.round(expenses_by_month, 0),
        "operating_cf_000": np.round(operating_cf, 0),
        "capex_000": np.round(capex_by_month, 0),
        "financing_000": np.round(financing_flow, 0),
        "cash_close_000": np.round(cash[1:], 0),
    })


def _periods_list():
    # FY 2025/26: Apr–Dec 25, Jan–Mar 26
    return [f"{m} 25" if m in ["Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"] else f"{m} 26" for m in MONTHS_ORDER]


def get_monthly_cashflow_detailed(scenario="base"):
    """
    Returns cashflow forecast in requested format, transposed: rows = line items, columns = periods.
    scenario: 'base' or 'best'. Best case includes £8m receivables collection over 12 months (£8m/12 per month).
    """
    periods = _periods_list()
    # Base growth: income +2%, costs +3%
    inc_mult = 1.02 if scenario == "base" else 1.04
    exp_mult = 1.03 if scenario == "base" else 1.01
    # Monthly run-rates with seasonality
    pc_annual = INCOME_2024_25["patient_care"] * inc_mult
    other_annual = INCOME_2024_25["other_operating"] * (1.02 if scenario == "base" else 1.04)
    staff_annual = EXPENSE_BREAKDOWN_2024_25["staff_costs"] * exp_mult
    drugs_annual = EXPENSE_BREAKDOWN_2024_25["drugs"] * exp_mult
    clinical_annual = EXPENSE_BREAKDOWN_2024_25["clinical_supplies"] * exp_mult
    other_exp_annual = EXPENSE_BREAKDOWN_2024_25["other_operating"] * exp_mult

    opening = []
    patient_care = []
    other_income = []
    total_income = []
    staff = []
    drugs = []
    clinical_supplies = []
    other_operating = []
    total_outflow = []
    net_operating = []
    financing = []
    capex = []
    receivables_impact = []
    net_cash_flow = []
    closing = []

    cash = float(CASH_GROUP_OPEN_31MAR25)
    principal_repay = (4147 + 5289) / 12
    pdc_div = 3954 / 12
    interest_in = 1567 / 12
    capex_pattern = [0.06, 0.06, 0.08, 0.08, 0.08, 0.08, 0.09, 0.09, 0.10, 0.10, 0.09, 0.09]
    annual_capex = 7595 * (0.90 if scenario == "best" else 1.0)
    pdc_extra = 5000 if scenario == "best" else 0

    for i in range(12):
        m = MONTHS_ORDER[i]
        s = MONTHLY_SEASONALITY[m]
        opening.append(round(cash, 0))

        pc_m = (pc_annual / 12) * s
        oi_m = (other_annual / 12) * s
        patient_care.append(round(pc_m, 0))
        other_income.append(round(oi_m, 0))
        tot_in = pc_m + oi_m
        total_income.append(round(tot_in, 0))

        staff_m = (staff_annual / 12) * s
        drugs_m = (drugs_annual / 12) * s
        clinical_m = (clinical_annual / 12) * s
        other_exp_m = (other_exp_annual / 12) * s
        staff.append(round(staff_m, 0))
        drugs.append(round(drugs_m, 0))
        clinical_supplies.append(round(clinical_m, 0))
        other_operating.append(round(other_exp_m, 0))
        tot_out = staff_m + drugs_m + clinical_m + other_exp_m
        total_outflow.append(round(tot_out, 0))

        net_op = tot_in - tot_out
        net_operating.append(round(net_op, 0))

        fin = -(principal_repay + pdc_div) + interest_in + (pdc_extra / 12 if i == 0 and scenario == "best" else 0)
        financing.append(round(fin, 0))

        cap = (annual_capex * capex_pattern[i])
        capex.append(round(cap, 0))

        rec_impact = RECEIVABLES_MONTHLY_000 if scenario == "best" else 0
        receivables_impact.append(round(rec_impact, 0))

        net_cf = net_op + fin - cap + rec_impact
        net_cash_flow.append(round(net_cf, 0))
        cash = cash + net_cf
        closing.append(round(cash, 0))

    # Build transposed: rows = line items, columns = periods
    data = {
        "Opening Cash Balance": opening,
        "Operating Inflow - patient care": patient_care,
        "Other Income": other_income,
        "Total Operating Income": total_income,
        "Operating Outflow": total_outflow,
        "  Staff costs": staff,
        "  Drugs": drugs,
        "  Clinical Supplies": clinical_supplies,
        "  Other operating": other_operating,
        "Net Operating": net_operating,
        "Financing": financing,
        "Capex expense": capex,
        "Receivables Impact": receivables_impact,
        "Net Cash Flow": net_cash_flow,
        "Closing Cash": closing,
    }
    df = pd.DataFrame(data, index=periods)
    return df.T  # rows = line items, columns = periods


def get_income_expense_assumptions():
    """Short text for dashboard: what makes up income and expenses and assumptions."""
    return {
        "income": {
            "Operating Inflow - patient care": "Contract income from ICBs/NHS England (activity-based and block), high-cost drugs, other clinical. Assumption: +2% base / +4% best on 2024/25 run-rate; seasonal pattern applied.",
            "Other Income": "Education & training, R&D, non-patient care, leases, other. Assumption: same growth and seasonality as patient care.",
        },
        "expenses": {
            "Staff costs": "Agenda for Change, medical, agency/locum. Assumption: +3% base / +1% best; seasonality applied.",
            "Drugs": "Drug inventory consumed and non-inventory drugs. Assumption: same growth as total operating expenses.",
            "Clinical Supplies": "Supplies and services – clinical. Assumption: same growth as total operating expenses.",
            "Other operating": "General supplies, premises, depreciation, clinical negligence, other. Assumption: same growth as total operating expenses.",
        },
        "receivables_impact": "Best case only: £8m of 2024/25 outstanding receivables collected over 12 months (£8m/12 per month, straight line). Base/Worst/Do nothing: no receivables impact.",
    }


def get_monthly_forecast_scenarios():
    """Best / Base / Worst / Do Nothing scenarios for 2025/26. Returns base df and scenario summaries + monthly cash for charts."""
    base = get_monthly_forecast_base()
    monthly_income_avg = INCOME_2024_25["total_operating_income"] / 12
    monthly_exp_avg = EXPENSES_2024_25 / 12
    annual_capex = 7595
    pdc_dividend_annual = 3954
    principal_annual = 4147 + 5289
    capex_pattern = [0.06, 0.06, 0.08, 0.08, 0.08, 0.08, 0.09, 0.09, 0.10, 0.10, 0.09, 0.09]

    scenarios = {}
    for scenario, inc_mult, exp_mult, capex_mult, pdc_extra, receivables in [
        ("Best", 1.04, 1.01, 0.90, 5000, True),
        ("Base", 1.02, 1.03, 1.00, 0, False),
        ("Worst", 0.99, 1.05, 1.00, 0, False),
        ("Do nothing", 1.00, 1.05, 1.00, 0, False),
    ]:
        inc = [monthly_income_avg * MONTHLY_SEASONALITY[m] * inc_mult for m in MONTHS_ORDER]
        exp = [monthly_exp_avg * MONTHLY_SEASONALITY[m] * exp_mult for m in MONTHS_ORDER]
        op_cf = [i - e for i, e in zip(inc, exp)]
        capex = [annual_capex * p * capex_mult for p in capex_pattern]
        fin_month = -(principal_annual / 12 + pdc_dividend_annual / 12) + 1567 / 12  # Include interest received
        pdc_in_month = pdc_extra / 12 if pdc_extra else 0
        rec_month = RECEIVABLES_MONTHLY_000 if receivables else 0
        cash = [CASH_GROUP_OPEN_31MAR25]
        for i in range(12):
            cf_op = op_cf[i]  # Net Operating
            cf_fin = fin_month + (pdc_in_month if i == 0 else 0)  # Financing (includes interest)
            rec_impact = rec_month if receivables else 0
            # Net Cash Flow = Net Operating + Financing - Capex + Receivables Impact
            net_cf = cf_op + cf_fin - capex[i] + rec_impact
            cash.append(cash[-1] + net_cf)
        scenarios[scenario] = {
            "operating_cf_000": sum(op_cf),
            "cash_close_000": cash[-1],
            "monthly_cash_000": cash[1:],
        }
    return base, scenarios


def get_working_capital_metrics():
    """Working capital metrics from SFP 31 Mar 24 vs 31 Mar 25 (£000)."""
    return pd.DataFrame({
        "metric": [
            "Receivables (current)",
            "Inventories",
            "Trade payables",
            "Cash and equivalents",
            "Net working capital (approx)",
        ],
        "31-Mar-24": [14652, 3483, 42184, 11921, 14652 + 3483 - 42184 + 11921],
        "31-Mar-25": [22873, 4719, 50814, 7965, 22873 + 4719 - 50814 + 7965],
    })


def get_sfp_summary():
    """Key balance sheet items 31 Mar 24 vs 31 Mar 25 (£000)."""
    return {
        "total_assets_24": 268292,
        "total_assets_25": 262286,
        "current_assets_24": 32471,
        "current_assets_25": 36537,
        "current_liabilities_24": 56718,
        "current_liabilities_25": 62295,
        "borrowings_current_24": 7165,
        "borrowings_current_25": 11183,
        "borrowings_ncl_24": 76278,
        "borrowings_ncl_25": 64668,
        "cash_24": 11921,
        "cash_25": 7965,
        "equity_24": 133561,
        "equity_25": 134140,
    }
