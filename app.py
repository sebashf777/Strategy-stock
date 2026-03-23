import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="PropIQ — Real Estate Analyzer",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    --gold:    #C9A84C;
    --gold-lt: #E8C97A;
    --dark:    #0E1117;
    --surface: #161B26;
    --card:    #1C2333;
    --border:  #2A3347;
    --text:    #E8EAF0;
    --muted:   #6B7A99;
    --green:   #2ECC71;
    --red:     #E74C3C;
    --blue:    #3498DB;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--dark) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stHeader"] { display: none !important; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1400px !important; }

/* ── KPI CARDS ── */
.kpi-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
.kpi-card {
    flex: 1; min-width: 160px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--gold), var(--gold-lt));
}
.kpi-card:hover { border-color: var(--gold); transform: translateY(-2px); }
.kpi-label { font-size: 11px; font-weight: 600; letter-spacing: 1.2px;
             text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }
.kpi-value { font-family: 'DM Serif Display', serif; font-size: 26px;
             color: var(--text); line-height: 1.1; }
.kpi-value.positive { color: var(--green); }
.kpi-value.negative { color: var(--red); }
.kpi-sub { font-size: 11px; color: var(--muted); margin-top: 6px; font-family: 'DM Mono', monospace; }
.kpi-icon { position: absolute; top: 16px; right: 16px; font-size: 22px; opacity: 0.25; }

/* ── SECTION HEADERS ── */
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    color: var(--text);
    margin: 32px 0 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-title span { color: var(--gold); }

/* ── PAGE TITLE ── */
.page-title {
    font-family: 'DM Serif Display', serif;
    font-size: 42px;
    background: linear-gradient(135deg, var(--gold), var(--gold-lt));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
    margin-bottom: 4px;
}
.page-sub { color: var(--muted); font-size: 15px; margin-bottom: 32px; }

/* ── STATUS BADGE ── */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
}
.badge-green  { background: rgba(46,204,113,0.15); color: var(--green); border:1px solid rgba(46,204,113,0.3); }
.badge-red    { background: rgba(231,76,60,0.15);  color: var(--red);   border:1px solid rgba(231,76,60,0.3); }
.badge-gold   { background: rgba(201,168,76,0.15); color: var(--gold);  border:1px solid rgba(201,168,76,0.3); }
.badge-blue   { background: rgba(52,152,219,0.15); color: var(--blue);  border:1px solid rgba(52,152,219,0.3); }

/* ── VERDICT BOX ── */
.verdict {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 28px;
    margin: 24px 0;
}
.verdict-title {
    font-family: 'DM Serif Display', serif;
    font-size: 20px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* ── TABLE STYLING ── */
.stDataFrame { border-radius: 10px; overflow: hidden; }
[data-testid="stDataFrameResizable"] { border: 1px solid var(--border) !important; border-radius: 10px; }

/* ── SIDEBAR INPUTS ── */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stSlider"] { padding: 4px 0; }
.stSlider [data-baseweb="slider"] { padding: 8px 0; }

/* ── TABS ── */
[data-testid="stTabs"] [role="tab"] {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    color: var(--muted) !important;
    border-bottom: 2px solid transparent;
    padding: 8px 20px;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom-color: var(--gold) !important;
}
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid var(--border);
    gap: 4px;
}

/* Divider */
.divider { height:1px; background: var(--border); margin: 24px 0; }
</style>
""", unsafe_allow_html=True)

# ── PLOTLY THEME ──────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(28,35,51,0.6)',
    font=dict(family='DM Sans', color='#6B7A99', size=11),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#E8EAF0', size=11)),
    xaxis=dict(gridcolor='#2A3347', linecolor='#2A3347', zerolinecolor='#2A3347'),
    yaxis=dict(gridcolor='#2A3347', linecolor='#2A3347', zerolinecolor='#2A3347'),
)
COLORS = dict(gold='#C9A84C', gold_lt='#E8C97A', green='#2ECC71',
              red='#E74C3C', blue='#3498DB', purple='#9B59B6',
              teal='#1ABC9C', orange='#E67E22')

# ── FINANCIAL FUNCTIONS ───────────────────────────────────────
def monthly_payment(principal, annual_rate_pct, term_months):
    r = annual_rate_pct / 1200
    if r == 0:
        return principal / term_months
    return float(principal) * (r * (1 + r)**term_months) / ((1 + r)**term_months - 1)

def calc_noi(rent, vacancy_pct, maintenance_pct, mgmt_fee_pct, annual_tax_pct, annual_ins_pct):
    eff = rent * (1 - vacancy_pct / 100)
    exp = eff * ((maintenance_pct + mgmt_fee_pct + annual_tax_pct + annual_ins_pct) / 100)
    return (eff - exp) * 12

def calc_max_purchase(rent, vacancy_pct, maintenance_pct, mgmt_fee_pct,
                      annual_tax_pct, annual_ins_pct, rate_pct, term, min_cf=100):
    r   = rate_pct / 1200
    eff = rent * (1 - vacancy_pct / 100)
    exp = eff * ((maintenance_pct + mgmt_fee_pct + annual_tax_pct + annual_ins_pct) / 100)
    qty = (r * (1 + r)**term) / ((1 + r)**term - 1) if r > 0 else 1/term
    return ((eff - exp - min_cf) / qty) / 0.80

def build_amortization(principal, annual_rate_pct, term_months):
    r       = annual_rate_pct / 1200
    payment = monthly_payment(principal, annual_rate_pct, term_months)
    balance = principal
    cumint  = 0
    records = []
    for month in range(1, int(term_months) + 1):
        interest      = balance * r
        principal_pd  = payment - interest
        balance      -= principal_pd
        cumint       += interest
        records.append({
            'Month':              month,
            'Payment':            round(payment, 2),
            'Principal':          round(principal_pd, 2),
            'Interest':           round(interest, 2),
            'Balance':            round(max(balance, 0), 2),
            'Cumul. Interest':    round(cumint, 2),
            'Equity':             round(principal - max(balance, 0), 2),
        })
    return pd.DataFrame(records)

def full_analysis(p):
    payment    = monthly_payment(p['loan'], p['rate'], p['term'])
    down       = p['price'] - p['loan']
    cash_req   = down + p['closing']
    noi        = calc_noi(p['rent'], p['vacancy'], p['maint'], p['mgmt'], p['tax'], p['ins'])
    annual_debt= payment * 12
    annual_cf  = noi - annual_debt
    cap_rate   = (noi / p['price']) * 100 if p['price'] > 0 else 0
    coc        = (annual_cf / cash_req) * 100 if cash_req > 0 else 0
    dscr       = noi / annual_debt if annual_debt > 0 else 0
    gross_yield= (p['rent'] * 12 / p['price']) * 100 if p['price'] > 0 else 0
    max_price  = calc_max_purchase(p['rent'], p['vacancy'], p['maint'], p['mgmt'],
                                   p['tax'], p['ins'], p['rate'], p['term'])
    grm        = p['price'] / (p['rent'] * 12) if p['rent'] > 0 else 0
    breakeven  = (p['loan'] * (1 - (p['vacancy']/100))) / p['price'] * 100 if p['price'] > 0 else 0

    return dict(
        payment=round(payment, 2),
        total_payments=round(payment * p['term'], 2),
        total_interest=round(payment * p['term'] - p['loan'], 2),
        cash_required=round(cash_req, 2),
        down_payment=round(down, 2),
        annual_debt=round(annual_debt, 2),
        noi=round(noi, 2),
        annual_cf=round(annual_cf, 2),
        monthly_cf=round(annual_cf / 12, 2),
        cap_rate=round(cap_rate, 2),
        coc=round(coc, 2),
        dscr=round(dscr, 3),
        gross_yield=round(gross_yield, 2),
        max_price=round(max_price, 2),
        grm=round(grm, 2),
        breakeven_occ=round(breakeven, 1),
        ltv=round((p['loan'] / p['price']) * 100, 1) if p['price'] > 0 else 0,
    )

# ── SIDEBAR — INPUTS ──────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:20px 0 10px'>
      <div style='font-family:"DM Serif Display",serif;font-size:26px;
                  background:linear-gradient(135deg,#C9A84C,#E8C97A);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent'>
        PropIQ
      </div>
      <div style='font-size:12px;color:#6B7A99;margin-top:2px'>
        Real Estate Investment Analyzer
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    project_name = st.text_input("🏷️ Project Name", value="Sample Property")

    st.markdown("#### 📋 Property Details")
    price   = st.number_input("Purchase Price ($)", value=350_000, step=5_000, format="%d")
    rent    = st.number_input("Monthly Rent ($)",   value=2_800,  step=50,    format="%d")
    closing = st.number_input("Closing Costs ($)",  value=7_000,  step=500,   format="%d")
    arv     = st.number_input("After Repair Value ($)", value=400_000, step=5_000, format="%d")
    repair  = st.number_input("Repair Costs ($)",   value=15_000, step=1_000, format="%d")

    st.markdown("#### 🏦 Loan Details")
    use_default = st.checkbox("Use 80% LTV (default)", value=True)
    if use_default:
        loan = price * 0.80
        st.caption(f"Loan Amount: ${loan:,.0f}")
    else:
        loan = st.number_input("Loan Amount ($)", value=int(price * 0.80), step=5_000, format="%d")
    rate = st.number_input("Interest Rate (%)", value=7.25, step=0.125, format="%.3f")
    term = st.selectbox("Loan Term", [360, 180, 120, 84], format_func=lambda x: f"{x} months ({x//12} yrs)")

    st.markdown("#### 📊 Operating Expenses")
    vacancy = st.slider("Vacancy Rate (%)",    0.0, 25.0, 5.0, 0.5)
    maint   = st.slider("Maintenance (%)",     0.0, 25.0, 5.0, 0.5)
    mgmt    = st.slider("Mgmt Fee (%)",        0.0, 20.0, 8.0, 0.5)
    tax     = st.slider("Annual Tax (%)",      0.0, 5.0,  1.2, 0.1)
    ins     = st.slider("Annual Insurance (%)",0.0, 3.0,  0.5, 0.1)

    st.markdown("#### 🔄 Analysis")
    sens    = st.slider("Sensitivity (%)", 5.0, 30.0, 10.0, 5.0)
    hold_yrs= st.slider("Hold Period (years)", 1, 30, 10)
    app_rate= st.slider("Annual Appreciation (%)", 0.0, 10.0, 3.0, 0.5)
    rent_gr = st.slider("Annual Rent Growth (%)",  0.0, 10.0, 2.0, 0.5)

    st.markdown("---")
    st.caption("💡 All calculations assume monthly compounding.")

# ── INPUTS DICT ───────────────────────────────────────────────
p = dict(price=price, rent=rent, closing=closing, loan=loan,
         rate=rate, term=term, vacancy=vacancy, maint=maint,
         mgmt=mgmt, tax=tax, ins=ins)

r  = full_analysis(p)
am = build_amortization(loan, rate, term)

# ── SENSITIVITY SCENARIOS ─────────────────────────────────────
p_up   = {**p, 'price': price*(1+sens/100), 'rent': rent*(1+sens/100),
           'loan': loan*(1+sens/100), 'closing': closing*(1+sens/100)}
p_down = {**p, 'price': price*(1-sens/100), 'rent': rent*(1-sens/100),
           'loan': loan*(1-sens/100), 'closing': closing*(1-sens/100)}
r_up   = full_analysis(p_up)
r_down = full_analysis(p_down)

# ── HEADER ────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f'<div class="page-title">PropIQ</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">Investment Analysis — <strong>{project_name}</strong></div>',
                unsafe_allow_html=True)
with col_h2:
    # Quick verdict
    if r['annual_cf'] > 0 and r['dscr'] >= 1.25 and r['cap_rate'] >= 5:
        verdict_html = '<span class="badge badge-green">✅ STRONG BUY</span>'
    elif r['annual_cf'] > 0 and r['dscr'] >= 1.0:
        verdict_html = '<span class="badge badge-gold">⚡ CONSIDER</span>'
    else:
        verdict_html = '<span class="badge badge-red">⚠️ CAUTION</span>'
    st.markdown(f'<div style="text-align:right;padding-top:20px">{verdict_html}</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:right;font-size:12px;color:#6B7A99;margin-top:6px">'
                f'DSCR: {r["dscr"]:.2f} · Cap: {r["cap_rate"]:.1f}%</div>',
                unsafe_allow_html=True)

# ── KPI CARDS ROW 1 ───────────────────────────────────────────
cf_class = "positive" if r['monthly_cf'] >= 0 else "negative"
coc_class = "positive" if r['coc'] >= 0 else "negative"

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-icon">💵</div>
    <div class="kpi-label">Monthly Cash Flow</div>
    <div class="kpi-value {cf_class}">${r['monthly_cf']:,.0f}</div>
    <div class="kpi-sub">Annual: ${r['annual_cf']:,.0f}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">📈</div>
    <div class="kpi-label">Cap Rate</div>
    <div class="kpi-value">{r['cap_rate']:.2f}%</div>
    <div class="kpi-sub">Gross Yield: {r['gross_yield']:.2f}%</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">💰</div>
    <div class="kpi-label">Cash-on-Cash</div>
    <div class="kpi-value {coc_class}">{r['coc']:.2f}%</div>
    <div class="kpi-sub">On ${r['cash_required']:,.0f} invested</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">🏦</div>
    <div class="kpi-label">DSCR</div>
    <div class="kpi-value {'positive' if r['dscr']>=1.25 else 'negative' if r['dscr']<1 else ''}">{r['dscr']:.2f}</div>
    <div class="kpi-sub">Min 1.25x for lenders</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">📊</div>
    <div class="kpi-label">Mortgage Payment</div>
    <div class="kpi-value">${r['payment']:,.0f}</div>
    <div class="kpi-sub">P&I Monthly</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">🎯</div>
    <div class="kpi-label">Max Purchase Price</div>
    <div class="kpi-value">${r['max_price']:,.0f}</div>
    <div class="kpi-sub">Min $100/mo cash flow</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ROW 2 ───────────────────────────────────────────
arv_equity = arv - price - repair
equity_mult = arv / (price + repair) if (price + repair) > 0 else 0

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-icon">🏗️</div>
    <div class="kpi-label">GRM</div>
    <div class="kpi-value">{r['grm']:.1f}x</div>
    <div class="kpi-sub">Gross Rent Multiplier</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">📉</div>
    <div class="kpi-label">LTV</div>
    <div class="kpi-value">{r['ltv']:.1f}%</div>
    <div class="kpi-sub">Loan-to-Value</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">🏠</div>
    <div class="kpi-label">Down Payment</div>
    <div class="kpi-value">${r['down_payment']:,.0f}</div>
    <div class="kpi-sub">+ ${closing:,.0f} closing costs</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">⚡</div>
    <div class="kpi-label">ARV Equity</div>
    <div class="kpi-value {'positive' if arv_equity>0 else 'negative'}">${arv_equity:,.0f}</div>
    <div class="kpi-sub">ARV − Price − Repairs</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">🔑</div>
    <div class="kpi-label">Breakeven Occupancy</div>
    <div class="kpi-value">{r['breakeven_occ']:.1f}%</div>
    <div class="kpi-sub">Min occ. to cover loan</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">💎</div>
    <div class="kpi-label">Total Interest Paid</div>
    <div class="kpi-value">${r['total_interest']/1000:.0f}K</div>
    <div class="kpi-sub">Over {term//12} years</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Cash Flow", "🔄 Sensitivity", "📅 Amortization",
    "📈 Projections", "🏗️ Deal Analyzer", "📋 Full Report"
])

# ════════════════════════════════════════════════════════════
# TAB 1 — CASH FLOW
# ════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">💵 <span>Monthly Income & Expense Breakdown</span></div>',
                unsafe_allow_html=True)

    eff_rent  = rent * (1 - vacancy/100)
    maint_amt = eff_rent * maint/100
    mgmt_amt  = eff_rent * mgmt/100
    tax_amt   = eff_rent * tax/100
    ins_amt   = eff_rent * ins/100
    total_exp = maint_amt + mgmt_amt + tax_amt + ins_amt
    monthly_noi = eff_rent - total_exp
    monthly_cf_v = monthly_noi - r['payment']

    col1, col2 = st.columns(2)

    with col1:
        # Waterfall chart
        categories = ['Gross Rent', 'Vacancy Loss', 'Maintenance', 'Mgmt Fee',
                      'Property Tax', 'Insurance', 'Debt Service', 'Net Cash Flow']
        values = [rent, -(rent - eff_rent), -maint_amt, -mgmt_amt,
                  -tax_amt, -ins_amt, -r['payment'], monthly_cf_v]
        colors_wf = [COLORS['gold'] if v > 0 else COLORS['red'] for v in values]
        colors_wf[-1] = COLORS['green'] if monthly_cf_v >= 0 else COLORS['red']

        fig_wf = go.Figure(go.Waterfall(
            orientation='v',
            measure=['absolute'] + ['relative']*6 + ['total'],
            x=categories,
            y=values,
            connector=dict(line=dict(color='#2A3347', width=1)),
            increasing=dict(marker_color=COLORS['gold']),
            decreasing=dict(marker_color=COLORS['red']),
            totals=dict(marker_color=COLORS['green'] if monthly_cf_v >= 0 else COLORS['red']),
            text=[f'${v:,.0f}' for v in values],
            textposition='outside',
            textfont=dict(color='#E8EAF0', size=10),
        ))
        fig_wf.update_layout(**PLOT_LAYOUT, title='Monthly Cash Flow Waterfall', height=380,
                             title_font=dict(color='#E8EAF0', size=14))
        st.plotly_chart(fig_wf, use_container_width=True)

    with col2:
        # Expense donut
        exp_labels = ['Vacancy', 'Maintenance', 'Mgmt Fee', 'Property Tax', 'Insurance', 'Debt Service']
        exp_values = [rent - eff_rent, maint_amt, mgmt_amt, tax_amt, ins_amt, r['payment']]
        exp_colors = [COLORS['orange'], COLORS['blue'], COLORS['purple'],
                      COLORS['teal'], COLORS['gold'], COLORS['red']]

        fig_donut = go.Figure(go.Pie(
            labels=exp_labels, values=exp_values,
            hole=0.6, marker_colors=exp_colors,
            textinfo='percent', textfont=dict(size=11, color='#E8EAF0'),
            hovertemplate='%{label}<br>$%{value:,.2f}<extra></extra>'
        ))
        fig_donut.add_annotation(
            text=f'${rent:,.0f}<br><span style="font-size:10px">Gross/mo</span>',
            x=0.5, y=0.5, font_size=16, font_color='#E8EAF0', showarrow=False
        )
        fig_donut.update_layout(**PLOT_LAYOUT, title='Monthly Expense Breakdown',
                                height=380, title_font=dict(color='#E8EAF0', size=14),
                                showlegend=True)
        st.plotly_chart(fig_donut, use_container_width=True)

    # Detailed income statement
    st.markdown('<div class="section-title">📋 <span>Pro Forma Income Statement</span></div>',
                unsafe_allow_html=True)
    items = [
        ('Gross Scheduled Rent',       rent,       rent*12),
        ('Less: Vacancy Loss',         -(rent-eff_rent), -(rent-eff_rent)*12),
        ('Effective Gross Income',     eff_rent,   eff_rent*12),
        ('',                           '',          ''),
        ('Less: Maintenance',          -maint_amt, -maint_amt*12),
        ('Less: Management Fee',       -mgmt_amt,  -mgmt_amt*12),
        ('Less: Property Tax',         -tax_amt,   -tax_amt*12),
        ('Less: Insurance',            -ins_amt,   -ins_amt*12),
        ('Net Operating Income (NOI)', monthly_noi, monthly_noi*12),
        ('',                           '',          ''),
        ('Less: Debt Service (P&I)',   -r['payment'], -r['annual_debt']),
        ('NET CASH FLOW',              monthly_cf_v, r['annual_cf']),
    ]
    rows_data = []
    for item, mo, yr in items:
        if item == '':
            rows_data.append({'Item': '─' * 40, 'Monthly': '', 'Annual': ''})
        else:
            rows_data.append({
                'Item': item,
                'Monthly': f"${mo:,.2f}" if isinstance(mo, float) else '',
                'Annual':  f"${yr:,.2f}" if isinstance(yr, float) else '',
            })
    df_stmt = pd.DataFrame(rows_data)
    st.dataframe(df_stmt, use_container_width=True, hide_index=True, height=420)

# ════════════════════════════════════════════════════════════
# TAB 2 — SENSITIVITY
# ════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">🔄 <span>Sensitivity Analysis</span></div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        scenarios = ['Base Case', f'+{sens:.0f}% Stress', f'-{sens:.0f}% Upside']
        metrics_s = {
            'Cash-on-Cash (%)':  [r['coc'],    r_up['coc'],    r_down['coc']],
            'Cap Rate (%)':      [r['cap_rate'],r_up['cap_rate'],r_down['cap_rate']],
            'Annual CF ($K)':    [r['annual_cf']/1e3, r_up['annual_cf']/1e3, r_down['annual_cf']/1e3],
            'DSCR':              [r['dscr'],   r_up['dscr'],   r_down['dscr']],
        }
        bar_colors = [COLORS['gold'], COLORS['red'], COLORS['green']]
        fig_sens = go.Figure()
        for i, (scenario, color) in enumerate(zip(scenarios, bar_colors)):
            fig_sens.add_trace(go.Bar(
                name=scenario, x=list(metrics_s.keys()),
                y=[v[i] for v in metrics_s.values()],
                marker_color=color, opacity=0.85,
                text=[f'{v[i]:.2f}' for v in metrics_s.values()],
                textposition='outside', textfont=dict(color='#E8EAF0', size=10)
            ))
        fig_sens.update_layout(**PLOT_LAYOUT, title='Key Metrics by Scenario',
                               barmode='group', height=380,
                               title_font=dict(color='#E8EAF0', size=14))
        st.plotly_chart(fig_sens, use_container_width=True)

    with col2:
        # Sensitivity heatmap — cap rate vs vacancy
        vacancy_range = np.arange(0, 25, 2.5)
        rate_range    = np.arange(5.0, 10.5, 0.5)
        heat_data = []
        for v in vacancy_range:
            row_data = []
            for rt in rate_range:
                pp = {**p, 'vacancy': v, 'rate': rt}
                rr = full_analysis(pp)
                row_data.append(round(rr['cap_rate'], 2))
            heat_data.append(row_data)

        fig_heat = go.Figure(go.Heatmap(
            z=heat_data,
            x=[f'{rt:.1f}%' for rt in rate_range],
            y=[f'{v:.1f}%' for v in vacancy_range],
            colorscale=[[0,'#E74C3C'],[0.5,'#C9A84C'],[1,'#2ECC71']],
            text=[[f'{v:.1f}%' for v in row] for row in heat_data],
            texttemplate='%{text}', textfont=dict(size=9),
            hovertemplate='Rate: %{x}<br>Vacancy: %{y}<br>Cap Rate: %{z:.2f}%<extra></extra>'
        ))
        fig_heat.update_layout(**PLOT_LAYOUT,
                               title='Cap Rate Heatmap (Interest Rate vs Vacancy)',
                               height=380, title_font=dict(color='#E8EAF0', size=14),
                               xaxis_title='Interest Rate', yaxis_title='Vacancy Rate')
        st.plotly_chart(fig_heat, use_container_width=True)

    # Sensitivity table
    st.markdown("#### Scenario Comparison Table")
    sens_df = pd.DataFrame({
        'Metric': ['Monthly Cash Flow', 'Annual Cash Flow', 'Cap Rate', 'Cash-on-Cash', 'DSCR', 'Monthly Payment'],
        f'Base Case': [f"${r['monthly_cf']:,.0f}", f"${r['annual_cf']:,.0f}", f"{r['cap_rate']:.2f}%", f"{r['coc']:.2f}%", f"{r['dscr']:.2f}", f"${r['payment']:,.0f}"],
        f'+{sens:.0f}% Stress': [f"${r_up['monthly_cf']:,.0f}", f"${r_up['annual_cf']:,.0f}", f"{r_up['cap_rate']:.2f}%", f"{r_up['coc']:.2f}%", f"{r_up['dscr']:.2f}", f"${r_up['payment']:,.0f}"],
        f'-{sens:.0f}% Upside': [f"${r_down['monthly_cf']:,.0f}", f"${r_down['annual_cf']:,.0f}", f"{r_down['cap_rate']:.2f}%", f"{r_down['coc']:.2f}%", f"{r_down['dscr']:.2f}", f"${r_down['payment']:,.0f}"],
    })
    st.dataframe(sens_df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════
# TAB 3 — AMORTIZATION
# ════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">📅 <span>Amortization Schedule</span></div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        fig_am = go.Figure()
        fig_am.add_trace(go.Scatter(x=am['Month'], y=am['Payment'],  name='Total Payment',
                                    line=dict(color=COLORS['gold'], width=2.5)))
        fig_am.add_trace(go.Scatter(x=am['Month'], y=am['Principal'], name='Principal',
                                    line=dict(color=COLORS['green'], width=2)))
        fig_am.add_trace(go.Scatter(x=am['Month'], y=am['Interest'],  name='Interest',
                                    line=dict(color=COLORS['red'], width=2)))
        fig_am.update_layout(**PLOT_LAYOUT, title='Payment Breakdown Over Time',
                             height=360, title_font=dict(color='#E8EAF0', size=14),
                             yaxis_tickprefix='$', yaxis_tickformat=',.0f')
        st.plotly_chart(fig_am, use_container_width=True)

    with col2:
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(x=am['Month'], y=am['Balance'],
                                    fill='tozeroy', fillcolor='rgba(201,168,76,0.12)',
                                    line=dict(color=COLORS['gold'], width=2), name='Loan Balance'))
        fig_eq.add_trace(go.Scatter(x=am['Month'], y=am['Equity'],
                                    fill='tozeroy', fillcolor='rgba(46,204,113,0.12)',
                                    line=dict(color=COLORS['green'], width=2), name='Equity Built'))
        fig_eq.update_layout(**PLOT_LAYOUT, title='Balance vs Equity Over Time',
                             height=360, title_font=dict(color='#E8EAF0', size=14),
                             yaxis_tickprefix='$', yaxis_tickformat=',.0f')
        st.plotly_chart(fig_eq, use_container_width=True)

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Monthly Payment", f"${r['payment']:,.2f}")
    col2.metric("Total Paid", f"${r['total_payments']:,.0f}")
    col3.metric("Total Interest", f"${r['total_interest']:,.0f}")
    col4.metric("Equity at Year 5", f"${am[am['Month']==60]['Equity'].values[0]:,.0f}" if len(am) >= 60 else "N/A")

    st.markdown("#### Full Amortization Table")
    am_display = am.copy()
    for col in ['Payment','Principal','Interest','Balance','Cumul. Interest','Equity']:
        am_display[col] = am_display[col].apply(lambda x: f"${x:,.2f}")
    st.dataframe(am_display, use_container_width=True, hide_index=True, height=450)

# ════════════════════════════════════════════════════════════
# TAB 4 — PROJECTIONS
# ════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">📈 <span>Investment Projections</span></div>',
                unsafe_allow_html=True)

    years       = list(range(1, hold_yrs + 1))
    prop_values = [price * (1 + app_rate/100)**y for y in years]
    rents_proj  = [rent * (1 + rent_gr/100)**y for y in years]
    equity_proj = []
    cfs_proj    = []
    coc_proj    = []

    for y in years:
        bal_row = am[am['Month'] == y*12]
        bal = float(bal_row['Balance'].values[0]) if not bal_row.empty else 0
        eq  = prop_values[y-1] - bal
        equity_proj.append(eq)

        r_rent = rents_proj[y-1]
        pp_y   = {**p, 'rent': r_rent}
        ry     = full_analysis(pp_y)
        cfs_proj.append(ry['annual_cf'])
        coc_proj.append(ry['coc'])

    # Appreciation chart
    col1, col2 = st.columns(2)
    with col1:
        fig_proj = go.Figure()
        fig_proj.add_trace(go.Scatter(x=years, y=prop_values,
                                      line=dict(color=COLORS['gold'], width=2.5),
                                      fill='tozeroy', fillcolor='rgba(201,168,76,0.08)',
                                      name='Property Value'))
        fig_proj.add_trace(go.Scatter(x=years, y=equity_proj,
                                      line=dict(color=COLORS['green'], width=2.5),
                                      fill='tozeroy', fillcolor='rgba(46,204,113,0.08)',
                                      name='Total Equity'))
        fig_proj.add_hline(y=price, line=dict(color='#6B7A99', dash='dash', width=1),
                           annotation_text='Purchase Price', annotation_font_color='#6B7A99')
        fig_proj.update_layout(**PLOT_LAYOUT, title=f'Property Value & Equity ({app_rate}% appreciation/yr)',
                               height=360, title_font=dict(color='#E8EAF0', size=14),
                               yaxis_tickprefix='$', yaxis_tickformat=',.0f',
                               xaxis_title='Year')
        st.plotly_chart(fig_proj, use_container_width=True)

    with col2:
        fig_cf = go.Figure()
        bar_cols = [COLORS['green'] if v >= 0 else COLORS['red'] for v in cfs_proj]
        fig_cf.add_trace(go.Bar(x=years, y=cfs_proj, marker_color=bar_cols,
                                name='Annual Cash Flow',
                                text=[f'${v:,.0f}' for v in cfs_proj],
                                textposition='outside', textfont=dict(color='#E8EAF0', size=9)))
        fig_cf.update_layout(**PLOT_LAYOUT, title=f'Annual Cash Flow ({rent_gr}% rent growth/yr)',
                             height=360, title_font=dict(color='#E8EAF0', size=14),
                             yaxis_tickprefix='$', yaxis_tickformat=',.0f',
                             xaxis_title='Year')
        st.plotly_chart(fig_cf, use_container_width=True)

    # Total return at exit
    exit_price      = prop_values[-1]
    exit_balance    = float(am[am['Month'] == hold_yrs*12]['Balance'].values[0]) if hold_yrs*12 <= term else 0
    sale_proceeds   = exit_price * 0.94  # assume 6% selling costs
    equity_at_exit  = sale_proceeds - exit_balance
    total_cf        = sum(cfs_proj)
    total_return    = equity_at_exit - r['cash_required'] + total_cf
    roi             = (total_return / r['cash_required']) * 100 if r['cash_required'] > 0 else 0
    annualized_roi  = ((1 + roi/100)**(1/hold_yrs) - 1) * 100 if hold_yrs > 0 else 0

    st.markdown(f'<div class="section-title">🎯 <span>Exit Analysis — Year {hold_yrs}</span></div>',
                unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Exit Property Value",  f"${exit_price:,.0f}")
    c2.metric("Sale Proceeds (net)",  f"${sale_proceeds:,.0f}", delta="-6% selling costs")
    c3.metric("Equity at Exit",       f"${equity_at_exit:,.0f}")
    c4.metric("Total Cash Flow",      f"${total_cf:,.0f}")
    c5.metric("Annualized ROI",       f"{annualized_roi:.1f}%")

# ════════════════════════════════════════════════════════════
# TAB 5 — DEAL ANALYZER
# ════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">🏗️ <span>Deal Analyzer & Quick Checks</span></div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🧪 Rule-of-Thumb Checks")

        checks = [
            ("1% Rule", rent / price * 100 >= 1.0,
             f"Rent/Price = {rent/price*100:.2f}% (target ≥ 1.0%)",
             f"Monthly rent should be ≥ 1% of purchase price. Yours: ${rent:,.0f} / ${price:,.0f}"),
            ("50% Rule", (rent * 0.5) > r['payment'],
             f"50% expenses = ${rent*0.5:,.0f}, Payment = ${r['payment']:,.0f}",
             "50% of gross rent should cover all expenses (excl. debt service)"),
            ("DSCR ≥ 1.25", r['dscr'] >= 1.25,
             f"DSCR = {r['dscr']:.2f} (lenders require ≥ 1.25)",
             "Debt Service Coverage Ratio — NOI / Annual Debt Service"),
            ("Positive Cash Flow", r['monthly_cf'] > 0,
             f"Monthly CF = ${r['monthly_cf']:,.0f}",
             "Property generates positive cash flow after all expenses"),
            ("Cap Rate ≥ 5%", r['cap_rate'] >= 5.0,
             f"Cap Rate = {r['cap_rate']:.2f}% (target ≥ 5%)",
             "Net Operating Income / Purchase Price"),
            ("GRM < 15", r['grm'] < 15,
             f"GRM = {r['grm']:.1f}x (target < 15x)",
             "Gross Rent Multiplier — lower is better"),
            ("LTV ≤ 80%", r['ltv'] <= 80,
             f"LTV = {r['ltv']:.1f}% (target ≤ 80%)",
             "Loan-to-Value ratio"),
            ("70% Rule (Flip)", (price + repair) <= arv * 0.70,
             f"(Price + Repairs) = ${price+repair:,.0f}, 70% ARV = ${arv*0.7:,.0f}",
             "Max buy price for a flip = 70% of ARV minus repairs"),
        ]
        for name, passed, detail, tooltip in checks:
            icon = "✅" if passed else "❌"
            col = "#2ECC71" if passed else "#E74C3C"
            st.markdown(f"""
            <div style="background:#1C2333;border:1px solid {'#2A4A3A' if passed else '#4A2A2A'};
                         border-left:3px solid {col};
                         border-radius:8px;padding:10px 14px;margin-bottom:8px">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-weight:600;color:#E8EAF0">{icon} {name}</span>
                <span class="badge {'badge-green' if passed else 'badge-red'}">{'PASS' if passed else 'FAIL'}</span>
              </div>
              <div style="font-size:12px;color:#6B7A99;margin-top:4px;font-family:'DM Mono',monospace">{detail}</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### 📊 Comparable Metrics")

        # Spider/Radar chart of deal quality
        categories_radar = ['Cap Rate', '1% Rule', 'Cash Flow', 'DSCR', 'LTV (inv)', 'CoC Return']
        score_raw = [
            min(r['cap_rate'] / 10 * 100, 100),
            min(rent / price * 100 / 1.0 * 100, 100),
            min(max(r['monthly_cf'] / 500 * 100, 0), 100),
            min(r['dscr'] / 1.5 * 100, 100),
            min((100 - r['ltv']) / 30 * 100, 100),
            min(max(r['coc'] / 12 * 100, 0), 100),
        ]
        fig_radar = go.Figure(go.Scatterpolar(
            r=score_raw + [score_raw[0]],
            theta=categories_radar + [categories_radar[0]],
            fill='toself', fillcolor='rgba(201,168,76,0.15)',
            line=dict(color=COLORS['gold'], width=2),
            name='Your Deal'
        ))
        fig_radar.update_layout(
            **{k: v for k, v in PLOT_LAYOUT.items() if k != 'xaxis' and k != 'yaxis'},
            polar=dict(
                bgcolor='rgba(28,35,51,0.6)',
                radialaxis=dict(visible=True, range=[0, 100],
                               gridcolor='#2A3347', tickfont=dict(color='#6B7A99', size=9)),
                angularaxis=dict(gridcolor='#2A3347', tickfont=dict(color='#E8EAF0', size=10))
            ),
            title='Deal Quality Score', height=380,
            title_font=dict(color='#E8EAF0', size=14),
            showlegend=False
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Overall score
        overall = int(sum(score_raw) / len(score_raw))
        score_col = '#2ECC71' if overall >= 70 else '#C9A84C' if overall >= 50 else '#E74C3C'
        score_label = 'Strong Deal' if overall >= 70 else 'Average Deal' if overall >= 50 else 'Weak Deal'
        st.markdown(f"""
        <div style="background:#1C2333;border:1px solid #2A3347;border-radius:12px;
                    padding:20px;text-align:center;margin-top:8px">
          <div style="font-size:13px;color:#6B7A99;text-transform:uppercase;letter-spacing:1px">
            Overall Deal Score
          </div>
          <div style="font-family:'DM Serif Display',serif;font-size:52px;color:{score_col};line-height:1.1">
            {overall}
          </div>
          <div style="font-size:14px;color:{score_col};font-weight:600">{score_label}</div>
          <div style="font-size:11px;color:#6B7A99;margin-top:4px">out of 100</div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 6 — FULL REPORT
# ════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-title">📋 <span>Full Investment Report</span></div>',
                unsafe_allow_html=True)
    st.markdown(f"*Generated for: **{project_name}***")

    report_data = {
        'Category': [
            '── PROPERTY ──', 'Purchase Price', 'After Repair Value', 'Repair Costs',
            'ARV Equity', 'Closing Costs', '',
            '── FINANCING ──', 'Loan Amount', 'Down Payment', 'Interest Rate',
            'Loan Term', 'LTV', 'Monthly Payment (P&I)', 'Total Payments', 'Total Interest Paid', '',
            '── INCOME ──', 'Monthly Gross Rent', 'Annual Gross Rent',
            'Vacancy Loss (monthly)', 'Effective Gross Income (monthly)', '',
            '── EXPENSES ──', 'Maintenance (monthly)', 'Mgmt Fee (monthly)',
            'Property Tax (monthly)', 'Insurance (monthly)', 'Total Op. Expenses (monthly)', '',
            '── RETURNS ──', 'Monthly NOI', 'Annual NOI',
            'Monthly Cash Flow', 'Annual Cash Flow',
            'Cap Rate', 'Cash-on-Cash Return', 'Gross Rental Yield',
            'DSCR', 'GRM', 'Breakeven Occupancy', 'Max Purchase Price', '',
            '── EXIT (YEAR {} ) ──'.format(hold_yrs),
            'Projected Exit Value', 'Equity at Exit', 'Total Cumulative CF', 'Annualized ROI',
        ],
        'Value': [
            '', f"${price:,.0f}", f"${arv:,.0f}", f"${repair:,.0f}",
            f"${arv_equity:,.0f}", f"${closing:,.0f}", '',
            '', f"${loan:,.0f}", f"${r['down_payment']:,.0f}", f"{rate:.3f}%",
            f"{term} months ({term//12} yrs)", f"{r['ltv']:.1f}%",
            f"${r['payment']:,.2f}", f"${r['total_payments']:,.0f}", f"${r['total_interest']:,.0f}", '',
            '', f"${rent:,.0f}", f"${rent*12:,.0f}",
            f"${(rent - rent*(1-vacancy/100)):,.2f}", f"${rent*(1-vacancy/100):,.2f}", '',
            '', f"${maint_amt:,.2f}", f"${mgmt_amt:,.2f}",
            f"${tax_amt:,.2f}", f"${ins_amt:,.2f}", f"${total_exp:,.2f}", '',
            '', f"${monthly_noi:,.2f}", f"${r['noi']:,.2f}",
            f"${r['monthly_cf']:,.2f}", f"${r['annual_cf']:,.2f}",
            f"{r['cap_rate']:.2f}%", f"{r['coc']:.2f}%", f"{r['gross_yield']:.2f}%",
            f"{r['dscr']:.2f}x", f"{r['grm']:.1f}x",
            f"{r['breakeven_occ']:.1f}%", f"${r['max_price']:,.0f}", '',
            '',
            f"${exit_price:,.0f}", f"${equity_at_exit:,.0f}",
            f"${total_cf:,.0f}", f"{annualized_roi:.1f}%",
        ]
    }
    df_report = pd.DataFrame(report_data)
    st.dataframe(df_report, use_container_width=True, hide_index=True, height=900)

    # Download
    csv = df_report.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Full Report (CSV)",
        data=csv,
        file_name=f"{project_name.replace(' ','_')}_PropIQ_Report.csv",
        mime='text/csv'
    )

# ── FOOTER ────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:40px 0 20px;color:#2A3347;font-size:12px'>
  PropIQ · Real Estate Investment Analyzer · Not financial advice
</div>
""", unsafe_allow_html=True)
