import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def plot_baseline_vs_ctf(
    categories, baseline_values, ctf_values,
    var_name="Value", xaxis_label="Categories", yaxis_label="Value",
    baseline_label="Baseline", ctf_label="Counterfactual",
    baseline_color="blue", ctf_color="red",
    title=None
):
    """
    Generates a Plotly bar plot comparing baseline and counterfactual (CTF) values.

    Parameters:
    - categories: List of category labels (e.g., countries, sectors, regions).
    - baseline_values: List/array of baseline values corresponding to categories.
    - ctf_values: List/array of counterfactual values corresponding to categories.
    - var_name: Name of the variable being compared (e.g., "Gross Output").
    - xaxis_label: Label for the x-axis.
    - yaxis_label: Label for the y-axis.
    - baseline_label: Legend label for the baseline data.
    - ctf_label: Legend label for the counterfactual data.
    - baseline_color: Color for the baseline bars.
    - ctf_color: Color for the counterfactual bars.
    - title: Custom plot title (if None, defaults to "var_name: Baseline vs Counterfactual").

    Returns:
    - A Plotly Figure object.
    """

    if title is None:
        title = f"{var_name}: Baseline vs Counterfactual"

    fig = go.Figure()

    # Baseline Values
    fig.add_trace(go.Bar(
        x=categories,
        y=baseline_values,
        name=baseline_label,
        marker_color=baseline_color,
        opacity=0.7
    ))

    # Counterfactual Values
    fig.add_trace(go.Bar(
        x=categories,
        y=ctf_values,
        name=ctf_label,
        marker_color=ctf_color,
        opacity=0.7
    ))

    # Formatting
    fig.update_layout(
        title=title,
        xaxis=dict(
            title=xaxis_label,
            tickangle=45  # Rotate x-axis labels for better readability
        ),
        yaxis_title=yaxis_label,
        barmode='group',  # Side-by-side bars
        template="plotly_white"
    )

    return fig


def plot_pct_change(
    categories, pct_change_values,
    var_name="Value", xaxis_label="Categories", yaxis_label="Value",
    pct_change_label="Counterfactual",
    title=None
):
    """
    Generates a Plotly bar plot comparing baseline and counterfactual (CTF) values.

    Parameters:
    - categories: List of category labels (e.g., countries, sectors, regions).
    - baseline_values: List/array of baseline values corresponding to categories.
    - pct_change_values: List/array of percent change values from baseline.
    - var_name: Name of the variable being compared (e.g., "Gross Output").
    - xaxis_label: Label for the x-axis.
    - yaxis_label: Label for the y-axis.
    - pct_change_label: Legend label for the percent change data.
    - title: Custom plot title (if None, defaults to "var_name: Baseline vs Counterfactual").

    Returns:
    - A Plotly Figure object.
    """

    if title is None:
        title = f"{var_name}: Percent Change from Baseline"

    fig = go.Figure()

    # Percent Change Values
    fig.add_trace(go.Bar(
        x=categories,
        y=pct_change_values,
        name=pct_change_label,
        opacity=0.7
    ))

    # Formatting
    fig.update_layout(
        title=title,
        xaxis=dict(
            title=xaxis_label,
            tickangle=45  # Rotate x-axis labels for better readability
        ),
        yaxis_title=yaxis_label,
        barmode='group',  # Side-by-side bars
        template="plotly_white"
    )

    return fig


def plot_decomposition(
    categories, delta_a, delta_b, delta_total,
    var_name="Variable", component_a_name="Factor A", component_b_name="Factor B",
    xaxis_label="Categories", yaxis_label="% Change",
    a_color="blue", b_color="red", total_color="purple",
    title=None
):
    """
    Generates a decomposition bar chart showing how changes in two components (a and b) contribute to the total absolute change,
    with an overlaid translucent bar representing total absolute change.

    Parameters:
    - categories: List of category labels (e.g., countries, sectors).
    - delta_a: Change due to component A.
    - delta_b: Change due to component B.
    - delta_total: Total change.
    - var_name: Name of the variable being decomposed.
    - component_a_name: Label for component A.
    - component_b_name: Label for component B.
    - xaxis_label: Label for the x-axis.
    - yaxis_label: Label for the y-axis.
    - a_color: Color for component A.
    - b_color: Color for component B.
    - total_color: Color for total absolute change overlay.
    - title: Custom plot title (if None, defaults to "Decomposition of var_name").

    Returns:
    - A Plotly Figure object.
    """

    if title is None:
        title = f"Decomposition of {var_name}"

    fig = go.Figure()

    # Component A Contribution
    fig.add_trace(go.Bar(
        x=categories,
        y=delta_a,
        name=f"Change due to {component_a_name}",
        marker_color=a_color,
        opacity=0.7
    ))

    # Component B Contribution
    fig.add_trace(go.Bar(
        x=categories,
        y=delta_b,
        name=f"Change due to {component_b_name}",
        marker_color=b_color,
        opacity=0.7
    ))

    # Total Absolute Change (Translucent Bar)
    fig.add_trace(go.Bar(
        x=categories,
        y=delta_total,
        name="Total Change",
        marker_color=total_color,
        opacity=0.3  # ✅ Make it translucent for overlay
    ))

    # Formatting
    fig.update_layout(
        title=title,
        xaxis=dict(
            title=xaxis_label,
            tickangle=45  # Rotate x-axis labels for better readability
        ),
        yaxis_title=yaxis_label,
        barmode="overlay",  # ✅ Allows the translucent bar to overlay the decomposition bars
        template="plotly_white"
    )

    return fig


def plot_trade_map(
    df,
    country=None,
    sector=None,
    flow=None,
    flow_label="Net Trade Flow (% Change)",
    title=None,
    color_range=None
):
    """
    Plots a sleek, modern choropleth map with bipolar color scale for trade flows.

    Parameters:
    - df: DataFrame with ['country' (ISO alpha-3), 'sector', 'trade_flow']
    - sector: Optional string to filter by sector
    - flow_label: Label for the colorbar
    - title: Plot title

    Returns:
    - Plotly Figure object
    """
    import pycountry
    import pandas as pd
    import plotly.express as px

    if title is None and sector is not None:
        title = f"{flow} by Country for {country}, Sector {sector}: Percent Change from Baseline"
    elif title is None:
        title = f"{flow} by Country for {country}: Percent Change from Baseline"

    # Add country names
    iso_to_name = {c.alpha_3: c.name for c in pycountry.countries}
    df["country_name"] = df["country"].map(
        iso_to_name).fillna(df.get("country_name", "Unknown"))

    # Fill missing countries with ROW value
    all_iso3 = {c.alpha_3 for c in pycountry.countries}
    existing_iso3 = set(df["country"])
    missing_iso3 = all_iso3 - existing_iso3

    row_value = df[df["country"] == "ROW"].iloc[0]
    row_copies = pd.DataFrame([
        {
            "country": iso3,
            "sector": row_value["sector"],
            "trade_flow": row_value["trade_flow"],
            "country_name": "Rest of World"
        }
        for iso3 in missing_iso3
    ])
    df = pd.concat([df, row_copies], ignore_index=True)

    # Symmetric color scale
    vmax = max(abs(df["trade_flow"].max()), abs(df["trade_flow"].min()))

    fig = px.choropleth(
        df,
        locations="country",
        color="trade_flow",
        hover_name="country_name",
        color_continuous_scale="RdBu",
        range_color=[-vmax, vmax],
        color_continuous_midpoint=0,
        title=title,
        labels={"trade_flow": flow_label}
    )

    fig.update_geos(
        showcountries=True,
        countrycolor="white",
        showcoastlines=False,
        showland=True,
        landcolor="whitesmoke",
        showframe=False,
        showlakes=False
    )

    fig.update_layout(
        height=450,
        margin=dict(l=0, r=0, t=30, b=0),
        coloraxis_colorbar=dict(
            title=flow_label,
            orientation='h',
            yanchor='bottom',
            y=-0.1,
            x=0.5,
            xanchor='center',
            len=0.6,
            thickness=12,
            tickformat=".2f",
            ticks="outside",
            ticklen=5,
            tickfont=dict(size=10)
        ),
        font=dict(size=12),
        title_x=0.5,
        title_font=dict(size=16),
        template="plotly_white"
    )
    fig.update_layout(
        title=dict(text=title, x=0, xanchor="left"),  # 👈 Left-aligned title
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig
