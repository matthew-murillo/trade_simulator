import os

import numpy as np
import pandas as pd
import streamlit as st


def inject_base_styles():
    st.markdown(
        """
        <style>
            :root {
                --canvas: #f5efe5;
                --panel: rgba(255, 252, 247, 0.88);
                --panel-strong: rgba(255, 249, 241, 0.96);
                --ink: #18242d;
                --muted: #5f6c73;
                --line: #d9cfc1;
                --accent: #bf5b2b;
                --accent-deep: #8e3f1d;
                --accent-soft: #f8e1d4;
                --good: #1f7a4d;
                --bad: #a33f32;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(191, 91, 43, 0.10), transparent 30%),
                    radial-gradient(circle at top right, rgba(24, 36, 45, 0.08), transparent 26%),
                    linear-gradient(180deg, #f8f3ea 0%, var(--canvas) 100%);
                color: var(--ink);
            }

            .block-container {
                padding-top: 1.1rem;
                padding-bottom: 3.5rem;
                padding-left: 2rem;
                padding-right: 2rem;
                max-width: 1320px;
            }

            .hero-card,
            .section-card {
                background: var(--panel);
                border: 1px solid rgba(217, 207, 193, 0.9);
                border-radius: 22px;
                box-shadow: 0 18px 50px rgba(24, 36, 45, 0.08);
                backdrop-filter: blur(12px);
            }

            .hero-card {
                padding: 1.5rem 1.6rem 1.35rem 1.6rem;
                margin-bottom: 1rem;
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
                font-size: 2.1rem;
                line-height: 1.08;
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
                padding: 1rem 1.1rem;
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
                border: 1px solid rgba(217, 207, 193, 0.85);
                border-radius: 18px;
                padding: 0.9rem 1rem;
                box-shadow: 0 12px 30px rgba(24, 36, 45, 0.05);
            }

            div[data-testid="stMetricLabel"] {
                color: var(--muted);
            }

            div[data-testid="stMetricValue"] {
                color: var(--ink);
            }

            .stButton > button {
                border-radius: 999px;
                border: 1px solid rgba(191, 91, 43, 0.35);
                background: linear-gradient(180deg, #fffaf4 0%, #f5e5d7 100%);
                color: var(--ink);
                font-weight: 600;
                padding: 0.55rem 1rem;
            }

            .stButton > button:hover {
                border-color: rgba(191, 91, 43, 0.55);
                color: var(--accent-deep);
            }

            .stDownloadButton > button {
                border-radius: 999px;
            }

            div[data-baseweb="select"] > div,
            div[data-baseweb="input"] > div,
            .stTextArea textarea {
                border-radius: 14px !important;
                border-color: rgba(217, 207, 193, 0.95) !important;
                background: rgba(255, 253, 249, 0.95) !important;
            }

            div[data-testid="stDataFrame"] {
                border: 1px solid rgba(217, 207, 193, 0.85);
                border-radius: 20px;
                overflow: hidden;
            }

            .summary-chip-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-top: 0.8rem;
            }

            .summary-chip {
                background: var(--accent-soft);
                border: 1px solid rgba(191, 91, 43, 0.18);
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
    p = np.load(path, allow_pickle=True).item()
    countries = pd.DataFrame({'code': p.get('c', []), 'name': p.get('c', [])})
    sectors = pd.DataFrame({'code': p.get('s', []), 'name': p.get('s', [])})
    return countries, sectors, 'output/p.npy'


def load_catalog(project_dir):
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

    return {
        'countries': countries,
        'sectors': sectors,
        'source': source,
    }
