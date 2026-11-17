"""
PULSE dashboard — Most Reliable T20 Players Under Pressure
SupeRR Selector Season 2, Round 1 (Rajasthan Royals x Unstop)

Run locally:   streamlit run app.py
Deploy:        Render web service (see render.yaml / README.md)
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------- setup
st.set_page_config(
    page_title="PULSE | Most Reliable Players Under Pressure",
    page_icon="🏏",
    layout="wide",
)

PINK, BLUE, GOLD, GRAY, NAVY = "#EA1A85", "#254AA5", "#CBA92B", "#A9A6B0", "#1B2F6E"
DATA = Path(__file__).parent / "data"


@st.cache_data
def load(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / f"{name}.csv")


bat = load("batters")
bowl = load("bowlers")
calib = load("calibration")
summary = load("summary").set_index("metric")["value"]
phase = load("phase")

bat10 = bat[bat["rank"] <= 10].sort_values("rank")
bowl10 = bowl[bowl["rank"] <= 10].sort_values("rank")


def S(key: str) -> float:
    return float(summary[key])


# ---------------------------------------------------------------- styles
st.markdown(
    f"""
<style>
.block-container {{padding-top: 1.6rem; max-width: 1200px;}}
.pl-hero {{background: linear-gradient(120deg, {PINK} 0%, #b8146a 45%, {BLUE} 100%);
  color: #fff; border-radius: 14px; padding: 22px 28px; border-bottom: 4px solid {GOLD}; margin-bottom: 18px;}}
.pl-kicker {{font-size: 12px; letter-spacing: .14em; text-transform: uppercase; opacity: .9; margin: 0 0 4px;}}
.pl-title {{font-family: Georgia, serif; font-weight: 400; font-size: clamp(24px, 4vw, 36px); line-height: 1.15; margin: 0; color: #fff;}}
.pl-sub {{margin: 6px 0 0; opacity: .92; font-size: 14px;}}
.pl-take {{font-size: 19px; line-height: 1.5; margin: 6px 0 18px;}}
.pl-take b {{color: {PINK};}}
.pl-kpis {{display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 10px;}}
.pl-card {{background: rgba(127,127,127,.06); border: 1px solid rgba(127,127,127,.22); border-radius: 12px;
  padding: 14px 16px; border-top: 3px solid {PINK};}}
.pl-card:nth-child(even) {{border-top-color: {BLUE};}}
.pl-kv {{font-family: Georgia, serif; font-size: 28px; line-height: 1.1;}}
.pl-kl {{font-size: 12px; opacity: .75; margin-top: 4px;}}
.pl-note {{opacity: .75; font-size: 14px; margin: -4px 0 10px;}}
.stTabs [data-baseweb="tab"] {{font-weight: 600; font-size: 15px;}}
.stTabs [aria-selected="true"] {{color: {PINK} !important;}}
.stTabs [data-baseweb="tab-highlight"] {{background-color: {PINK} !important;}}
.pl-foot {{text-align: center; font-size: 12px; opacity: .65; margin-top: 30px;}}
</style>
""",
    unsafe_allow_html=True,
)


def kpi_row(items):
    cards = "".join(
        f'<div class="pl-card"><div class="pl-kv">{v}</div><div class="pl-kl">{label}</div></div>' for v, label in items
    )
    st.markdown(f'<div class="pl-kpis">{cards}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- charts
BASE_LAYOUT = dict(
    margin=dict(l=10, r=30, t=10, b=30),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(size=13),
    hoverlabel=dict(bgcolor="white", font_size=12),
    showlegend=False,
)


def score_bars(df: pd.DataFrame, color: str, kind: str) -> go.Figure:
    colors = [GOLD] + [color] * (len(df) - 1)
    if kind == "bat":
        hover = [
            f"<b>{r.name}</b><br>Rank {r.rank} · PULSE {r.pulse_score:.2f}"
            f"<br>{r.pressure_balls} pressure balls in {r.pressure_innings} innings"
            f"<br>SR {r.sr_pressure:.1f} under pressure vs {r.sr_normal:.1f} normally"
            f"<br>Consistency {r.consistency_pct}% · top 10 in {r.top10_pct}% of resamples"
            for r in df.itertuples()
        ]
    else:
        hover = [
            f"<b>{r.name}</b><br>Rank {r.rank} · PULSE {r.pulse_score:.2f}"
            f"<br>{r.pressure_balls} pressure balls in {r.pressure_innings} spells"
            f"<br>Economy {r.econ_pressure:.2f} under pressure vs {r.econ_normal:.2f} normally"
            f"<br>{r.wkts_pressure} pressure wickets · top 10 in {r.top10_pct}% of resamples"
            for r in df.itertuples()
        ]
    fig = go.Figure(
        go.Bar(
            x=df["pulse_score"], y=df["name"], orientation="h", marker_color=colors,
            text=[f"{v:.2f}" for v in df["pulse_score"]], textposition="outside", cliponaxis=False,
            hovertext=hover, hoverinfo="text",
        )
    )
    fig.update_layout(**BASE_LAYOUT, height=420)
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[0, df["pulse_score"].max() * 1.15], gridcolor="rgba(127,127,127,.15)", title="PULSE score")
    return fig


def dumbbell(df: pd.DataFrame, normal: str, pressure: str, axis_title: str, fmt: str) -> go.Figure:
    xs, ys = [], []
    for r in df.itertuples():
        xs += [getattr(r, normal), getattr(r, pressure), None]
        ys += [r.name, r.name, None]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color="rgba(127,127,127,.35)", width=4), hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=df[normal], y=df["name"], mode="markers", name="Normal situations",
        marker=dict(color=GRAY, size=11, line=dict(color="white", width=2)),
        hovertemplate="<b>%{y}</b><br>Normal: %{x:" + fmt + "}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df[pressure], y=df["name"], mode="markers", name="Under pressure",
        marker=dict(color=PINK, size=13, line=dict(color="white", width=2)),
        hovertemplate="<b>%{y}</b><br>Under pressure: %{x:" + fmt + "}<extra></extra>",
    ))
    layout = dict(BASE_LAYOUT)
    layout["showlegend"] = True
    fig.update_layout(**layout, height=420,
                      legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0))
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(gridcolor="rgba(127,127,127,.15)", title=axis_title)
    return fig


def calibration_chart() -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Perfect calibration",
                             line=dict(color=GRAY, dash="dash"), hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=calib["pred"], y=calib["actual"], mode="lines+markers", name="PULSE win probability",
        line=dict(color=PINK, width=3), marker=dict(size=9, color=PINK, line=dict(color="white", width=2)),
        customdata=calib["n"],
        hovertemplate="Predicted %{x:.1%}<br>Actually won %{y:.1%}<br>%{customdata:,} balls<extra></extra>",
    ))
    layout = dict(BASE_LAYOUT)
    layout["showlegend"] = True
    fig.update_layout(**layout, height=380, legend=dict(orientation="h", y=-0.2, x=0))
    fig.update_xaxes(range=[0, 1], tickformat=".0%", title="Predicted win probability", gridcolor="rgba(127,127,127,.15)")
    fig.update_yaxes(range=[0, 1], tickformat=".0%", title="Actual win rate", gridcolor="rgba(127,127,127,.15)")
    return fig


def phase_chart() -> go.Figure:
    fig = go.Figure(go.Bar(
        x=phase["share_pct"], y=phase["phase"], orientation="h", marker_color=PINK,
        text=[f"{v:.1f}%" for v in phase["share_pct"]], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x:.1f}% of all pressure balls<extra></extra>",
    ))
    fig.update_layout(**BASE_LAYOUT, height=300)
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[0, phase["share_pct"].max() * 1.2], title="% of all pressure balls",
                     gridcolor="rgba(127,127,127,.15)")
    return fig


def ranking_table(df: pd.DataFrame, cols: dict, key: str):
    choice = st.selectbox("Show", ["Top 10", "Top 25", "All eligible"], key=key)
    n = {"Top 10": 10, "Top 25": 25}.get(choice, len(df))
    st.dataframe(df.head(n)[list(cols)].rename(columns=cols), hide_index=True, use_container_width=True)


# ---------------------------------------------------------------- page
st.markdown(
    """
<div class="pl-hero">
  <p class="pl-kicker">Halla Bol · SupeRR Selector Season 2 · Round 1</p>
  <h1 class="pl-title">PULSE: the most reliable T20 players under pressure</h1>
  <p class="pl-sub">Pressure-Under-Leverage Statistical Evaluation · IPL 2022–26 and T20 Internationals · Mohammed Haaris</p>
</div>
""",
    unsafe_allow_html=True,
)

tb, tw = bat10.iloc[0], bowl10.iloc[0]
st.markdown(
    f'<p class="pl-take"><b>{tb["name"]}</b> is the most reliable batter under pressure '
    f'(PULSE score <b>{tb["pulse_score"]:.2f}</b>), and <b>{tw["name"]}</b> is the most reliable bowler '
    f'(PULSE score <b>{tw["pulse_score"]:.2f}</b>).</p>',
    unsafe_allow_html=True,
)

kpi_row([
    (f"{S('balls'):,.0f}", "Deliveries analysed"),
    (f"{S('matches'):,.0f}", "Matches"),
    (f"{S('pressure_balls'):,.0f}", "Pressure balls (top 25% per innings)"),
    (f"{S('eligible_batters'):,.0f}", "Eligible batters (120+ pressure balls)"),
    (f"{S('eligible_bowlers'):,.0f}", "Eligible bowlers (120+ pressure balls)"),
])

tab_bat, tab_bowl, tab_method, tab_find = st.tabs(["🏏 Batters", "🎯 Bowlers", "📐 Method", "🔎 Player lookup"])

with tab_bat:
    st.subheader("Top 10 batters under pressure")
    st.markdown('<p class="pl-note">Ranked by PULSE score: 40% value added on pressure balls, 25% win probability added, '
                '20% lift over their own normal level, 15% consistency. Hover over a bar for details.</p>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**PULSE score**")
        st.plotly_chart(score_bars(bat10, PINK, "bat"), use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.markdown("**Strike rate: normal vs under pressure**")
        st.plotly_chart(dumbbell(bat10, "sr_normal", "sr_pressure", "Strike rate", ".1f"),
                        use_container_width=True, config={"displayModeBar": False})
    st.markdown("#### Batter rankings")
    ranking_table(bat, {
        "rank": "#", "name": "Batter", "pulse_score": "PULSE", "pressure_balls": "Pressure balls",
        "sr_pressure": "SR pressure", "sr_normal": "SR normal", "avg_pressure": "Avg pressure", "avg_normal": "Avg normal",
        "consistency_pct": "Consistency %", "top10_pct": "Top-10 in resamples %",
    }, key="bat_n")

with tab_bowl:
    st.subheader("Top 10 bowlers under pressure")
    st.markdown('<p class="pl-note">Same PULSE score, measured on runs saved and wickets taken against what is expected '
                'in each situation. Hover over a bar for details.</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**PULSE score**")
        st.plotly_chart(score_bars(bowl10, BLUE, "bowl"), use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.markdown("**Economy: normal vs under pressure (lower is better)**")
        st.plotly_chart(dumbbell(bowl10, "econ_normal", "econ_pressure", "Economy (runs per over)", ".2f"),
                        use_container_width=True, config={"displayModeBar": False})
    st.markdown("#### Bowler rankings")
    ranking_table(bowl, {
        "rank": "#", "name": "Bowler", "pulse_score": "PULSE", "pressure_balls": "Pressure balls",
        "econ_pressure": "Econ pressure", "econ_normal": "Econ normal", "wkts_pressure": "Wickets pressure",
        "sr_pressure": "Strike rate pressure", "consistency_pct": "Consistency %", "top10_pct": "Top-10 in resamples %",
    }, key="bowl_n")

with tab_method:
    st.subheader("How pressure is measured")
    st.markdown('<p class="pl-note">Every ball gets a win probability from DLS-style resource curves fitted to the data. '
                'Its Pressure Index is how much that probability can swing on the ball. The top 25% of balls in each '
                'innings are pressure balls.</p>', unsafe_allow_html=True)
    kpi_row([
        (f"{S('close_pressure_pct'):.1f}%", "Pressure balls with the game in the balance (20–80% win chance)"),
        (f"{S('close_normal_pct'):.1f}%", "Normal balls with the game in the balance"),
        (f"{S('wkt_pressure_pct'):.1f}%", "Wicket rate on pressure balls"),
        (f"{S('wkt_normal_pct'):.1f}%", "Wicket rate on normal balls"),
        (f"{S('brier'):.3f}", "Win-probability accuracy (Brier score; 0 = perfect, 0.25 = coin toss)"),
    ])
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Predicted vs actual win rate**")
        st.plotly_chart(calibration_chart(), use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.markdown("**Where pressure balls happen**")
        st.plotly_chart(phase_chart(), use_container_width=True, config={"displayModeBar": False})

    with st.expander("Full methodology in brief", expanded=False):
        st.markdown(
            """
1. **Clean and join** all six datasets. Wides are not balls faced, byes and leg-byes are not charged to the bowler,
   run-outs are not bowler wickets, super overs are excluded and rain-revised targets are used.
2. **Resource curves:** expected runs left = Z(w) × (1 − e^(−k(w) × balls left)) for each number of wickets in hand
   (the DLS form), adjusted for each season's IPL and T20I scoring level.
3. **Win probability** for every ball: chasing side = chance of scoring the runs needed; side batting first = chance
   its projected total beats an average chase.
4. **Pressure Index** = expected swing in win probability on the ball, ×1.2 in knockouts. Pressure balls are the
   top 25% within each innings (cutoffs 1.02 in the first innings and 1.52 in the second).
5. **Value per ball** = runs and wickets compared with what is expected in the same innings, phase, wickets lost,
   competition and pace or spin. A wicket costs the runs it takes away from the team at that moment.
6. **Fairness:** at least 120 pressure balls; empirical-Bayes (DerSimonian-Laird) shrinkage for small samples;
   lower weight for games against Associate sides (0.5) and Ireland or Zimbabwe (0.8).
7. **PULSE score** = 40% pressure value + 25% win probability added + 20% lift over own normal + 15% consistency,
   each as a z-score.
8. **Stress tests:** 300 bootstrap resamples of matches, five weight settings (at most one name changes) and
   minimum-ball cutoffs from 60 to 200 (the top 8 batters never change).
"""
        )

with tab_find:
    st.subheader("Look up any eligible player")
    role = st.radio("Role", ["Batter", "Bowler"], horizontal=True)
    df = bat if role == "Batter" else bowl
    name = st.selectbox("Player", df["name"].tolist())
    r = df[df["name"] == name].iloc[0]
    st.markdown(f"**{name}** · {r['teams']} · PULSE rank **{int(r['rank'])} of {len(df)}** "
                f"(score {r['pulse_score']:.2f}; top 10 in {int(r['top10_pct'])}% of resamples)")
    m1, m2, m3, m4 = st.columns(4)
    if role == "Batter":
        m1.metric("Strike rate under pressure", f"{r['sr_pressure']:.1f}", f"{r['sr_pressure'] - r['sr_normal']:+.1f} vs normal")
        avg_p, avg_n = r["avg_pressure"], r["avg_normal"]
        if pd.notna(avg_p) and pd.notna(avg_n):
            m2.metric("Average under pressure", f"{avg_p:.1f}", f"{avg_p - avg_n:+.1f} vs normal")
        else:
            m2.metric("Average under pressure", "–")
    else:
        m1.metric("Economy under pressure", f"{r['econ_pressure']:.2f}",
                  f"{r['econ_pressure'] - r['econ_normal']:+.2f} vs normal", delta_color="inverse")
        m2.metric("Wickets under pressure", f"{int(r['wkts_pressure'])}", f"1 every {r['sr_pressure']:.1f} balls",
                  delta_color="off")
    m3.metric("Pressure balls", f"{int(r['pressure_balls'])}", f"{int(r['pressure_innings'])} innings/spells", delta_color="off")
    m4.metric("Consistency", f"{int(r['consistency_pct'])}%", "pressure innings with positive impact", delta_color="off")

st.markdown(
    '<p class="pl-foot">PULSE · Pressure-Under-Leverage Statistical Evaluation · SupeRR Selector Season 2, Round 1 · '
    "Data: supplied IPL &amp; T20I ball-by-ball dataset (2022–2026)</p>",
    unsafe_allow_html=True,
)
