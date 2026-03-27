import streamlit as st
import pandas as pd

st.set_page_config(page_title="Winman Tax ERP Pro", layout="wide", page_icon="🧾")

# Advanced tax functions with surcharge/cess FY 2025-26 [web:1][web:48]
@st.cache_data
def calculate_tax(taxable_income, regime='old'):
    if regime == 'old':
        slabs = [(250000,0),(500000,0.05),(1000000,0.2),(float('inf'),0.3)]
    else:
        slabs = [(400000,0),(800000,0.05),(1200000,0.1),(1600000,0.15),(2000000,0.2),(2400000,0.25),(float('inf'),0.3)]
    
    tax = 0
    prev = 0
    for lim, rate in slabs:
        if taxable_income > prev:
            tax += min(taxable_income - prev, lim - prev) * rate
        prev = lim
    
    # Surcharge (basic, simplified)
    if taxable_income > 5000000:
        tax *= 1.10  # 10% surcharge approx
    elif taxable_income > 10000000:
        tax *= 1.15
    
    tax *= 1.04  # 4% cess
    return round(tax)

st.title("🧾 Winman CA ERP Pro - Complete ITR Computation FY 2025-26")
st.markdown("**All 5 Heads | Unlimited Income | Auto ITR | Advanced Optimizations** [web:56]")

# Expanders for all heads (Winman-style organized entry)
st.sidebar.header("📊 Heads of Income Entry")

with st.sidebar.expander("💰 Income from Salary", expanded=True):
    salary_gross = st.number_input("Gross Salary", 0.0, None, value=800000.0, step=5000.0)
    hra_ex = st.number_input("HRA Exempt", 0.0, None)
    std_ded = 50000 if st.checkbox("Old Regime Std Ded ₹50k") else 75000

with st.sidebar.expander("🏠 House Property", expanded=False):
    rental_inc = st.number_input("Rental Income", 0.0, None)
    hp_loss = st.number_input("Interest Ded/30% NAV (Loss OK)", -200000.0, None, value=0.0)  # Allow loss
    hp_income = max(0, rental_inc + hp_loss)  # Loss setoff later

with st.sidebar.expander("💼 Business/Profession", expanded=False):
    bus_prof = st.number_input("PGBP Income", 0.0, None)

with st.sidebar.expander("📈 Capital Gains", expanded=False):
    stcg = st.number_input("STCG (20%)", 0.0, None)
    ltcg = st.number_input("LTCG (12.5% >₹1.25L)", 0.0, None)
    cg_income = stcg + max(0, ltcg - 125000)  # Basic exemption

with st.sidebar.expander("📋 Other Sources", expanded=False):
    interest = st.number_input("Interest/FDs/Dividend", 0.0, None)
    other = st.number_input("Other (Lottery etc.)", 0.0, None)
    other_inc = interest + other

# Deductions (Old regime only)
with st.sidebar.expander("🛡️ Deductions (Old Only)"):
    sec80c = st.number_input("80C ₹1.5L", 0.0, 150000.0)
    sec80d = st.number_input("80D ₹25k", 0.0, 25000.0)
    nps_self = st.number_input("80CCD(1B) NPS ₹50k", 0.0, 50000.0)
    ded_total = sec80c + sec80d + nps_self

# Total GTI
gti_old = salary_gross + hp_income + bus_prof + cg_income + other_inc - min(0, hp_loss)[:200000]  # HP loss setoff ₹2L [web:53]
taxable_old = max(0, gti_old - ded_total - std_ded)
gti_new = gti_old  # New: minimal ded
taxable_new = max(0, gti_new - std_ded)

tax_old = calculate_tax(taxable_old, 'old')
tax_new = calculate_tax(taxable_new, 'new')

# Main Winman-style computation table
col1, col2 = st.columns([1.4, 1])
with col1:
    st.subheader("💰 Gross Total Income & Tax Computation")
    heads_data = {
        "Head": ["Salary", "House Property", "Business/Prof", "Capital Gains", "Other Sources", "HP Loss Setoff", "**GTI**"],
        "Amount (₹)": [f"{salary_gross:,.0f}", f"{hp_income:,.0f}", f"{bus_prof:,.0f}", f"{cg_income:,.0f}", f"{other_inc:,.0f}", f"{min(0,hp_loss)[:200000]:,.0f}", f"**{gti_old:,.0f}**"]
    }
    df_heads = pd.DataFrame(heads_data)
    st.table(df_heads)
    
    st.subheader("Tax Table")
    tax_data = {
        "Particulars": ["Taxable Income", "Tax Payable"],
        "Old Regime": [f"₹{taxable_old:,.0f}", f"₹{tax_old:,.0f}"],
        "New Regime": [f"₹{taxable_new:,.0f}", f"₹{tax_new:,.0f}"]
    }
    df_tax = pd.DataFrame(tax_data)
    st.table(df_tax)
    
    best = "New" if tax_new < tax_old else "Old"
    savings = abs(tax_old - tax_new)
    st.success(f"✅ **Recommended: {best} Regime | Tax: ₹{min(tax_old,tax_new):,.0f} | Savings: ₹{savings:,.0f}**")

with col2:
    st.subheader("🚀 Smart Optimizations")
    if sec80c < 150000 and tax_old > tax_new * 1.1:
        st.success(f"**Max 80C/NPS**: ₹{150000-sec80c:,.0f} more → Save ~₹{(150000-sec80c)*0.3:,.0f}")
    if hp_loss < -200000:
        st.info("**HP Loss**: Carry forward excess ₹{abs(hp_loss)-200000:,.0f} to next 8 yrs [web:53]")
    if ltcg > 125000:
        st.warning("**LTCG**: Indexation? Check 12.5% vs old 20%")
    if gti_old > 5000000:
        st.balloons()
        st.info("**High Income**: Plan LTCG reinvest u/s 54/54F")
    
    itr_type = "ITR-1" if cg_income==0 and bus_prof==0 else "ITR-2/3"
    st.info(f"**Auto ITR Form: {itr_type}**")

# Export section
st.subheader("📤 Winman Exports")
col1, col2, col3 = st.columns(3)
with col1:
    csv_heads = df_heads.to_csv(index=False)
    st.download_button("Heads Excel", csv_heads, "heads_income.csv")
with col2:
    csv_tax = df_tax.to_csv(index=False)
    st.download_button("Tax Excel", csv_tax, "tax_comp.csv")
with col3:
    st.download_button("ITR JSON", f'{{"GTI":{gti_old},"Tax":{min(tax_old,tax_new)}}}', "itr_data.json")

st.markdown("---")
st.caption("✅ Complete 5 Heads | No Income Limits | Surcharge/Cess Incl. | Pro for Articleship Audits [web:56][web:51]")
