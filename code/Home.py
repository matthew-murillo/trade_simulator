import pandas as pd
import streamlit as st
import os
PROJECT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT = os.path.join(PROJECT, 'output')
DATA = os.path.join(PROJECT, 'data')
dictionary = pd.read_csv(os.path.join(DATA, 'dictionary.csv'))
c = dictionary['country'].dropna()
s = dictionary['sector'].dropna()

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Trade Simulator")
st.subheader("Overview")
st.markdown("""
This is a multi-county, multi-sector, quantitative general equilibrium trade model with input-output linkages.
""")

st.markdown("#### What you can do:")
st.markdown("- Experiment with different trade policies")
st.markdown("- Simulate their economic impact")
st.markdown("- Visualize trade and economic outcomes")

st.sidebar.markdown("### Sector Codes")

# Create two columns in the sidebar
col1, col2 = st.sidebar.columns([2, 1])
col1.markdown("**Sector**")
col2.markdown("**Code**")

# Display sector names and codes side by side
for sector, code in zip(s, range(len(s))):
    c1, c2 = st.sidebar.columns([2, 1])
    c1.write(sector)
    c2.write(code)
