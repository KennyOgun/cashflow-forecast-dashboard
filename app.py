"""
Cashflow Forecast & Working Capital Dashboard
Metropolitan NHS Foundation Trust — 2025/26 forecast
Portfolio project: real-world NHS financials, scenario modelling, recommendations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_forecast import (
    TRUST_NAME,
    get_historical_pl_df,
    get_monthly_forecast_base,
    get_monthly_forecast_scenarios,
    get_monthly_cashflow_detailed,
    get_income_expense_assumptions,
    get_working_capital_metrics,
    get_sfp_summary,
    MONTHS_ORDER,
    _periods_list,
)

st.set_page_config(
    page_title="Cashflow Forecast & Working Capital",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header { font-size: 1.8rem; font-weight: 700; color: #1e3a5f; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1rem; color: #5a6c7d; margin-bottom: 1.5rem; }
    .metric-card { background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 1rem; border-radius: 8px; border-left: 4px solid #1e3a5f; margin: 0.5rem 0; }
    .scenario-best { border-left-color: #059669 !important; }
    .scenario-worst { border-left-color: #dc2626 !important; }
    .scenario-base { border-left-color: #2563eb !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 10px 20px; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

st.markdown(f'<p class="main-header">📊 Cashflow Forecast & Working Capital Dashboard</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">{TRUST_NAME} · FY 2025/26 forecast (Apr 25 – Mar 26) ', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Executive summary",
    "Monthly forecast",
    "Working capital",
    "Scenario modelling",
    "Assumptions & methodology",
    "Recommendations",
])

# --- Tab 1: Executive summary (problem, solution, context) ---
with tab1:
    st.subheader("Problem scenario")
    st.markdown("""
    **Metropolitan NHS Foundation Trust** is a typical acute and community provider facing:
    - **Recurring operating deficit**: £5.3m deficit in 2024/25 despite income growth; prior year £18.0m deficit.
    - **Cash squeeze**: Group cash fell from £15.9m (Apr 24) to £10.6m (Mar 25); Trust-only cash £8.0m at year-end.
    - **Working capital strain**: Receivables up £8.2m (to £22.9m), payables up £8.6m (to £50.8m), stretching DSO/DPO and liquidity.
    - **Borrowing and PDC**: DHSC loans and lease obligations with principal and PDC dividend outflows; limited headroom for unplanned spend.
    """)
    st.subheader("What the organisation is craving")
    st.markdown("""
    - **Month-by-month cashflow visibility** to anticipate pinch points and plan drawdowns.
    - **Scenario modelling** (best / base / worst / do nothing) to support business cases and board reporting.
    - **Clear assumptions** for revenue, costs, capital and financing so decisions are evidence-based.
    - **Actionable recommendations** to improve liquidity, working capital and sustainability.
    """)
    st.subheader("Solution delivered")
    st.markdown("""
    This dashboard provides:
    1. **12-month cashflow forecast** (Apr 25 – Mar 26) derived from 2024/25 actuals and stated assumptions.
    2. **Working capital and balance sheet metrics** to monitor receivables, payables and cash.
    3. **Scenario modelling** with best / base / worst / do-nothing cases and closing cash positions.
    4. **Documented assumptions** for income, expenses, capital and finance (with reasons).
    5. **Recommendations** for liquidity, cost control and stakeholder reporting.
    """)
    st.info("Data is based on a typical NHS Foundation Trust financial statements (2024/25).")

    # High-level KPIs
    pl_df = get_historical_pl_df()
    sfp = get_sfp_summary()
    _, scenarios_dict = get_monthly_forecast_scenarios()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("2024/25 Operating deficit (£k)", f"{pl_df.loc[pl_df['year']=='2024/25', 'operating_surplus_deficit'].values[0]:,.0f}", help="P&L operating result")
    with c2:
        st.metric("Cash at 31 Mar 25 (£k)", f"{sfp['cash_25']:,.0f}", help="Group cash per SFP")
    with c3:
        st.metric("Base case cash Mar 26 (£k)", f"{scenarios_dict['Base']['cash_close_000']:,.0f}", help="Forecast closing cash, base scenario")
    with c4:
        st.metric("Worst case cash Mar 26 (£k)", f"{scenarios_dict['Worst']['cash_close_000']:,.0f}", help="Forecast closing cash, worst scenario")
    with c5:
        st.metric("Best case cash Mar 26 (£k)", f"{scenarios_dict['Best']['cash_close_000']:,.0f}", help="Forecast closing cash, best scenario")

    # Executive summary: aesthetic charts for non-technical stakeholders
    st.subheader("At a glance")
    periods_hist = pl_df["year"].tolist()
    fig_income_exp = go.Figure()
    fig_income_exp.add_trace(go.Bar(x=periods_hist, y=pl_df["patient_care_income"], name="Patient care income", marker_color="#2563eb"))
    fig_income_exp.add_trace(go.Bar(x=periods_hist, y=pl_df["other_operating_income"], name="Other income", marker_color="#60a5fa"))
    fig_income_exp.add_trace(go.Bar(x=periods_hist, y=-pl_df["operating_expenses"], name="Operating expenses", marker_color="#dc2626"))
    fig_income_exp.update_layout(barmode="group", title="Income vs expenses (£k) — 5-year view", xaxis_title="Year", yaxis_title="£000", height=380, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_income_exp, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        fig_surplus = go.Figure()
        fig_surplus.add_trace(go.Bar(x=periods_hist, y=pl_df["operating_surplus_deficit"], name="Operating surplus/(deficit)", marker_color=["#059669" if x >= 0 else "#dc2626" for x in pl_df["operating_surplus_deficit"]]))
        fig_surplus.update_layout(title="Operating result (£k)", xaxis_title="Year", yaxis_title="£000", height=320)
        st.plotly_chart(fig_surplus, use_container_width=True)
    with col_b:
        cash_hist = [15930, 10646]
        fig_cash = go.Figure()
        fig_cash.add_trace(go.Scatter(x=["Apr 24", "Mar 25"], y=cash_hist, mode="lines+markers", name="Group cash", line=dict(color="#059669", width=3), marker=dict(size=12)))
        fig_cash.update_layout(title="Cash position (£k)", xaxis_title="Period", yaxis_title="Cash £000", height=320)
        st.plotly_chart(fig_cash, use_container_width=True)

    fig_forecast_runway = go.Figure()
    periods_f = _periods_list()
    for scenario, color in [("Best", "#059669"), ("Base", "#2563eb"), ("Worst", "#dc2626")]:
        fig_forecast_runway.add_trace(go.Scatter(x=periods_f, y=scenarios_dict[scenario]["monthly_cash_000"], mode="lines+markers", name=scenario, line=dict(color=color, width=2)))
    fig_forecast_runway.update_layout(title="Forecast closing cash by scenario (£k) — Apr 25 to Mar 26", xaxis_title="Period", yaxis_title="Cash £000", height=360, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_forecast_runway, use_container_width=True)

# --- Tab 2: Monthly forecast ---
with tab2:
    st.subheader("12-month cashflow forecast (Apr 25 – Mar 26)")
    scenario_forecast = st.radio("Scenario", ["Base", "Best"], horizontal=True, help="Best case includes £8m receivables over 12 months (£8m/12 per month).")
    cf_detailed = get_monthly_cashflow_detailed(scenario_forecast.lower())
    # cf_detailed: index = line items, columns = periods (already transposed)
    cf_display = cf_detailed.copy()
    cf_display.index.name = "Line item"
    st.dataframe(cf_display.style.format("{:,.0f}", subset=cf_display.columns.tolist()), use_container_width=True)

    st.subheader("What makes up income and expenses — assumptions")
    assumptions = get_income_expense_assumptions()
    st.markdown("**Income**")
    for k, v in assumptions["income"].items():
        st.markdown(f"- **{k}**: {v}")
    st.markdown("**Expenses (Operating Outflow)**")
    for k, v in assumptions["expenses"].items():
        st.markdown(f"- **{k}**: {v}")
    st.markdown(f"**Receivables Impact**: {assumptions['receivables_impact']}")

    periods_plot = cf_display.columns.tolist()
    fig_income = go.Figure()
    fig_income.add_trace(go.Bar(x=periods_plot, y=cf_display.loc["Operating Inflow - patient care"], name="Patient care", marker_color="#2563eb"))
    fig_income.add_trace(go.Bar(x=periods_plot, y=cf_display.loc["Other Income"], name="Other income", marker_color="#60a5fa"))
    fig_income.update_layout(barmode="stack", title="Operating income by period (£k)", xaxis_title="Period", yaxis_title="£000", height=340)
    st.plotly_chart(fig_income, use_container_width=True)

    fig_runway = go.Figure()
    fig_runway.add_trace(go.Scatter(x=periods_plot, y=cf_display.loc["Closing Cash"], mode="lines+markers", name="Closing cash", line=dict(color="#059669", width=3)))
    fig_runway.update_layout(title="Closing cash position by period (£k)", xaxis_title="Period", yaxis_title="Cash £000", height=340)
    st.plotly_chart(fig_runway, use_container_width=True)

# --- Tab 3: Working capital ---
with tab3:
    st.subheader("Working capital and balance sheet")
    wc = get_working_capital_metrics()
    wc_display = wc.copy()
    wc_display.columns = ["Metric", "31 Mar 24 (£k)", "31 Mar 25 (£k)"]
    st.dataframe(wc_display.style.format("{:,.0f}", subset=["31 Mar 24 (£k)", "31 Mar 25 (£k)"]), use_container_width=True)
    st.caption("Receivables and payables have both increased; cash has fallen. Net working capital position has tightened.")
    sfp = get_sfp_summary()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current ratio (31 Mar 25)", f"{(sfp['current_assets_25'] / sfp['current_liabilities_25']):.2f}", help="Current assets / current liabilities")
    with col2:
        st.metric("Cash as % of current assets", f"{(sfp['cash_25'] / sfp['current_assets_25'] * 100):.1f}%", help="Liquidity")

# --- Tab 4: Scenario modelling ---
with tab4:
    st.subheader("Scenario modelling: Best / Base / Worst / Do nothing")
    _, scenarios_dict = get_monthly_forecast_scenarios()
    scenario_df = pd.DataFrame([
        {"Scenario": k, "Operating CF (£k)": v["operating_cf_000"], "Closing cash (£k)": v["cash_close_000"]}
        for k, v in scenarios_dict.items()
    ])
    st.dataframe(scenario_df.style.format("{:,.0f}", subset=["Operating CF (£k)", "Closing cash (£k)"]), use_container_width=True)

    fig_sc = go.Figure()
    months = _periods_list()
    for scenario, color in [("Best", "#059669"), ("Base", "#2563eb"), ("Worst", "#dc2626"), ("Do nothing", "#6b7280")]:
        fig_sc.add_trace(go.Scatter(x=months, y=scenarios_dict[scenario]["monthly_cash_000"], mode="lines+markers", name=scenario, line=dict(color=color, width=2)))
    fig_sc.update_layout(title="Closing cash by scenario (£k)", xaxis_title="Period", yaxis_title="Cash £000", height=450)
    st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown("""
    | Scenario | Income | Costs | Capex | PDC / financing | Receivables | Rationale |
    |----------|--------|-------|-------|-----------------|-------------|-----------|
    | **Best** | +4% | +1% | -10% | £5m injection | £8m/12 per month (12 months) | Contract gains, cost discipline, deferred capex, one-off PDC, accelerated collection of 2024/25 receivables |
    | **Base** | +2% | +3% | Flat | None | None | Moderate growth, cost pressure; planning assumption |
    | **Worst** | -1% | +5% | Flat | None | None | Demand/contract risk, pay and inflation above income |
    | **Do nothing** | Flat | +5% | Flat | None | None | No mitigation; costs drift, income flat |
    """)

# --- Tab 5: Assumptions ---
with tab5:
    st.subheader("Assumptions and methodology")
    st.markdown("""
    **Revenue inflow**
    - Base: +2% on 2024/25 run-rate; seasonal pattern (winter uplift, March year-end).
    - *Reason*: Contract and activity growth in line with system plans; seasonality from historic patterns.
    **Expenses**
    - Base: +3% run-rate; same seasonality as income where relevant.
    - *Reason*: Pay and price inflation; agency and demand pressure.
    **Capital (capex)**
    - From 2024/25 investing cash flow; pattern skewed to Q3/Q4 (estate and equipment).
    - *Reason*: Reflects planned capital programme and timing of spend.
    **Finance**
    - Interest: DHSC and lease interest from 2024/25; PDC dividend per policy.
    - Principal: Repayments on DHSC loans and lease obligations as per Note 34.
    - *Reason*: Contractual and policy-driven; no new borrowing assumed in base.
    **Opening position**
    - Group cash at 31 Mar 25 £10,646k (from Statement of Cash Flows); used as forecast opening.
    """)
    st.subheader("Seasonality (monthly index)")
    from data_forecast import MONTHLY_SEASONALITY
    sea_df = pd.DataFrame(list(MONTHLY_SEASONALITY.items()), columns=["Month", "Index (1.0 = avg)"])
    st.dataframe(sea_df, use_container_width=True)

# --- Tab 6: Recommendations ---
with tab6:
    st.subheader("Recommendations")
    st.markdown("""
    1. **Liquidity**: Monitor monthly cash against base and worst-case scenarios; agree a minimum cash floor and escalation with treasury/board.
    2. **Working capital**: Accelerate receivable collection (ICB and other bodies); align payment terms with suppliers where possible; review inventory levels.
    3. **Cost control**: Focus on agency and locum spend, procurement and pathway efficiency to keep cost growth below revenue growth.
    4. **Capital**: Prioritise essential capex; defer non-essential projects if cash tight; seek PDC or grant funding for strategic schemes.
    5. **Stakeholder reporting**: Use this dashboard for finance papers and board reports; update assumptions quarterly and re-run scenarios.
    6. **Do-nothing risk**: If no action is taken, the do-nothing scenario shows materially lower closing cash; recommend at least base-case mitigations.
    """)

st.sidebar.markdown("### About")
st.sidebar.markdown("Dashboard built from **actual NHS Foundation Trust** 2024/25 financial statements. Forecast period: Apr 25 – Mar 26.")
st.sidebar.markdown("Suitable for **cashflow modelling, scenario analysis and dashboard delivery.**")
