import os
import sys

import numpy as np
import pandas as pd
import streamlit as st


CURRENT = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(CURRENT)
PROJECT = os.path.abspath(os.path.join(CURRENT, '..', '..'))

if CODE_DIR not in sys.path:
    sys.path.append(CODE_DIR)

from plots import plot_baseline_vs_ctf, plot_decomposition, plot_pct_change, plot_trade_map
from ui_utils import format_selection, inject_base_styles, load_catalog, pct_change, render_page_header, safe_divide


def _round_frame(frame, digits=3):
    rounded = frame.copy()
    numeric_cols = rounded.select_dtypes(include=[np.number]).columns
    rounded[numeric_cols] = rounded[numeric_cols].round(digits)
    return rounded


def _top_abs(frame, metric, n=15):
    order = frame[metric].abs().sort_values(ascending=False).head(n).index
    return frame.loc[order]


def _sort_abs(frame, metric):
    return frame.reindex(frame[metric].abs().sort_values(ascending=False).index)


def _shorten_labels(values, max_chars=30):
    labels = []
    for value in values:
        text = str(value)
        if len(text) <= max_chars:
            labels.append(text)
        else:
            labels.append(text[: max_chars - 1] + "...")
    return labels


def _download_table(frame, slug):
    st.download_button(
        "Download current table",
        data=_round_frame(frame).to_csv(index=False).encode('utf-8'),
        file_name=f"{slug}.csv",
        mime='text/csv',
        use_container_width=True,
    )


inject_base_styles()

catalog = load_catalog(PROJECT)
country_name_map = dict(zip(catalog['countries']['code'], catalog['countries']['name']))
country_label_map = dict(zip(catalog['countries']['code'], catalog['countries']['label']))

render_page_header(
    "Results",
    "Read the scenario from the top down: first the headline shifts, then the category-specific charts, then the detailed table for export or further work.",
    kicker="Counterfactual Analysis",
)

results = st.session_state.get('results')
baseline = st.session_state.get('d')
p = st.session_state.get('p')
rules = st.session_state.get('rules', [])

if results is None or baseline is None or p is None:
    st.warning("No stored results were found. Run a scenario on the model page first.")
    if st.button("Go to model", use_container_width=True):
        st.switch_page("pages/Model.py")
    st.stop()

countries = np.asarray(p['c'])
country_lookup = {code: country_label_map.get(code, code) for code in countries}
country_names = [country_name_map.get(code, code) for code in countries]

if len(catalog['sectors']) == len(p['s']):
    sector_codes = np.asarray(catalog['sectors']['code'])
    sector_names = np.asarray(catalog['sectors']['name'])
    sector_lookup = dict(zip(catalog['sectors']['code'], catalog['sectors']['label']))
else:
    sector_codes = np.asarray(p['s'])
    sector_names = np.asarray(p['s'])
    sector_lookup = {code: code for code in sector_codes}

if rules:
    with st.expander("Scenario summary", expanded=False):
        summary_rows = []
        for idx, rule in enumerate(rules, start=1):
            summary_rows.append({
                'Rule': f'Rule {idx}',
                'Importers': format_selection(rule['importer']),
                'Exporters': format_selection(rule['exporter']),
                'Sectors': format_selection(rule['sectors']),
                'Policy': 'Free trade reset' if rule['free_trade'] else f"{rule['tariff_change']:.1f}%",
            })
        st.dataframe(summary_rows, use_container_width=True, hide_index=True)


baseline_output = np.sum(baseline['GO'], axis=0)
counterfactual_output = np.sum(results['GO'], axis=0)
output_hat = safe_divide(counterfactual_output, baseline_output)
price_hat = np.asarray(results['Pn_hat'], dtype=float)
real_output_hat = safe_divide(output_hat, price_hat)
income_hat = safe_divide(results['In'], baseline['In'])
welfare_hat = safe_divide(income_hat, price_hat)
value_added_hat = safe_divide(np.sum(results['VAnj'], axis=0), np.sum(baseline['VAnj'], axis=0))
employment_hat = safe_divide(value_added_hat, results['w_hat'])

country_summary = pd.DataFrame({
    'Country': countries,
    'Name': country_names,
    'Nominal output %': np.nan_to_num((output_hat - 1.0) * 100.0),
    'Price %': np.nan_to_num((price_hat - 1.0) * 100.0),
    'Real output %': np.nan_to_num((real_output_hat - 1.0) * 100.0),
    'Imports %': pct_change(np.sum(results['Im'], axis=0), np.sum(baseline['Im'], axis=0)),
    'Exports %': pct_change(np.sum(results['Ex'], axis=0), np.sum(baseline['Ex'], axis=0)),
    'Wage %': np.nan_to_num((np.asarray(results['w_hat'], dtype=float) - 1.0) * 100.0),
    'Employment %': np.nan_to_num((employment_hat - 1.0) * 100.0),
    'Income %': np.nan_to_num((income_hat - 1.0) * 100.0),
    'Welfare %': np.nan_to_num((welfare_hat - 1.0) * 100.0),
    'Baseline output': baseline_output,
    'Counterfactual output': counterfactual_output,
    'Baseline income': baseline['In'],
    'Counterfactual income': results['In'],
})

best_welfare = country_summary.loc[country_summary['Welfare %'].idxmax()]
worst_welfare = country_summary.loc[country_summary['Welfare %'].idxmin()]
largest_output = country_summary.loc[country_summary['Real output %'].abs().idxmax()]
avg_welfare = country_summary['Welfare %'].mean()

metric_cols = st.columns(4)
metric_cols[0].metric("Average welfare", f"{avg_welfare:+.2f}%")
metric_cols[1].metric(
    "Best welfare outcome",
    best_welfare['Country'],
    delta=f"{best_welfare['Welfare %']:+.2f}%",
)
metric_cols[2].metric(
    "Weakest welfare outcome",
    worst_welfare['Country'],
    delta=f"{worst_welfare['Welfare %']:+.2f}%",
)
metric_cols[3].metric(
    "Largest real-output move",
    largest_output['Country'],
    delta=f"{largest_output['Real output %']:+.2f}%",
)

category = st.radio(
    "Focus",
    ["Production", "Imports", "Exports", "Labor", "Welfare"],
    horizontal=True,
)

active_table = None

if category == "Production":
    scope = st.radio(
        "View",
        ["All countries", "Country detail"],
        horizontal=True,
        key='production_scope',
    )

    if scope == "All countries":
        top_real = _top_abs(country_summary, 'Real output %', n=18)
        comparison = country_summary.sort_values('Baseline output', ascending=False).head(15)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                plot_pct_change(
                    top_real['Country'],
                    top_real['Real output %'],
                    var_name="Real output",
                    xaxis_label="Countries",
                    yaxis_label="% change",
                ),
                use_container_width=True,
            )
        with col2:
            st.plotly_chart(
                plot_pct_change(
                    top_real['Country'],
                    top_real['Price %'],
                    var_name="Price level",
                    xaxis_label="Countries",
                    yaxis_label="% change",
                ),
                use_container_width=True,
            )

        st.plotly_chart(
            plot_baseline_vs_ctf(
                comparison['Country'],
                comparison['Baseline output'],
                comparison['Counterfactual output'],
                var_name="Gross output",
                xaxis_label="Countries",
                yaxis_label="Output",
            ),
            use_container_width=True,
        )

        active_table = _sort_abs(
            country_summary[[
                'Country',
                'Name',
                'Nominal output %',
                'Price %',
                'Real output %',
                'Baseline output',
                'Counterfactual output',
            ]],
            'Real output %',
        )
    else:
        selected_country = st.selectbox(
            "Country",
            options=countries,
            format_func=lambda code: country_lookup.get(code, code),
            key='production_country',
        )
        country_idx = int(np.where(countries == selected_country)[0][0])
        sector_frame = pd.DataFrame({
            'Sector code': sector_codes,
            'Sector': sector_names,
            'Baseline output': baseline['GO'][:, country_idx],
            'Counterfactual output': results['GO'][:, country_idx],
        })
        sector_nominal_hat = safe_divide(
            sector_frame['Counterfactual output'].to_numpy(),
            sector_frame['Baseline output'].to_numpy(),
        )
        sector_price_hat = np.asarray(results['P_hat'][:, country_idx], dtype=float)
        sector_real_hat = safe_divide(sector_nominal_hat, sector_price_hat)
        sector_frame['Nominal output %'] = np.nan_to_num((sector_nominal_hat - 1.0) * 100.0)
        sector_frame['Price %'] = np.nan_to_num((sector_price_hat - 1.0) * 100.0)
        sector_frame['Real output %'] = np.nan_to_num((sector_real_hat - 1.0) * 100.0)

        top_sectors = _top_abs(sector_frame, 'Real output %', n=12)
        sector_labels = _shorten_labels(top_sectors['Sector'])

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                plot_baseline_vs_ctf(
                    sector_labels,
                    top_sectors['Baseline output'],
                    top_sectors['Counterfactual output'],
                    var_name=f"Gross output for {selected_country}",
                    xaxis_label="Sectors",
                    yaxis_label="Output",
                ),
                use_container_width=True,
            )
        with col2:
            st.plotly_chart(
                plot_decomposition(
                    sector_labels,
                    top_sectors['Real output %'],
                    top_sectors['Price %'],
                    top_sectors['Nominal output %'],
                    var_name=f"Output drivers for {selected_country}",
                    component_a_name="Real output",
                    component_b_name="Prices",
                    xaxis_label="Sectors",
                    yaxis_label="% change",
                ),
                use_container_width=True,
            )

        active_table = _sort_abs(
            sector_frame[['Sector code', 'Sector', 'Baseline output', 'Counterfactual output', 'Nominal output %', 'Price %', 'Real output %']],
            'Real output %',
        )

elif category == "Imports":
    scope = st.radio(
        "View",
        ["All countries", "Country detail"],
        horizontal=True,
        key='imports_scope',
    )

    imports_frame = country_summary[['Country', 'Name', 'Imports %']].copy()

    if scope == "All countries":
        movers = _top_abs(imports_frame, 'Imports %', n=18)
        st.plotly_chart(
            plot_pct_change(
                movers['Country'],
                movers['Imports %'],
                var_name="Imports",
                xaxis_label="Countries",
                yaxis_label="% change",
            ),
            use_container_width=True,
        )
        active_table = _sort_abs(imports_frame, 'Imports %')
    else:
        selected_country = st.selectbox(
            "Country",
            options=countries,
            format_func=lambda code: country_lookup.get(code, code),
            key='imports_country',
        )
        country_idx = int(np.where(countries == selected_country)[0][0])
        sector_frame = pd.DataFrame({
            'Sector code': sector_codes,
            'Sector': sector_names,
            'Imports %': pct_change(results['Im'][:, country_idx], baseline['Im'][:, country_idx]),
            'Baseline imports': baseline['Im'][:, country_idx],
            'Counterfactual imports': results['Im'][:, country_idx],
        })
        top_sectors = _top_abs(sector_frame, 'Imports %', n=12)

        st.plotly_chart(
            plot_pct_change(
                _shorten_labels(top_sectors['Sector']),
                top_sectors['Imports %'],
                var_name=f"Imports for {selected_country}",
                xaxis_label="Sectors",
                yaxis_label="% change",
            ),
            use_container_width=True,
        )

        sector_choice = st.selectbox(
            "Partner map sector",
            options=["All sectors"] + list(sector_codes),
            format_func=lambda code: sector_lookup.get(code, code),
            key='imports_partner_sector',
        )
        if sector_choice == "All sectors":
            partner_pct = pct_change(np.sum(results['xbilat'], axis=2), np.sum(baseline['xbilat'], axis=2))
            sector_label = None
        else:
            sector_idx = int(np.where(sector_codes == sector_choice)[0][0])
            partner_pct = pct_change(results['xbilat'][:, :, sector_idx], baseline['xbilat'][:, :, sector_idx])
            sector_label = sector_lookup.get(sector_choice, sector_choice)
        np.fill_diagonal(partner_pct, 0.0)

        partner_frame = pd.DataFrame({
            'Country': countries,
            'Name': country_names,
            'Imports %': partner_pct[country_idx, :],
        })
        partner_frame = partner_frame[partner_frame['Country'] != selected_country]
        partner_frame = _sort_abs(partner_frame, 'Imports %')

        map_df = pd.DataFrame({
            'country': partner_frame['Country'],
            'sector': sector_choice,
            'trade_flow': partner_frame['Imports %'],
        })
        st.plotly_chart(
            plot_trade_map(map_df, selected_country, flow="Imports", sector=sector_label),
            use_container_width=True,
        )

        active_table = _sort_abs(
            sector_frame[['Sector code', 'Sector', 'Baseline imports', 'Counterfactual imports', 'Imports %']],
            'Imports %',
        )
        st.markdown("#### Partner detail")
        st.dataframe(_round_frame(partner_frame), use_container_width=True, hide_index=True)

elif category == "Exports":
    scope = st.radio(
        "View",
        ["All countries", "Country detail"],
        horizontal=True,
        key='exports_scope',
    )

    exports_frame = country_summary[['Country', 'Name', 'Exports %']].copy()

    if scope == "All countries":
        movers = _top_abs(exports_frame, 'Exports %', n=18)
        st.plotly_chart(
            plot_pct_change(
                movers['Country'],
                movers['Exports %'],
                var_name="Exports",
                xaxis_label="Countries",
                yaxis_label="% change",
            ),
            use_container_width=True,
        )
        active_table = _sort_abs(exports_frame, 'Exports %')
    else:
        selected_country = st.selectbox(
            "Country",
            options=countries,
            format_func=lambda code: country_lookup.get(code, code),
            key='exports_country',
        )
        country_idx = int(np.where(countries == selected_country)[0][0])
        sector_frame = pd.DataFrame({
            'Sector code': sector_codes,
            'Sector': sector_names,
            'Exports %': pct_change(results['Ex'][:, country_idx], baseline['Ex'][:, country_idx]),
            'Baseline exports': baseline['Ex'][:, country_idx],
            'Counterfactual exports': results['Ex'][:, country_idx],
        })
        top_sectors = _top_abs(sector_frame, 'Exports %', n=12)

        st.plotly_chart(
            plot_pct_change(
                _shorten_labels(top_sectors['Sector']),
                top_sectors['Exports %'],
                var_name=f"Exports for {selected_country}",
                xaxis_label="Sectors",
                yaxis_label="% change",
            ),
            use_container_width=True,
        )

        sector_choice = st.selectbox(
            "Partner map sector",
            options=["All sectors"] + list(sector_codes),
            format_func=lambda code: sector_lookup.get(code, code),
            key='exports_partner_sector',
        )
        if sector_choice == "All sectors":
            partner_pct = pct_change(np.sum(results['xbilat'], axis=2), np.sum(baseline['xbilat'], axis=2))
            sector_label = None
        else:
            sector_idx = int(np.where(sector_codes == sector_choice)[0][0])
            partner_pct = pct_change(results['xbilat'][:, :, sector_idx], baseline['xbilat'][:, :, sector_idx])
            sector_label = sector_lookup.get(sector_choice, sector_choice)
        np.fill_diagonal(partner_pct, 0.0)

        partner_frame = pd.DataFrame({
            'Country': countries,
            'Name': country_names,
            'Exports %': partner_pct[:, country_idx],
        })
        partner_frame = partner_frame[partner_frame['Country'] != selected_country]
        partner_frame = _sort_abs(partner_frame, 'Exports %')

        map_df = pd.DataFrame({
            'country': partner_frame['Country'],
            'sector': sector_choice,
            'trade_flow': partner_frame['Exports %'],
        })
        st.plotly_chart(
            plot_trade_map(map_df, selected_country, flow="Exports", sector=sector_label),
            use_container_width=True,
        )

        active_table = _sort_abs(
            sector_frame[['Sector code', 'Sector', 'Baseline exports', 'Counterfactual exports', 'Exports %']],
            'Exports %',
        )
        st.markdown("#### Partner detail")
        st.dataframe(_round_frame(partner_frame), use_container_width=True, hide_index=True)

elif category == "Labor":
    scope = st.radio(
        "View",
        ["All countries", "Country detail"],
        horizontal=True,
        key='labor_scope',
    )

    labor_frame = country_summary[['Country', 'Name', 'Wage %', 'Employment %']].copy()

    if scope == "All countries":
        movers = _top_abs(labor_frame, 'Employment %', n=18)
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                plot_pct_change(
                    movers['Country'],
                    movers['Wage %'],
                    var_name="Wages",
                    xaxis_label="Countries",
                    yaxis_label="% change",
                ),
                use_container_width=True,
            )
        with col2:
            st.plotly_chart(
                plot_pct_change(
                    movers['Country'],
                    movers['Employment %'],
                    var_name="Employment",
                    xaxis_label="Countries",
                    yaxis_label="% change",
                ),
                use_container_width=True,
            )
        active_table = _sort_abs(labor_frame, 'Employment %')
    else:
        selected_country = st.selectbox(
            "Country",
            options=countries,
            format_func=lambda code: country_lookup.get(code, code),
            key='labor_country',
        )
        country_idx = int(np.where(countries == selected_country)[0][0])
        sector_value_added_hat = safe_divide(results['VAnj'][:, country_idx], baseline['VAnj'][:, country_idx])
        sector_employment_hat = safe_divide(sector_value_added_hat, results['w_hat'][country_idx])
        sector_frame = pd.DataFrame({
            'Sector code': sector_codes,
            'Sector': sector_names,
            'Value added %': np.nan_to_num((sector_value_added_hat - 1.0) * 100.0),
            'Employment %': np.nan_to_num((sector_employment_hat - 1.0) * 100.0),
        })
        top_sectors = _top_abs(sector_frame, 'Employment %', n=12)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                plot_pct_change(
                    _shorten_labels(top_sectors['Sector']),
                    top_sectors['Value added %'],
                    var_name=f"Value added for {selected_country}",
                    xaxis_label="Sectors",
                    yaxis_label="% change",
                ),
                use_container_width=True,
            )
        with col2:
            st.plotly_chart(
                plot_pct_change(
                    _shorten_labels(top_sectors['Sector']),
                    top_sectors['Employment %'],
                    var_name=f"Employment for {selected_country}",
                    xaxis_label="Sectors",
                    yaxis_label="% change",
                ),
                use_container_width=True,
            )

        active_table = _sort_abs(
            sector_frame[['Sector code', 'Sector', 'Value added %', 'Employment %']],
            'Employment %',
        )

else:
    welfare_frame = country_summary[[
        'Country',
        'Name',
        'Income %',
        'Price %',
        'Welfare %',
        'Baseline income',
        'Counterfactual income',
    ]].copy()

    top_welfare = _top_abs(welfare_frame, 'Welfare %', n=18)
    comparison = welfare_frame.sort_values('Baseline income', ascending=False).head(15)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            plot_baseline_vs_ctf(
                comparison['Country'],
                comparison['Baseline income'],
                comparison['Counterfactual income'],
                var_name="Income",
                xaxis_label="Countries",
                yaxis_label="Income",
            ),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            plot_decomposition(
                top_welfare['Country'],
                top_welfare['Income %'],
                -top_welfare['Price %'],
                top_welfare['Welfare %'],
                var_name="Welfare",
                component_a_name="Income",
                component_b_name="Prices",
                xaxis_label="Countries",
                yaxis_label="% change",
            ),
            use_container_width=True,
        )

    st.plotly_chart(
        plot_pct_change(
            top_welfare['Country'],
            top_welfare['Welfare %'],
            var_name="Welfare",
            xaxis_label="Countries",
            yaxis_label="% change",
        ),
        use_container_width=True,
    )

    active_table = _sort_abs(welfare_frame, 'Welfare %')


st.markdown("### Detail table")
if active_table is not None:
    table_col, download_col = st.columns([4, 1])
    with download_col:
        _download_table(active_table, f"{category.lower()}_results")
    with table_col:
        st.caption("Rounded for display. Download the CSV if you want the current slice outside the app.")
    st.dataframe(_round_frame(active_table), use_container_width=True, hide_index=True)
