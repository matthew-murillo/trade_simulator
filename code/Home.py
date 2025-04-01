import pandas as pd
import streamlit as st
import os

PROJECT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT = os.path.join(PROJECT, 'output')
DATA = os.path.join(PROJECT, 'data')
dictionary = pd.read_csv(os.path.join(DATA, 'dictionary.csv'))
c = dictionary['country'].dropna()
c_name = dictionary['c_name'].dropna()
s = dictionary['sector'].dropna()
s_name = dictionary['s_name'].dropna()

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 3rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Trade Simulator")

# --- Tabs ---
tab_overview, tab_data, tab_model = st.tabs(
    ["Overview", "Data", "Model"])

with tab_overview:
    st.subheader("Overview")
    st.markdown("""
    This is a multi-county, multi-sector, quantitative general equilibrium trade model with input-output linkages. The goal of this project is to allow users to simulate the impacts of trade policy changes on changes in:
    - Output
    - Trade flows
    - Prices
    - Employment
    - Welfare
    - etc ...            
    """)

    st.markdown("""
    The model is designed to be user-friendly and accessible to a wide audience, including policymakers, researchers, and students. Users can input their own trade policies, see the resulting economic impacts, and download all results for further analysis. The original codes that solve the model can be found [here](https://github.com/matthew-murillo/trade_simulator) along with all the necessary data. 
    """)

    st.markdown("#### References:")
    st.markdown("- Caliendo, L., Parro, F. (2015) Estimates of the Trade and Welfare Effects of NAFTA, *Review of Economic Studies*, 82(1), 1-44.")
    st.markdown(
        "- OECD. (2023) OECD Inter-Country Input-Output Tables, http://oe.cd/icio")

with tab_data:
    st.markdown("### Data Overview")
    st.markdown("""
    The model uses the OECD Inter-Country Input-Output Tables as its main data source. The model is calibrated to 77 countries and 45 sectors. The only parameters that are estimated from the data are the trade elasticities $(\\theta^j)$. The rest of the fundamentals can be backed out directly from the data. The follow table lists all countries and sectors used in the model. 
    """)
    st.markdown("#### Countries")
    c = pd.DataFrame(c)
    c["names"] = c_name
    c = c.rename(columns={"country": "Country Code", "names": "Country"})
    c.index = range(1, len(c) + 1)
    st.dataframe(c, use_container_width=True)
    st.markdown("#### Sectors")
    s = pd.DataFrame(s)
    s["names"] = s_name
    s = s.rename(columns={"sector": "Sector Code", "names": "Sector"})
    s.index = range(1, len(s) + 1)
    st.dataframe(s, use_container_width=True)

with tab_model:
    st.markdown("### Model Overview")
    st.markdown("""
    Given a set of fundamentals $\\left\{\\pi_{ni}^j, \\gamma_n^j, \\gamma_n^{k,j}, w_nL_n, \\alpha_n^j, \\theta^j  \\right\}$ (trade shares, value added shares, expenditure shares on intermediates, value added, final consumption shares, productivity dispersion) about the economy and counterfactual changes in tariffs, the equilibrium is defined as the vector of prices $(\\hat{w}, \\hat{P})$ that satisfies: 
    1. **Input cost bundle**
                
    $$
    \\hat{c}_n^j = \\hat{w}_n^{\\gamma_n^j} \\prod_{k=1}^J (\\hat{P}_n^k)^{\\gamma_n^{k,j}}
    $$
                
    2. **Price index**
                
    $$
    \\hat{P}_n^j = \\left[\sum_{i=1}^N \\pi_{ni}^j \\left(\\hat{\\tau}_{ni}^j \\hat{c}_i^j  \\right)^{-\\theta^j}   \\right]^{-1/\\theta^j}
    $$
                
    3. **Bilateral trade shares**
    
    $$
    \\hat{\\pi}_{ni}^j = \\left[\\frac{\\hat{\\tau}_{ni}^j\\hat{c}_i^j}{\\hat{P}_n^j}\\right]^{-\\theta^j}            
    $$
                
    4. **Expenditure in each country $n$ and sector $j$**

    $$
    X_n^{j\\prime} = \\sum_{k=1}^J \\gamma_n^{k,j} \\sum_{i=1}^N X_i^{k\\prime} \\frac{\\pi_{in}^{k\\prime}}{\\tau_{in}^{k\\prime}} + \\alpha_n^j \\left(\\hat{w}_n w_nL_n + \\sum_{j=1}^J\\sum_{i=1}^N X_n^{j\\prime} (\\tau_{ni}^{j\\prime}-1) \\frac{\\pi_{ni}^{j\\prime}}{\\tau_{ni}^{j\\prime}}  +D_n \\right)
    $$
    
    """)
