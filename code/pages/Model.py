import io
import os
import sys
import uuid

import streamlit as st


CURRENT = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(CURRENT)
PROJECT = os.path.abspath(os.path.join(CURRENT, '..', '..'))

if CODE_DIR not in sys.path:
    sys.path.append(CODE_DIR)

from QGE.main import run
from ui_utils import format_selection, inject_base_styles, load_catalog, render_page_header


catalog = load_catalog(PROJECT)
country_df = catalog['countries']
sector_df = catalog['sectors']

country_options = country_df['code'].tolist()
sector_options = sector_df['code'].tolist()
country_labels = dict(zip(country_df['code'], country_df['label']))
sector_labels = dict(zip(sector_df['code'], sector_df['label']))


class StreamlitLogger(io.StringIO):
    def __init__(self, container):
        super().__init__()
        self.container = container
        self.messages = []

    def write(self, message):
        cleaned = message.strip()
        if cleaned:
            self.messages.append(cleaned)
            self.container.code("\n".join(self.messages[-12:]), language="text")

    def flush(self):
        return None


def _init_state():
    st.session_state.setdefault('results', None)
    st.session_state.setdefault('d', None)
    st.session_state.setdefault('p', None)
    st.session_state.setdefault('rules', [])
    st.session_state.setdefault('model_ran', False)
    st.session_state.setdefault('last_run_rule_count', 0)


def _cleanup_rule_state(rule_id):
    for key in ('importer', 'exporter', 'sectors', 'free_trade', 'tariff'):
        st.session_state.pop(f'{key}_{rule_id}', None)


def _build_policy_payload(rules):
    payload = {}
    for rule in rules:
        payload[rule['id']] = [{
            'importer_indices': [
                country_options.index(code) for code in rule['importer']
                if code in country_options
            ],
            'exporter_indices': [
                country_options.index(code) for code in rule['exporter']
                if code in country_options
            ],
            'sector_indices': [
                sector_options.index(code) for code in rule['sectors']
                if code in sector_options
            ],
            'free_trade': rule['free_trade'],
            'tariff_change': rule['tariff_change'],
        }]
    return payload


def _summary_table(rules):
    rows = []
    for idx, rule in enumerate(rules, start=1):
        rows.append({
            'Rule': f'Rule {idx}',
            'Importers': format_selection(rule['importer']),
            'Exporters': format_selection(rule['exporter']),
            'Sectors': format_selection(rule['sectors']),
            'Policy': 'Free trade reset' if rule['free_trade'] else f"{rule['tariff_change']:.1f}%",
        })
    return rows


inject_base_styles()
_init_state()

render_page_header(
    "Policy Builder",
    "Create tariff or free-trade rules, review the scenario at a glance, and run the counterfactual when the package looks right.",
    kicker="Scenario Design",
)

if catalog['source'] != 'dictionary.csv':
    st.info(
        f"Catalog labels are loading from `{catalog['source']}` because `data/dictionary.csv` is not available in this workspace."
    )

headline_cols = st.columns(4)
headline_cols[0].metric("Policy rules", len(st.session_state.rules))
headline_cols[1].metric("Countries available", len(country_options))
headline_cols[2].metric("Sectors available", len(sector_options))
headline_cols[3].metric(
    "Results ready",
    "Yes" if st.session_state.results is not None else "No",
    delta=f"{st.session_state.last_run_rule_count} rules last run"
    if st.session_state.model_ran else None,
)

action_cols = st.columns([1, 1, 2])
if action_cols[0].button("Add policy rule", use_container_width=True):
    st.session_state.rules.append({
        'id': str(uuid.uuid4()),
        'importer': [],
        'exporter': [],
        'sectors': [],
        'free_trade': False,
        'tariff_change': 0.0,
    })

if action_cols[1].button(
    "Clear all",
    use_container_width=True,
    disabled=not st.session_state.rules,
):
    for rule in st.session_state.rules:
        _cleanup_rule_state(rule['id'])
    st.session_state.rules = []

action_cols[2].markdown(
    """
    <div class="section-card">
        <h4>Scope rule</h4>
        <p>Leave an importer, exporter, or sector list blank to apply the rule to the full set in that dimension.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

updated_rules = []

for idx, rule in enumerate(st.session_state.rules, start=1):
    rule_id = rule['id']

    defaults = {
        f'importer_{rule_id}': rule.get('importer', []),
        f'exporter_{rule_id}': rule.get('exporter', []),
        f'sectors_{rule_id}': rule.get('sectors', []),
        f'free_trade_{rule_id}': rule.get('free_trade', False),
        f'tariff_{rule_id}': float(rule.get('tariff_change', 0.0) or 0.0),
    }
    for state_key, default_value in defaults.items():
        st.session_state.setdefault(state_key, default_value)

    with st.expander(f"Rule {idx}", expanded=True):
        info_col, remove_col = st.columns([5, 1])
        info_col.caption("Blank selections mean the rule applies to all countries or sectors in that dimension.")
        remove_rule = remove_col.button("Remove", key=f"remove_{rule_id}", use_container_width=True)

        col1, col2, col3 = st.columns(3)
        importer = col1.multiselect(
            "Importing countries",
            options=country_options,
            format_func=lambda code: country_labels.get(code, code),
            key=f'importer_{rule_id}',
        )
        exporter = col2.multiselect(
            "Exporting countries",
            options=country_options,
            format_func=lambda code: country_labels.get(code, code),
            key=f'exporter_{rule_id}',
        )
        sectors = col3.multiselect(
            "Sectors",
            options=sector_options,
            format_func=lambda code: sector_labels.get(code, code),
            key=f'sectors_{rule_id}',
        )

        lower_col, upper_col = st.columns([1, 2])
        free_trade = lower_col.checkbox(
            "Reset to free trade",
            key=f'free_trade_{rule_id}',
        )
        if free_trade:
            tariff_change = 0.0
            upper_col.info("This rule replaces the selected tariff wedge with the frictionless benchmark.")
        else:
            tariff_change = upper_col.slider(
                "Tariff change (%)",
                min_value=-100.0,
                max_value=100.0,
                step=1.0,
                key=f'tariff_{rule_id}',
            )

        if remove_rule:
            _cleanup_rule_state(rule_id)
            continue

        updated_rules.append({
            'id': rule_id,
            'importer': importer,
            'exporter': exporter,
            'sectors': sectors,
            'free_trade': free_trade,
            'tariff_change': tariff_change,
        })

st.session_state.rules = updated_rules

st.markdown("### Scenario summary")
if st.session_state.rules:
    summary_df = _summary_table(st.session_state.rules)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
else:
    st.markdown(
        """
        <div class="section-card">
            <h4>No custom policy rules yet</h4>
            <p>Running now will simply return the calibrated baseline equilibrium. Add a rule when you want a counterfactual shock.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

policy_payload = _build_policy_payload(st.session_state.rules)

st.markdown("### Run the model")
run_col, nav_col = st.columns(2)
log_container = st.empty()

if run_col.button("Run scenario", type="primary", use_container_width=True):
    original_stdout = sys.stdout
    try:
        sys.stdout = StreamlitLogger(log_container)
        with st.spinner("Solving the equilibrium..."):
            model_results = run(policy_payload)
        if model_results:
            st.session_state.results, st.session_state.d, st.session_state.p = model_results
            st.session_state.model_ran = True
            st.session_state.last_run_rule_count = len(st.session_state.rules)
            st.success("Scenario solved. The results page is ready.")
    except Exception as exc:
        st.error(f"Model run failed: {exc}")
    finally:
        sys.stdout = original_stdout

if nav_col.button(
    "Open results",
    use_container_width=True,
    disabled=st.session_state.results is None,
):
    st.switch_page("pages/Results.py")
