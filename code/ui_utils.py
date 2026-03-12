import os
from functools import lru_cache

import numpy as np
import pandas as pd
import streamlit as st


def inject_base_styles():
    st.markdown(
        """
        <style>
            :root {
                --canvas: #eef4ff;
                --panel: rgba(255, 255, 255, 0.74);
                --panel-strong: rgba(255, 255, 255, 0.9);
                --ink: #10233c;
                --muted: #5b6f88;
                --line: rgba(133, 154, 191, 0.28);
                --accent: #326bff;
                --accent-deep: #1742a0;
                --accent-soft: rgba(50, 107, 255, 0.12);
                --good: #0f9f7a;
                --bad: #db5c7a;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(50, 107, 255, 0.16), transparent 28%),
                    radial-gradient(circle at top right, rgba(0, 196, 204, 0.13), transparent 24%),
                    linear-gradient(180deg, #f6faff 0%, var(--canvas) 52%, #edf3fb 100%);
                color: var(--ink);
                font-family: "Avenir Next", "Segoe UI", "Helvetica Neue", sans-serif;
            }

            .block-container {
                padding-top: 3.15rem;
                padding-bottom: 3.5rem;
                padding-left: 2rem;
                padding-right: 2rem;
                max-width: 1320px;
            }

            div[data-testid="stAppViewBlockContainer"] > div:first-child {
                padding-top: 3.15rem;
            }

            .hero-card,
            .section-card {
                background: var(--panel);
                border: 1px solid var(--line);
                border-radius: 24px;
                box-shadow: 0 24px 60px rgba(20, 42, 77, 0.12);
                backdrop-filter: blur(18px);
            }

            .hero-card {
                padding: 1.8rem 1.8rem 1.6rem 1.8rem;
                margin-bottom: 1.1rem;
                background:
                    linear-gradient(135deg, rgba(255, 255, 255, 0.88), rgba(245, 250, 255, 0.72)),
                    radial-gradient(circle at top right, rgba(50, 107, 255, 0.14), transparent 34%);
            }

            .hero-kicker {
                color: var(--accent-deep);
                font-size: 0.82rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.35rem;
            }

            .hero-card h1 {
                font-size: 2.25rem;
                line-height: 1.04;
                margin: 0;
                color: var(--ink);
            }

            .hero-card p {
                color: var(--muted);
                font-size: 1rem;
                margin: 0.7rem 0 0;
                max-width: 68rem;
            }

            .section-card {
                padding: 1rem 1.15rem;
                margin: 0.85rem 0 1rem;
            }

            .section-card h3,
            .section-card h4 {
                margin: 0;
                color: var(--ink);
            }

            .section-card p {
                color: var(--muted);
                margin: 0.4rem 0 0;
            }

            div[data-testid="stMetric"] {
                background: var(--panel-strong);
                border: 1px solid var(--line);
                border-radius: 20px;
                padding: 0.9rem 1rem;
                box-shadow: 0 16px 34px rgba(20, 42, 77, 0.07);
            }

            div[data-testid="stMetricLabel"] {
                color: var(--muted);
            }

            div[data-testid="stMetricValue"] {
                color: var(--ink);
            }

            .stButton > button {
                border-radius: 999px;
                border: 1px solid rgba(50, 107, 255, 0.22);
                background: linear-gradient(180deg, #ffffff 0%, #eef4ff 100%);
                color: var(--ink);
                font-weight: 600;
                padding: 0.55rem 1rem;
                box-shadow: 0 10px 22px rgba(50, 107, 255, 0.08);
            }

            .stButton > button:hover {
                border-color: rgba(50, 107, 255, 0.48);
                color: var(--accent-deep);
            }

            .stButton > button[kind="primary"] {
                background: linear-gradient(135deg, #3168ff 0%, #15a9d7 100%);
                color: white;
            }

            .stDownloadButton > button {
                border-radius: 999px;
            }

            div[data-baseweb="select"] > div,
            div[data-baseweb="input"] > div,
            .stTextArea textarea,
            div[data-baseweb="base-input"] > div {
                border-radius: 14px !important;
                border-color: rgba(133, 154, 191, 0.28) !important;
                background: rgba(255, 255, 255, 0.9) !important;
            }

            div[data-testid="stDataFrame"] {
                border: 1px solid var(--line);
                border-radius: 20px;
                overflow: hidden;
            }

            div[data-baseweb="tab-list"] {
                gap: 0.4rem;
            }

            button[data-baseweb="tab"] {
                border-radius: 999px;
                border: 1px solid transparent;
                background: rgba(255, 255, 255, 0.52);
                color: var(--muted);
                padding: 0.45rem 0.95rem;
            }

            button[data-baseweb="tab"][aria-selected="true"] {
                background: linear-gradient(135deg, rgba(49, 104, 255, 0.14), rgba(21, 169, 215, 0.14));
                border-color: rgba(50, 107, 255, 0.2);
                color: var(--accent-deep);
            }

            div[data-testid="stAlert"] {
                border-radius: 18px;
                border: 1px solid var(--line);
                background: rgba(255, 255, 255, 0.82);
            }

            .summary-chip-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-top: 0.8rem;
            }

            .summary-chip {
                background: var(--accent-soft);
                border: 1px solid rgba(50, 107, 255, 0.14);
                border-radius: 999px;
                color: var(--accent-deep);
                font-size: 0.9rem;
                font-weight: 600;
                padding: 0.4rem 0.75rem;
            }

            .muted-copy {
                color: var(--muted);
                font-size: 0.95rem;
            }

            .equation-card {
                background: rgba(255, 255, 255, 0.7);
                border: 1px solid var(--line);
                border-radius: 22px;
                padding: 1rem 1.15rem 0.35rem 1.15rem;
                margin: 0.7rem 0;
                box-shadow: 0 18px 36px rgba(20, 42, 77, 0.08);
            }

            .equation-card p {
                color: var(--muted);
                margin: 0 0 0.4rem 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title, subtitle, kicker=None):
    kicker_html = f"<div class='hero-kicker'>{kicker}</div>" if kicker else ""
    st.markdown(
        f"""
        <div class="hero-card">
            {kicker_html}
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_card(title, body):
    st.markdown(
        f"""
        <div class="section-card">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_divide(numerator, denominator, fill_value=1.0):
    numerator, denominator = np.broadcast_arrays(
        np.asarray(numerator, dtype=float),
        np.asarray(denominator, dtype=float),
    )
    result = np.full(numerator.shape, fill_value, dtype=float)
    np.divide(
        numerator,
        denominator,
        out=result,
        where=np.abs(denominator) > 1e-12,
    )
    return result


def pct_change(counterfactual, baseline, fill_value=1.0):
    ratio = safe_divide(counterfactual, baseline, fill_value=fill_value)
    return np.nan_to_num((ratio - 1.0) * 100.0, nan=0.0, posinf=0.0, neginf=0.0)


def format_selection(values):
    return ", ".join(values) if values else "All"


def make_label(code, name):
    if not name or code == name:
        return str(code)
    return f"{code} - {name}"


def _load_dictionary(path):
    dictionary = pd.read_csv(path)

    country_name_col = 'c_name' if 'c_name' in dictionary.columns else 'country'
    sector_name_col = 's_name' if 's_name' in dictionary.columns else 'sector'

    countries = (
        dictionary[['country', country_name_col]]
        .dropna(subset=['country'])
        .drop_duplicates(subset=['country'])
        .rename(columns={'country': 'code', country_name_col: 'name'})
    )
    sectors = (
        dictionary[['sector', sector_name_col]]
        .dropna(subset=['sector'])
        .drop_duplicates(subset=['sector'])
        .rename(columns={'sector': 'code', sector_name_col: 'name'})
    )

    return countries.reset_index(drop=True), sectors.reset_index(drop=True), 'dictionary.csv'


def _load_from_calibration(path):
    project_dir = os.path.dirname(os.path.dirname(path))
    p = np.load(path, allow_pickle=True).item()
    sector_names = list(p.get('s', []))
    sector_codes = _load_sector_codes_from_data(project_dir, len(sector_names))

    if len(sector_codes) != len(sector_names):
        sector_codes = sector_names

    countries = pd.DataFrame({'code': p.get('c', []), 'name': p.get('c', [])})
    sectors = pd.DataFrame({'code': sector_codes, 'name': sector_names})
    return countries, sectors, 'output/p.npy'


def _load_sector_codes_from_data(project_dir, expected_count):
    data_path = os.path.join(project_dir, 'data', '2020_SML.csv')
    if not os.path.exists(data_path):
        return []

    columns = pd.read_csv(data_path, nrows=0).columns.tolist()[1:]
    if not columns:
        return []

    first_country = columns[0].split('_', 1)[0]
    sector_codes = []

    for column in columns:
        if '_' not in column:
            continue
        country_code, sector_code = column.split('_', 1)
        if country_code != first_country:
            break
        sector_codes.append(sector_code)

    if len(sector_codes) != expected_count:
        return []

    return sector_codes


@lru_cache(maxsize=None)
def _load_catalog_cached(project_dir):
    dictionary_path = os.path.join(project_dir, 'data', 'dictionary.csv')
    calibration_path = os.path.join(project_dir, 'output', 'p.npy')

    if os.path.exists(dictionary_path):
        countries, sectors, source = _load_dictionary(dictionary_path)
    elif os.path.exists(calibration_path):
        countries, sectors, source = _load_from_calibration(calibration_path)
    else:
        countries = pd.DataFrame(columns=['code', 'name'])
        sectors = pd.DataFrame(columns=['code', 'name'])
        source = 'none'

    countries['label'] = [
        make_label(code, name)
        for code, name in zip(countries['code'], countries['name'])
    ]
    sectors['label'] = [
        make_label(code, name)
        for code, name in zip(sectors['code'], sectors['name'])
    ]

    return countries, sectors, source


def load_catalog(project_dir):
    countries, sectors, source = _load_catalog_cached(project_dir)

    return {
        'countries': countries.copy(),
        'sectors': sectors.copy(),
        'source': source,
    }
