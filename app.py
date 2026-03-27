import streamlit as st
import pandas as pd

st.set_page_config(page_title="Winman Tax ERP", layout="wide", page_icon="🧾")

# Tax logic FY 2025-26 [web:1]
@st.cache_data
def old_tax(taxable):
    slabs = [(250000,0),(500000,0.05),(1000000,0.2),(float('inf'),0.3)]
    tax = 0
    prev = 0
    for lim, rate in slabs:
        if taxable > prev:
            tax += min(taxable-prev, lim-prev) * rate
        prev = lim
    return tax

@st.cache_data
def new_tax(taxable):
    slabs = [(400000,0),(800000,0.05),(1200000,0.1),(1600000,0.15),(2000000,0.2),(2400000,0.25),(float('inf'),0.3)]
    tax = 0
    prev = 0
    for lim, rate in slabs:
        if taxable > prev:
            tax += min(taxable-prev, lim-prev) * rate
        prev = lim
    return tax

st.title("🧾 Winman CA ERP - Tax Computation FY 2025-26")
st.markdown("**Single Window | ITR Auto-Recommend | Old/New Compare | Optimizations** [web:33]")

# Sidebar data entry (Winman-style menu)
st.sidebar.header("📝 Assessee Data Entry")
gross = st.sidebar.number_input("Gross Salary (₹)", 0.0, 5000000.0, 800000.0)
sec80c = st.sidebar.number_input("80C (ELSS/PPF/NPS ₹1.5L max)", 0.0, 150000.0)
sec80d = st.sidebar.number_input("80D (Health ₹25k)", 0.0, 25000.0)
hra_ex = st.sidebar.number_input("HRA Exempt", 0.0, 200000.0)
nps_emp = st.sidebar.number_input("Employer NPS 80CCD(2)", 0.0, 100000.0)

# Main single window computation table
col1, col2 = st.columns([1.5,1])
with col1:
    st.subheader("💰 Computation Table (Winman Style)")
    ded_old = min(sec80c + sec80d + hra_ex, 225000)  # Approx caps
    taxable_old = max(0, gross - ded_old - 50000)  # Std ded
    tax_old = old_tax(taxable_old)
    
    taxable_new = max(0, gross - nps_emp - 75000)  # New std ded
    tax_new = new_tax(taxable_new)
    
    # Table like Winman expanding
    data = {
        "Head": ["Gross Income", "Deductions/Exempt", "Taxable Income", "Tax Payable"],
        "Old Regime": [f"₹{gross:,.0f}", f"₹{ded_old:,.0f}", f"₹{taxable_old:,.0f}", f"₹{tax_old:,.0f}"],
        "New Regime": ["", f"₹{nps_emp + 75000:,.0f}", f"₹{taxable_new:,.0f}", f"₹{tax_new:,.0f}"]
    }
    df = pd.DataFrame(data)
    st.table(df)
    
    best_regime = "New" if tax_new < tax_old else "Old"
    st.success(f"✅ **Best: {best_regime} Regime | Total Tax: ₹{min(tax_old, tax_new):,.0f}**")

with col2:
    st.subheader("⚡ Optimizations & Warnings")
    if sec80c < 150000 and tax_old > 10000:
        save = (150000 - sec80c) * 0.3
        st.balloons()
        st.success(f"**Max 80C**: Invest ₹{150000-sec80c:,.0f} more → Save ₹{save:,.0f} [80C/1B NPS]")
    if gross > 1000000 and tax_new < tax_old:
        st.info("**New Optimal**: Add Employer NPS (14% salary)")
    st.info("**Other**: HRA proof | Home loan 24(b) | Donations 80G")
    
    if taxable_old < gross * 0.5:
        st.warning("⚠️ Check HRA/80C proofs for audit")
    st.caption("Excl. 4% cess. Cap gains separate.[web:35]")

# Bottom bar: Export/ITR like Winman
st.subheader("📤 Generate/Export")
col3, col4, col5 = st.columns(3)
with col3:
    csv = df.to_csv(index=False)
    st.download_button("Excel Export", csv, "tax_comp.csv", "📊")
with col4:
    st.download_button("ITR Preview", "ITR Data", "itr.txt")
with col5:
    itr = "ITR-2" if gross > 500000 else "ITR-1"
    st.info(f"**Auto ITR: {itr}**")

st.markdown("---")
st.caption("🔒 Inspired by Winman single-window UI. For articleship use.[web:33]")
