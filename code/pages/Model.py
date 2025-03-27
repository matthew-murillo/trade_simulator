import uuid
import streamlit as st
import numpy as np
import json
import os
import sys
import time
import io

if os.path.abspath('..') not in sys.path:
    sys.path.append(os.path.abspath('..'))
from QGE.main import run
import pandas as pd
import matplotlib.pyplot as plt

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 4rem;  /* ✅ Increased bottom padding */
            padding-left: 2rem;
            padding-right: 2rem;
        }
        
        .stText {
            padding-bottom: 2rem; /* ✅ Extra spacing below log output */
        }
    </style>
""", unsafe_allow_html=True)

PROJECT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUTPUT = os.path.join(PROJECT, 'output')
DATA = os.path.join(PROJECT, 'data')

dictionary = pd.read_csv(os.path.join(DATA, 'dictionary.csv'))
c = dictionary['country'].dropna()
s = dictionary['sector'].dropna()

st.title("The Model")

if "results" not in st.session_state:
    st.session_state.results = None
if "d" not in st.session_state:
    st.session_state.d = None
if "p" not in st.session_state:
    st.session_state.p = None

# Initialize session state variables
if "rules" not in st.session_state:
    st.session_state.rules = []

if "update_counts" not in st.session_state:
    st.session_state.update_counts = {}

if "summary_visible" not in st.session_state:
    st.session_state.summary_visible = False  # Track whether to show summary

# Add rule button
if st.button("➕ Add Tariff"):
    new_rule_id = str(uuid.uuid4())
    st.session_state.rules.append({
        "id": new_rule_id,
        "importer": [],
        "exporter": [],
        "sectors": [],
        "free_trade": False,
        "tariff_change": 0.0
    })
    st.session_state.update_counts[new_rule_id] = 0  # Initialize update count

# Processing rules
rules_to_keep = []
update_happened = False

for i, rule in enumerate(st.session_state.rules):
    rule_id = rule["id"]

    # Ensure session state variables exist
    for key in ["importer", "exporter", "sectors"]:
        state_key = f"{key}_{rule_id}"
        if state_key not in st.session_state:
            # Set once, avoid overwriting
            st.session_state[state_key] = rule[key]

    with st.form(f"form_{rule_id}"):
        st.markdown(f"#### Tariff {i + 1}")

        c1, c2, c3 = st.columns(3)

        importer = c1.multiselect(
            f"Importer {i}", c, key=f"importer_{rule_id}")

        exporter = c2.multiselect(
            f"Exporter {i}", c, key=f"exporter_{rule_id}")

        sectors = c3.multiselect(
            f"Sectors {i}", s, key=f"sectors_{rule_id}")

        free_trade = st.checkbox("Free Trade", value=rule.get(
            "free_trade", False), key=f"free_trade_{rule_id}")

        tariff_change = None if free_trade else st.slider(
            "Tariff Change (%)", -100.0, 100.0, rule.get("tariff_change", 0), step=1.0, key=f"tariff_{rule_id}")

        delete = st.checkbox("🗑️ Delete this rule", key=f"delete_{rule_id}")

        submitted = st.form_submit_button("Update Rule")

        if submitted:
            if rule_id not in st.session_state.update_counts:
                st.session_state.update_counts[rule_id] = 0

            if not delete:
                rules_to_keep.append({
                    "id": rule_id,
                    "importer": st.session_state[f"importer_{rule_id}"],
                    "exporter": st.session_state[f"exporter_{rule_id}"],
                    "sectors": st.session_state[f"sectors_{rule_id}"],
                    "free_trade": free_trade,
                    "tariff_change": tariff_change
                })
            else:
                st.session_state.pop(f"importer_{rule_id}", None)
                st.session_state.pop(f"exporter_{rule_id}", None)
                st.session_state.pop(f"sectors_{rule_id}", None)
        else:
            rules_to_keep.append(rule)

# ✅ Update session state only once after processing all rules
st.session_state.rules = rules_to_keep
st.session_state.summary_visible = True  # Ensure summary remains visible
# ✅ Success message with automatic disappearance
if update_happened:
    success_placeholder = st.empty()
    success_placeholder.success("Rule updated successfully!")
    time.sleep(1)
    success_placeholder.empty()

# ✅ Summary of Trade Policy (updates only on double-click and persists)
if not st.session_state.rules:
    st.info("No tariffs have been applied.")
elif st.session_state.summary_visible:
    st.markdown("### Summary of Counterfactual Tariffs")
    for i, rule in enumerate(st.session_state.rules):
        st.markdown(f"**Tariff {i + 1}:**")
        st.write(
            f"- **Importer(s):** {', '.join(rule['importer']) if rule['importer'] else 'All'}")
        st.write(
            f"- **Exporter(s):** {', '.join(rule['exporter']) if rule['exporter'] else 'All'}")
        st.write(
            f"- **Sectors:** {', '.join(rule['sectors']) if rule['sectors'] else 'All'}")
        if rule["free_trade"]:
            st.write("- **Policy:** Free Trade (No Tariffs)")
        else:
            st.write(f"- **Tariff Change:** {rule['tariff_change']}%")

index_policy_dict = {}

# Process rules into dictionary for model execution
for rule in st.session_state.rules:
    importer_indices = c[c.isin(rule["importer"])].index.tolist()
    exporter_indices = c[c.isin(rule["exporter"])].index.tolist()
    sector_indices = s[s.isin(rule["sectors"])].index.tolist()

    rule_entry = {
        "importer_indices": importer_indices,
        "exporter_indices": exporter_indices,
        "sector_indices": sector_indices,
        "free_trade": rule["free_trade"],
        "tariff_change": rule["tariff_change"]
    }

    if rule["id"] in index_policy_dict:
        index_policy_dict[rule["id"]].append(rule_entry)
    else:
        index_policy_dict[rule["id"]] = [rule_entry]

st.markdown("---")

c4, c5 = st.columns(2)

with c4:
    if st.button("Run Model"):
        class StreamlitLogger(io.StringIO):
            """ Custom StringIO class to continuously overwrite the same line in Streamlit. """

            def __init__(self, container):
                super().__init__()
                self.container = container

            def write(self, message):
                """ Override write method to replace the log text instead of appending. """
                if message.strip():  # Ignore empty lines
                    # Replace text instead of appending
                    self.container.text(message.strip())

            def flush(self):
                pass  # No need to flush since updates happen live

        log_container = st.empty()  # ✅ This will hold a single dynamic output line

        # Redirect stdout for dynamic logs
        sys.stdout = StreamlitLogger(log_container)

        # ✅ Run model and store results in session state
        model_results = run(index_policy_dict)

        if model_results:
            st.session_state.results, st.session_state.d, st.session_state.p = model_results
            st.session_state.model_ran = True  # Mark model as run
            st.success("Model run complete.")

        sys.stdout = sys.__stdout__

with c5:
    # Navigation button to Results page
    if st.button("Go to Results"):
        st.switch_page("pages/Results.py")
