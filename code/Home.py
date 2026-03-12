import os

import pandas as pd
import streamlit as st

from ui_utils import inject_base_styles, load_catalog, render_page_header, render_section_card


PROJECT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

catalog = load_catalog(PROJECT)
countries = catalog['countries']
sectors = catalog['sectors']

inject_base_styles()

render_page_header(
    "Trade Simulator",
    "Build tariff scenarios, solve the multi-country equilibrium, and compare how output, trade, labor, and welfare move under the counterfactual.",
    kicker="Quantitative General Equilibrium",
)

metric_cols = st.columns(4)
metric_cols[0].metric("Countries", len(countries))
metric_cols[1].metric("Sectors", len(sectors))
metric_cols[2].metric("Outputs", "5 views")
metric_cols[3].metric("Catalog source", catalog['source'])

overview_tab, data_tab, model_tab = st.tabs(["Overview", "Coverage", "Model"])

with overview_tab:
    render_section_card(
        "What this app does",
        "This interface solves a Caliendo-Parro style trade model with input-output linkages. You can define tariffs or free-trade counterfactuals, run the equilibrium, and inspect how the scenario shifts output, prices, wages, trade flows, and welfare.",
    )
    st.markdown(
        """
        <div class="section-card">
            <h3>Why it is useful</h3>
            <p>
                The simulator is designed for quick policy experiments without losing the structure of the underlying model.
                It is a good fit for classroom demos, internal policy notes, and exploratory scenario work where you want
                to compare baseline and counterfactual outcomes side by side.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("#### References")
    st.markdown(
        "- Caliendo, L., Parro, F. (2015). Estimates of the Trade and Welfare Effects of NAFTA, *Review of Economic Studies*, 82(1), 1-44."
    )
    st.markdown("- OECD. (2023). OECD Inter-Country Input-Output Tables, http://oe.cd/icio")

with data_tab:
    render_section_card(
        "Coverage",
        f"The current calibration exposes {len(countries)} countries and {len(sectors)} sectors. Catalog labels are being loaded from `{catalog['source']}` in this workspace.",
    )

    country_df = countries[['code', 'name']].rename(
        columns={'code': 'Country code', 'name': 'Country'}
    )
    sector_df = sectors[['code', 'name']].rename(
        columns={'code': 'Sector code', 'name': 'Sector'}
    )

    country_df.index = range(1, len(country_df) + 1)
    sector_df.index = range(1, len(sector_df) + 1)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Countries")
        st.dataframe(country_df, use_container_width=True)
    with col2:
        st.markdown("#### Sectors")
        st.dataframe(sector_df, use_container_width=True)

with model_tab:
    render_section_card(
        "Model structure",
        "The equilibrium is pinned down by input costs, sectoral price indices, bilateral trade shares, expenditure propagation through the input-output network, and the labor-market clearing condition.",
    )

    st.markdown(
        """
        1. **Input cost bundle**

        $$
        \hat{c}_n^j = \hat{w}_n^{\gamma_n^j}\prod_{k=1}^J(\hat{P}_n^k)^{\gamma_n^{k,j}}
        $$

        2. **Price index**

        $$
        \hat{P}_n^j = \left[\sum_{i=1}^N \pi_{ni}^j\left(\hat{\tau}_{ni}^j\hat{c}_i^j\right)^{-\theta^j}\right]^{-1/\theta^j}
        $$

        3. **Bilateral trade shares**

        $$
        \hat{\pi}_{ni}^j = \left[\frac{\hat{\tau}_{ni}^j\hat{c}_i^j}{\hat{P}_n^j}\right]^{-\theta^j}
        $$

        4. **Expenditure recursion**

        $$
        X_n^{j\prime} = \sum_{k=1}^J \gamma_n^{k,j}\sum_{i=1}^N X_i^{k\prime}
        \frac{\pi_{in}^{k\prime}}{\tau_{in}^{k\prime}}
        + \alpha_n^j\left(\hat{w}_n w_nL_n + \sum_{j=1}^J\sum_{i=1}^N X_n^{j\prime}
        (\tau_{ni}^{j\prime}-1)\frac{\pi_{ni}^{j\prime}}{\tau_{ni}^{j\prime}} + D_n\right)
        $$
        """
    )
