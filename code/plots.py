import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


BASELINE_COLOR = "#2f5fe3"
COUNTERFACTUAL_COLOR = "#15a9d7"
POSITIVE_COLOR = "#0f9f7a"
NEGATIVE_COLOR = "#db5c7a"
NEUTRAL_COLOR = "#b8c7df"
TOTAL_COLOR = "#10233c"
GRID_COLOR = "rgba(16, 35, 60, 0.12)"
PAPER_BG = "rgba(255,255,255,0)"
PLOT_BG = "rgba(255,255,255,0.56)"


def _base_layout(title, xaxis_label, yaxis_label):
    return dict(
        title=dict(text=title, x=0.01, xanchor="left"),
        xaxis=dict(
            title=xaxis_label,
            tickangle=-28,
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            title=yaxis_label,
            showgrid=True,
            gridcolor=GRID_COLOR,
            zeroline=True,
            zerolinecolor=GRID_COLOR,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.0,
        ),
        margin=dict(l=30, r=20, t=65, b=30),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color="#10233c"),
        hoverlabel=dict(bgcolor="white"),
    )


def plot_baseline_vs_ctf(
    categories, baseline_values, ctf_values,
    var_name="Value", xaxis_label="Categories", yaxis_label="Value",
    baseline_label="Baseline", ctf_label="Counterfactual",
    baseline_color=BASELINE_COLOR, ctf_color=COUNTERFACTUAL_COLOR,
    title=None
):
    if title is None:
        title = f"{var_name}: Baseline vs Counterfactual"

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=categories,
        y=baseline_values,
        name=baseline_label,
        marker_color=baseline_color,
        marker_line_width=0,
        hovertemplate="%{x}<br>Baseline: %{y:,.3f}<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        x=categories,
        y=ctf_values,
        name=ctf_label,
        marker_color=ctf_color,
        marker_line_width=0,
        hovertemplate="%{x}<br>Counterfactual: %{y:,.3f}<extra></extra>",
    ))

    fig.update_layout(
        **_base_layout(title, xaxis_label, yaxis_label),
        barmode="group",
        bargap=0.18,
    )

    return fig


def plot_pct_change(
    categories, pct_change_values,
    var_name="Value", xaxis_label="Categories", yaxis_label="Value",
    pct_change_label="Percent change",
    title=None
):
    if title is None:
        title = f"{var_name}: Percent Change from Baseline"

    values = np.asarray(pct_change_values, dtype=float)
    colors = np.where(
        values > 0,
        POSITIVE_COLOR,
        np.where(values < 0, NEGATIVE_COLOR, NEUTRAL_COLOR),
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        name=pct_change_label,
        marker_color=colors,
        marker_line_width=0,
        hovertemplate="%{x}<br>%{y:+.3f}%<extra></extra>",
    ))

    fig.update_layout(
        **_base_layout(title, xaxis_label, yaxis_label),
        showlegend=False,
    )

    return fig


def plot_decomposition(
    categories, delta_a, delta_b, delta_total,
    var_name="Variable", component_a_name="Factor A", component_b_name="Factor B",
    xaxis_label="Categories", yaxis_label="% Change",
    a_color=BASELINE_COLOR, b_color=COUNTERFACTUAL_COLOR, total_color=TOTAL_COLOR,
    title=None
):
    if title is None:
        title = f"Drivers of {var_name}"

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=categories,
        y=delta_a,
        name=component_a_name,
        marker_color=a_color,
        hovertemplate="%{x}<br>" + component_a_name + ": %{y:+.3f}%<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        x=categories,
        y=delta_b,
        name=component_b_name,
        marker_color=b_color,
        hovertemplate="%{x}<br>" + component_b_name + ": %{y:+.3f}%<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=categories,
        y=delta_total,
        name="Total",
        mode="lines+markers",
        line=dict(color=total_color, width=2.5),
        marker=dict(color=total_color, size=7),
        hovertemplate="%{x}<br>Total: %{y:+.3f}%<extra></extra>",
    ))

    fig.update_layout(
        **_base_layout(title, xaxis_label, yaxis_label),
        barmode="relative",
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
    import pycountry

    frame = df.copy()

    if title is None and sector is not None:
        title = f"{flow} partner shifts for {country}, {sector}"
    elif title is None:
        title = f"{flow} partner shifts for {country}"

    iso_to_name = {item.alpha_3: item.name for item in pycountry.countries}
    frame["country_name"] = frame["country"].map(iso_to_name).fillna(frame["country"])

    if "ROW" in frame["country"].values:
        row_rows = frame[frame["country"] == "ROW"]
        if not row_rows.empty:
            row_value = row_rows.iloc[0]
            all_iso3 = {item.alpha_3 for item in pycountry.countries}
            existing_iso3 = set(frame["country"])
            missing_iso3 = sorted(all_iso3 - existing_iso3)
            row_copies = pd.DataFrame([
                {
                    "country": iso3,
                    "sector": row_value["sector"],
                    "trade_flow": row_value["trade_flow"],
                    "country_name": "Rest of World",
                }
                for iso3 in missing_iso3
            ])
            frame = pd.concat([frame[frame["country"] != "ROW"], row_copies], ignore_index=True)

    vmax = max(abs(frame["trade_flow"].max()), abs(frame["trade_flow"].min()))
    if color_range is None:
        color_range = [-vmax, vmax] if vmax > 0 else [-1, 1]

    fig = px.choropleth(
        frame,
        locations="country",
        color="trade_flow",
        hover_name="country_name",
        color_continuous_scale=[
            [0.0, "#db5c7a"],
            [0.5, "#f7fbff"],
            [1.0, "#0f9f7a"],
        ],
        range_color=color_range,
        color_continuous_midpoint=0,
        title=title,
        labels={"trade_flow": flow_label},
    )

    fig.update_geos(
        showcountries=True,
        countrycolor="white",
        showcoastlines=False,
        showland=True,
        landcolor="#edf5ff",
        showframe=False,
        showlakes=False,
    )

    fig.update_layout(
        height=450,
        margin=dict(l=10, r=10, t=50, b=20),
        coloraxis_colorbar=dict(
            title=flow_label,
            orientation='h',
            yanchor='bottom',
            y=-0.12,
            x=0.5,
            xanchor='center',
            len=0.62,
            thickness=12,
            tickformat=".2f",
        ),
        font=dict(color="#10233c"),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
    )

    return fig
