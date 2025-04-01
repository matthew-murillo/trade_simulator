import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from plots import plot_baseline_vs_ctf, plot_pct_change, plot_decomposition, plot_trade_map

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

st.title("Results")
# Create a dropdown at the top left
st.sidebar.title("Select Results Category")
result_category = st.sidebar.selectbox(
    "Choose a category:",
    ["Production", "Imports", "Exports", "Labor", "Welfare"]
)

# Display selected result
st.title(f"{result_category}")

# ✅ Use `.get()` to prevent crashes if results do not exist
results = st.session_state.get("results", None)
baseline = st.session_state.get("d", None)
p = st.session_state.get("p", None)

if results is None:
    st.warning("No results found. Please run the model first.")
    st.stop()
else:
    results = st.session_state.results
    baseline = st.session_state.d
    p = st.session_state.p

    # Placeholder for showing results dynamically (replace with actual data processing logic)
    if result_category == "Production":

        # Create a dropdown for selecting either "All Countries" or a specific country
        selection_options = ["All Countries"] + list(p['c'])
        selected_option = st.selectbox("Choose a view:", selection_options)

        if selected_option == "All Countries":
            # Display results for all countries
            st.write("Displaying results for all countries...")
            # Production visualization
            ctf_go = np.sum(results['GO'], axis=0)
            baseline_go = np.sum(baseline['GO'], axis=0)
            go_hat = ctf_go / baseline_go
            q_hat = (go_hat / results['Pn_hat'])
            go_pct_change = np.round(((go_hat)-1)*100, 4)
            pn_pct_change = np.round(((results['Pn_hat'])-1)*100, 4)
            q_pct_change = np.round(((q_hat)-1)*100, 4)

            fig = plot_baseline_vs_ctf(
                p['c'], baseline_go, ctf_go,
                var_name="Gross Output", xaxis_label="Countries", yaxis_label="Gross Output (USD Million)",
                baseline_label="Baseline", ctf_label="Counterfactual",
                baseline_color="blue", ctf_color="red"
            )

            st.plotly_chart(fig, use_container_width=True)

            fig = plot_pct_change(
                p['c'], q_pct_change,
                var_name="Output % Change", xaxis_label="Countries", yaxis_label="Output % Change",
                pct_change_label="% Change")

            st.plotly_chart(fig, use_container_width=True)

            fig = plot_pct_change(
                p['c'], pn_pct_change,
                var_name="Prices", xaxis_label="Countries", yaxis_label="Prices % Change",
                pct_change_label="% Change")

            st.plotly_chart(fig, use_container_width=True)

            fig = plot_decomposition(
                p['c'], q_pct_change, pn_pct_change, go_pct_change,
                var_name="Gross Output", component_a_name="Quantity", component_b_name="Price",
                xaxis_label="Countries", yaxis_label="Decomposition (% Change from Baseline)")
            st.plotly_chart(fig, use_container_width=True)

        else:
            # Display results for a specific country
            st.write(f"Displaying results for {selected_option}...")
            # Production visualization
            ctf_go = results['GO'][:, p['c'] == selected_option].flatten()
            baseline_go = baseline['GO'][:, p['c']
                                         == selected_option].flatten()
            go_hat = results['GO']/baseline['GO']
            q_hat = go_hat / results['P_hat']
            go_pct_change = np.round(((go_hat)-1)*100, 4)
            pn_pct_change = np.round(((results['P_hat'])-1)*100, 4)
            q_pct_change = np.round(((q_hat)-1)*100, 4)

            # Country specific
            go_pct_change = go_pct_change[:,
                                          p['c'] == selected_option].flatten()
            pn_pct_change = pn_pct_change[:,
                                          p['c'] == selected_option].flatten()
            q_pct_change = q_pct_change[:, p['c'] == selected_option].flatten()

            fig = plot_baseline_vs_ctf(
                np.arange(len(p['s'])), baseline_go, ctf_go,
                var_name="Gross Output", xaxis_label="Sectors", yaxis_label="Gross Output (USD Million)",
                baseline_label="Baseline", ctf_label="Counterfactual",
                baseline_color="blue", ctf_color="red"
            )

            st.plotly_chart(fig, use_container_width=True)

            fig = plot_pct_change(
                np.arange(len(p['s'])), q_pct_change,
                var_name="Output", xaxis_label="Sectors", yaxis_label="Output % Change",
                pct_change_label="% Change")

            st.plotly_chart(fig, use_container_width=True)

            fig = plot_pct_change(
                np.arange(len(p['s'])), pn_pct_change,
                var_name="Prices", xaxis_label="Sectors", yaxis_label="Prices % Change",
                pct_change_label="% Change")

            st.plotly_chart(fig, use_container_width=True)

            fig = plot_decomposition(
                np.arange(
                    len(p['s'])), q_pct_change, pn_pct_change, go_pct_change,
                var_name="Gross Output", component_a_name="Quantity", component_b_name="Price",
                xaxis_label="Sectors", yaxis_label="Decomposition")
            st.plotly_chart(fig, use_container_width=True)

    elif result_category == "Imports":

        # Create a dropdown for selecting either "All Countries" or a specific country
        selection_options = ["All Countries"] + list(p['c'])
        selected_option = st.selectbox("Choose a view:", selection_options)

        if selected_option == "All Countries":
            st.write("Displaying results for all countries...")
            # Imports visualization
            ctf_m = np.sum(results['Im'], axis=0)
            baseline_m = np.sum(baseline['Im'], axis=0)
            m_hat = ctf_m / baseline_m
            m_pct_change = np.round(((m_hat)-1)*100, 4)

            fig = plot_pct_change(
                p['c'], m_pct_change,
                var_name="Imports % Change", xaxis_label="Countries", yaxis_label="Imports % Change",
                pct_change_label="% Change")

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.write(f"Displaying results for {selected_option}...")
            # Imports visualization
            ctf_m = results['Im'][:, p['c'] == selected_option].flatten()
            baseline_m = baseline['Im'][:, p['c'] == selected_option].flatten()
            m_hat = ctf_m / baseline_m
            m_pct_change = np.round(((m_hat)-1)*100, 4)
            ctf_xbilat = results['xbilat']
            baseline_xbilat = baseline['xbilat']

            fig = plot_pct_change(
                np.arange(len(p['s'])), m_pct_change,
                var_name=f"Imports by Sector for {selected_option}", xaxis_label="Sectors", yaxis_label="Imports % Change",
                pct_change_label="% Change")

            st.plotly_chart(fig, use_container_width=True)

            # ✅ Layout: dropdown in the left column, map in the right
            selected_sector = st.selectbox(
                "Sector", ["All"] + list(p['s']))

            if selected_sector == "All":
                sector_filter = None
                # Aggregate trade flows
                xbilat_agg_hat = np.sum(ctf_xbilat, axis=2) / \
                    np.sum(baseline_xbilat, axis=2)
                xbilat_agg_pct_change = np.round(
                    ((xbilat_agg_hat)-1)*100, 4)
                np.fill_diagonal(xbilat_agg_pct_change, 0)
                # replace nan with 0
                xbilat_agg_pct_change = np.nan_to_num(xbilat_agg_pct_change)

                # Country specific
                df = pd.DataFrame()
                df['country'] = p['c']
                df['sector'] = "All"
                df['trade_flow'] = xbilat_agg_pct_change[p['c']
                                                         == selected_option, :].flatten()
                fig = plot_trade_map(
                    df, selected_option, flow="Imports", sector=sector_filter)
                st.plotly_chart(fig, use_container_width=True)
            else:
                sector_filter = np.where(p['s'] == selected_sector)[0][0]
                # Aggregate trade flows
                xbilat_hat = ctf_xbilat / baseline_xbilat
                xbilat_pct_change = np.round(((xbilat_hat)-1)*100, 4)
                for j in range(p['J']):
                    np.fill_diagonal(xbilat_pct_change[:, :, j], 0)
                # replace nan with 0
                xbilat_pct_change = np.nan_to_num(xbilat_pct_change)
                # Country specific
                df = pd.DataFrame()
                df['country'] = p['c']
                df['sector'] = selected_sector
                df['trade_flow'] = xbilat_pct_change[p['c'] == selected_option,
                                                     :, p['s'] == selected_sector].flatten()

                fig = plot_trade_map(
                    df, selected_option, flow="Imports", sector=sector_filter)
                st.plotly_chart(fig, use_container_width=True)

    elif result_category == "Exports":

        # Create a dropdown for selecting either "All Countries" or a specific country
        selection_options = ["All Countries"] + list(p['c'])
        selected_option = st.selectbox("Choose a view:", selection_options)

        if selected_option == "All Countries":
            st.write("Displaying results for all countries...")
            # Imports visualization
            ctf_m = np.sum(results['Ex'], axis=0)
            baseline_m = np.sum(baseline['Ex'], axis=0)
            m_hat = ctf_m / baseline_m
            m_pct_change = np.round(((m_hat)-1)*100, 4)

            fig = plot_pct_change(
                p['c'], m_pct_change,
                var_name="Exports % Change", xaxis_label="Countries", yaxis_label="Exports % Change",
                pct_change_label="% Change")

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.write(f"Displaying results for {selected_option}...")
            # Imports visualization
            ctf_m = results['Ex'][:, p['c'] == selected_option].flatten()
            baseline_m = baseline['Ex'][:, p['c'] == selected_option].flatten()
            m_hat = ctf_m / baseline_m
            m_pct_change = np.round(((m_hat)-1)*100, 4)
            ctf_xbilat = results['xbilat']
            baseline_xbilat = baseline['xbilat']

            fig = plot_pct_change(
                np.arange(len(p['s'])), m_pct_change,
                var_name=f"Exports by Sector for {selected_option}", xaxis_label="Sectors", yaxis_label="Exports % Change",
                pct_change_label="% Change")

            st.plotly_chart(fig, use_container_width=True)

            # ✅ Layout: dropdown in the left column, map in the right
            selected_sector = st.selectbox(
                "Sector", ["All"] + list(p['s']))

            if selected_sector == "All":
                sector_filter = None
                # Aggregate trade flows
                xbilat_agg_hat = np.sum(ctf_xbilat, axis=2) / \
                    np.sum(baseline_xbilat, axis=2)
                xbilat_agg_pct_change = np.round(
                    ((xbilat_agg_hat)-1)*100, 4)
                np.fill_diagonal(xbilat_agg_pct_change, 0)
                # replace nan with 0
                xbilat_agg_pct_change = np.nan_to_num(xbilat_agg_pct_change)

                # Country specific
                df = pd.DataFrame()
                df['country'] = p['c']
                df['sector'] = "All"
                df['trade_flow'] = xbilat_agg_pct_change[:,
                                                         p['c'] == selected_option].flatten()
                fig = plot_trade_map(
                    df, selected_option, flow="Exports", sector=sector_filter)
                st.plotly_chart(fig, use_container_width=True)
            else:
                sector_filter = np.where(p['s'] == selected_sector)[0][0]
                # Aggregate trade flows
                xbilat_hat = ctf_xbilat / baseline_xbilat
                xbilat_pct_change = np.round(((xbilat_hat)-1)*100, 4)
                for j in range(p['J']):
                    np.fill_diagonal(xbilat_pct_change[:, :, j], 0)
                # replace nan with 0
                xbilat_pct_change = np.nan_to_num(xbilat_pct_change)
                # Country specific
                df = pd.DataFrame()
                df['country'] = p['c']
                df['sector'] = selected_sector
                df['trade_flow'] = xbilat_pct_change[:,
                                                     p['c'] == selected_option, p['s'] == selected_sector].flatten()

                fig = plot_trade_map(
                    df, selected_option, flow="Exports", sector=sector_filter)
                st.plotly_chart(fig, use_container_width=True)

    elif result_category == "Labor":

        # Create a dropdown for selecting either "All Countries" or a specific country
        selection_options = ["All Countries"] + list(p['c'])
        selected_option = st.selectbox("Choose a view:", selection_options)
        if selected_option == "All Countries":
            st.write("Displaying results for all countries...")
            # Labor visualization
            VA_hat = np.sum(results['VAnj'], axis=0) / \
                np.sum(baseline['VAnj'], axis=0)
            w_pct_change = np.round(((results['w_hat'])-1)*100, 4)

            fig = plot_pct_change(
                p['c'], w_pct_change,
                var_name="Wages % Change", xaxis_label="Countries", yaxis_label="Wages % Change",
                pct_change_label="% Change")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write(f"Displaying results for {selected_option}...")
            # Labor visualization
            VAnj_hat = results['VAnj']/baseline['VAnj']
            Lnj_hat = VAnj_hat/results['w_hat']
            Lnj_pct_change = np.round(((Lnj_hat)-1)*100, 4)
            np.nan_to_num(Lnj_pct_change)

            fig = plot_pct_change(
                np.arange(len(p['s'])), Lnj_pct_change[:,
                                                       p['c'] == selected_option].flatten(),
                var_name="Employment", xaxis_label="Sectors", yaxis_label="Employment % Change",
                pct_change_label="% Change")
            st.plotly_chart(fig, use_container_width=True)
    elif result_category == "Welfare":

        st.write("Displaying results for all countries...")
        income_hat = results['In'] / baseline['In']
        income_pct_change = np.round(((income_hat)-1)*100, 4)
        pn_pct_change = np.round(((results['Pn_hat'])-1)*100, 4)
        welfare_hat = income_hat/results['Pn_hat']
        welfare_pct_change = np.round(((welfare_hat)-1)*100, 4)

        # Comparing income between counterfactual and baseline for all countries
        fig = plot_baseline_vs_ctf(
            p['c'], results['In'], baseline['In'],
            var_name="Income", xaxis_label="Countries", yaxis_label="Income (USD Million)",
            baseline_label="Baseline", ctf_label="Counterfactual",
            baseline_color="blue", ctf_color="red"
        )

        st.plotly_chart(fig, use_container_width=True)
        # Percent change in welfare
        fig = plot_pct_change(
            p['c'], welfare_pct_change,
            var_name="Welfare % Change", xaxis_label="Countries", yaxis_label="Welfare % Change",
            pct_change_label="% Change")
        st.plotly_chart(fig, use_container_width=True)
        # Welfare decomposition
        fig = plot_decomposition(
            p['c'], income_pct_change, -pn_pct_change, welfare_pct_change,
            var_name="Welfare", component_a_name="Income", component_b_name="Prices",
            xaxis_label="Countries", yaxis_label="Decomposition (% Change from Baseline)")
        st.plotly_chart(fig, use_container_width=True)
