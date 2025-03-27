import streamlit as st

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
st.markdown("- Set up multiple custom tariff rules")
st.markdown("- Simulate their economic impact")
st.markdown("- Visualize trade and macroeconomic outcomes")
