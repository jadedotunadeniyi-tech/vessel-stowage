"""
Vessel Stowage Calculator
=========================
A professional crude oil loading plan tool for offshore tanker operations.

Implements:
- Volume → Draft prediction (with API/SG correction)
- Draft → Volume calculation
- Under Keel Clearance (UKC) assessment
- Vessel utilisation scoring
- Full fleet specification browser
- Custom vessel entry
- Industry-standard deductions (bunker, fresh water, constants)
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import math

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Vessel Stowage Calculator",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:       #0b0f1a;
    --surface:  #111827;
    --surface2: #1a2236;
    --border:   #1e3a5f;
    --accent:   #0ea5e9;
    --accent2:  #f59e0b;
    --accent3:  #10b981;
    --danger:   #ef4444;
    --text:     #e2e8f0;
    --muted:    #64748b;
    --mono:     'IBM Plex Mono', monospace;
    --sans:     'IBM Plex Sans', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--sans);
    background: var(--bg);
    color: var(--text);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Main area */
.main .block-container { padding: 1.5rem 2rem 3rem; }

/* Headers */
h1, h2, h3 { font-family: var(--mono); font-weight: 600; letter-spacing: -0.02em; }
h1 { font-size: 1.8rem; color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
h2 { font-size: 1.2rem; color: var(--accent); margin-top: 1.5rem; }
h3 { font-size: 1rem; color: var(--accent2); }

/* Inputs */
input[type="number"], input[type="text"], select, textarea,
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
}

/* Metric cards */
.metric-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem 1.25rem;
    margin: 0.4rem 0;
}
.metric-label {
    font-size: 0.72rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: var(--mono);
    margin-bottom: 0.2rem;
}
.metric-value {
    font-size: 1.6rem;
    font-weight: 600;
    font-family: var(--mono);
    color: var(--text);
    line-height: 1.1;
}
.metric-unit {
    font-size: 0.8rem;
    color: var(--muted);
    font-family: var(--mono);
    margin-left: 4px;
}

/* Result panel */
.result-panel {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1rem 0;
}
.result-primary {
    font-size: 2.4rem;
    font-weight: 600;
    font-family: var(--mono);
    color: var(--accent);
    line-height: 1.1;
}
.result-secondary {
    font-size: 1.1rem;
    font-family: var(--mono);
    color: var(--accent2);
    margin-top: 0.3rem;
}

/* Score gauge */
.score-bar-bg {
    background: var(--border);
    border-radius: 4px;
    height: 12px;
    margin: 8px 0;
    overflow: hidden;
}
.score-bar-fill {
    height: 12px;
    border-radius: 4px;
    transition: width 0.6s ease;
}

/* Warning / status badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 3px;
    font-size: 0.72rem;
    font-family: var(--mono);
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.badge-ok   { background: #064e3b; color: #6ee7b7; border: 1px solid #065f46; }
.badge-warn { background: #78350f; color: #fde68a; border: 1px solid #92400e; }
.badge-risk { background: #7f1d1d; color: #fca5a5; border: 1px solid #991b1b; }

/* Section divider */
.sec-div {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* Table */
.stDataFrame { border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }
.stDataFrame th {
    background: var(--surface2) !important;
    color: var(--muted) !important;
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

/* Info box */
.info-box {
    background: #0c1a2e;
    border: 1px solid #1e3a5f;
    border-left: 3px solid var(--accent);
    border-radius: 4px;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: var(--muted);
    margin: 0.5rem 0;
    font-family: var(--sans);
    line-height: 1.5;
}

/* Tab style */
button[data-baseweb="tab"] {
    font-family: var(--mono) !important;
    font-size: 0.85rem !important;
    color: var(--muted) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* Expander */
details { border: 1px solid var(--border) !important; border-radius: 6px !important; }
details > summary { color: var(--accent2) !important; font-family: var(--mono) !important; }

/* Buttons */
.stButton > button {
    background: var(--accent) !important;
    color: #0b0f1a !important;
    font-family: var(--mono) !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 4px !important;
    letter-spacing: 0.04em;
}
.stButton > button:hover { opacity: 0.9 !important; }

/* Number input arrows */
button[aria-label*="decrement"], button[aria-label*="increment"] {
    color: var(--muted) !important;
}

/* Label overrides */
label { color: var(--muted) !important; font-size: 0.8rem !important; font-family: var(--mono) !important; }
p { color: var(--text); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# VESSEL DATABASE  (extracted from workbook + computed fields)
# ─────────────────────────────────────────────────────────────────────────────

# Lightship = Displacement - DWT (from each vessel's individual sheet)
VESSELS: list[dict] = [
    # ── Mother Vessels (offshore loading terminals) ──────────────────────────
    {
        "name": "Alkebulan", "class": "Suezmax",
        "dwt": 159988, "grt": 64473,
        "tank_m3_98": 171991.2, "keel": 50.6, "loa": 274.2, "beam": 48.0,
        "displacement": 183068.1, "constant": 500, "bunker_fw": 2500,
        "draft_full": 17.05, "block_coeff": 0.7959,
        "breakwater_lat": 11.3, "api_ref": 19,
        "note": "Suezmax mother vessel — BIA only",
    },
    {
        "name": "Green Eagle", "class": "Suezmax",
        "dwt": 154164, "grt": 78922,
        "tank_m3_98": 166696.0, "keel": 49.94, "loa": 274.2, "beam": 48.0,
        "displacement": 176634.0, "constant": 500, "bunker_fw": 2500,
        "draft_full": 16.36, "block_coeff": 0.7862,
        "breakwater_lat": 11.3, "api_ref": 19,
        "note": "Suezmax mother vessel — BIA only",
    },
    {
        "name": "Bryanston", "class": "Aframax",
        "dwt": 108493, "grt": 46904,
        "tank_m3_98": 120859.9, "keel": 48.0, "loa": 244.26, "beam": 42.03,
        "displacement": 125786.0, "constant": 203, "bunker_fw": 2500,
        "draft_full": 15.228, "block_coeff": 0.7850,
        "breakwater_lat": 11.35, "api_ref": 27,
        "note": "Aframax mother vessel — BIA only",
    },
    {
        "name": "Nourah", "class": "Aframax",
        "dwt": 123755, "grt": 70933,
        "tank_m3_98": 133639.2, "keel": 48.99, "loa": 249.97, "beam": 44.0,
        "displacement": 142000.0, "constant": 400, "bunker_fw": 2500,
        "draft_full": 15.5, "block_coeff": 0.800,
        "breakwater_lat": 11.3, "api_ref": 27,
        "note": "Aframax — BIA",
    },
    # ── LR-1 / Intermediate ──────────────────────────────────────────────────
    {
        "name": "MT San Barth", "class": "LR-1",
        "dwt": 71533, "grt": 40456,
        "tank_m3_98": 77629.5, "keel": 47.14, "loa": 219.0, "beam": 32.23,
        "displacement": 84769.0, "constant": 203, "bunker_fw": 2500,
        "draft_full": 13.901, "block_coeff": 0.8429,
        "breakwater_lat": 3.45, "api_ref": 27,
        "note": "Permanent BIA intermediate storage; breakwater LAT 3.45 m",
    },
    {
        "name": "Louloulight", "class": "LR-1",
        "dwt": 77020.8, "grt": 32957,
        "tank_m3_98": 82937.43, "keel": 49.05, "loa": 228.0, "beam": 32.24,
        "displacement": 90000.0, "constant": 300, "bunker_fw": 2000,
        "draft_full": 14.0, "block_coeff": 0.820,
        "breakwater_lat": 11.3, "api_ref": 27,
        "note": "",
    },
    {
        "name": "MT VILMA", "class": "LR-1",
        "dwt": 62915, "grt": 27799,
        "tank_m3_98": 75532.0, "keel": 45.33, "loa": 213.35, "beam": 32.29,
        "displacement": 75000.0, "constant": 250, "bunker_fw": 2000,
        "draft_full": 13.5, "block_coeff": 0.820,
        "breakwater_lat": 11.3, "api_ref": 27,
        "note": "",
    },
    {
        "name": "PRESTIGIOUS", "class": "LR-1",
        "dwt": 75025, "grt": 31165,
        "tank_m3_98": 75742.8, "keel": 47.24, "loa": 228.5, "beam": 32.24,
        "displacement": 88000.0, "constant": 300, "bunker_fw": 2000,
        "draft_full": 13.8, "block_coeff": 0.820,
        "breakwater_lat": 11.3, "api_ref": 27,
        "note": "",
    },
    # ── MR Tankers (shuttle fleet) ───────────────────────────────────────────
    {
        "name": "MT Westmore", "class": "MR",
        "dwt": 47418, "grt": 22808,
        "tank_m3_98": 53611.58, "keel": 46.37, "loa": 183.0, "beam": 32.2,
        "displacement": 57531.58, "constant": 270, "bunker_fw": 1500,
        "draft_full": 12.471, "block_coeff": 0.7638,
        "breakwater_lat": 3.45, "api_ref": 20,
        "note": "Westmore storage — dredge depth 7 m",
    },
    {
        "name": "MT Chapel", "class": "MR",
        "dwt": 48354, "grt": 22050,
        "tank_m3_98": 50332.4, "keel": 45.55, "loa": 182.5, "beam": 32.23,
        "displacement": 48354.0, "constant": 270, "bunker_fw": 1500,
        "draft_full": 12.93, "block_coeff": 0.6203,
        "breakwater_lat": 14.0, "api_ref": 20,
        "note": "Chapel storage — deep water terminal",
    },
    {
        "name": "MT Jasmine S", "class": "MR",
        "dwt": 47205, "grt": 28150,
        "tank_m3_98": 54244.97, "keel": 46.27, "loa": 179.88, "beam": 32.23,
        "displacement": 56048.0, "constant": 270, "bunker_fw": 1500,
        "draft_full": 12.27, "block_coeff": 0.7862,
        "breakwater_lat": 3.45, "api_ref": 20,
        "note": "Jasmine S storage",
    },
    {
        "name": "MT Laphroaig", "class": "MR",
        "dwt": 35832.8, "grt": 19707,
        "tank_m3_98": 39944.98, "keel": 44.11, "loa": 154.31, "beam": 36.03,
        "displacement": 45364.4, "constant": 100, "bunker_fw": 1500,
        "draft_full": 9.18, "block_coeff": 0.8671,
        "breakwater_lat": 3.45, "api_ref": 20.5,
        "note": "Shuttle — Chapel/JasmineS; dredge depth 2.55 m",
    },
    {
        "name": "MT Pinarello", "class": "MR",
        "dwt": 35832.84, "grt": 19707,
        "tank_m3_98": 39914.477, "keel": 41.11, "loa": 154.31, "beam": 36.0,
        "displacement": 45296.9, "constant": 100, "bunker_fw": 1500,
        "draft_full": 9.203, "block_coeff": 0.8640,
        "breakwater_lat": 3.45, "api_ref": 20,
        "note": "Shuttle — Chapel/JasmineS; dredge depth 2.55 m",
    },
    {
        "name": "MT Sherlock", "class": "MR",
        "dwt": 35640.4, "grt": 19707,
        "tank_m3_98": 39939.857, "keel": 39.29, "loa": 154.31, "beam": 36.03,
        "displacement": 45172.0, "constant": 100, "bunker_fw": 1500,
        "draft_full": 9.188, "block_coeff": 0.8627,
        "breakwater_lat": 3.45, "api_ref": 20,
        "note": "Shuttle — Jasmine S primary; dredge depth 2.55 m",
    },
    {
        "name": "MONTAGU", "class": "MR",
        "dwt": 47425.33, "grt": 30032,
        "tank_m3_98": 52219.03, "keel": 46.95, "loa": 183.0, "beam": 32.2,
        "displacement": 55000.0, "constant": 270, "bunker_fw": 1500,
        "draft_full": 12.2, "block_coeff": 0.780,
        "breakwater_lat": 3.45, "api_ref": 20,
        "note": "",
    },
    # ── General Purpose tankers ──────────────────────────────────────────────
    {
        "name": "MT Bedford", "class": "General Purpose",
        "dwt": 18568, "grt": 14876,
        "tank_m3_98": 26098.32, "keel": 39.7, "loa": 157.5, "beam": 27.7,
        "displacement": 25081.0, "constant": 200, "bunker_fw": 800,
        "draft_full": 7.146, "block_coeff": 0.620,
        "breakwater_lat": 3.45, "api_ref": 20,
        "note": "Ibom offshore loader; dredge depth 2.55 m",
    },
    {
        "name": "MT Bagshot", "class": "General Purpose",
        "dwt": 18457, "grt": 9729,
        "tank_m3_98": 20059.1, "keel": 39.67, "loa": 145.06, "beam": 22.9,
        "displacement": 23611.0, "constant": 29, "bunker_fw": 800,
        "draft_full": 9.1, "block_coeff": 0.720,
        "breakwater_lat": 3.45, "api_ref": 20,
        "note": "Shuttle — Barge Starturn; dredge depth 2.55 m",
    },
    {
        "name": "MT Woodstock", "class": "General Purpose",
        "dwt": 15761, "grt": 8602,
        "tank_m3_98": 16050.0, "keel": 35.6, "loa": 139.95, "beam": 21.0,
        "displacement": 20000.0, "constant": 250, "bunker_fw": 800,
        "draft_full": 8.252, "block_coeff": 0.760,
        "breakwater_lat": 3.45, "api_ref": 20,
        "note": "Shuttle — Duke (Awoba); dredge depth 2.55 m",
    },
    {
        "name": "MT Rathbone", "class": "General Purpose",
        "dwt": 12590.59, "grt": 7446,
        "tank_m3_98": 13082.02, "keel": 33.2, "loa": 140.95, "beam": 19.6,
        "displacement": 16145.59, "constant": 220, "bunker_fw": 800,
        "draft_full": 6.956, "block_coeff": 0.720,
        "breakwater_lat": 3.45, "api_ref": 20,
        "note": "Shuttle — Ibom/Balham; dredge depth 2.55 m",
    },
    {
        "name": "MT Rahama", "class": "General Purpose",
        "dwt": 8318.07, "grt": 6204,
        "tank_m3_98": 8265.0, "keel": 34.0, "loa": 115.0, "beam": 21.4,
        "displacement": 11620.83, "constant": 0, "bunker_fw": 400,
        "draft_full": 6.14, "block_coeff": 0.700,
        "breakwater_lat": 3.3, "api_ref": 20,
        "note": "Awoba shuttle",
    },
    {
        "name": "MT Enford", "class": "General Purpose",
        "dwt": 17300.4, "grt": 11271,
        "tank_m3_98": 18479.62, "keel": 39.48, "loa": 144.0, "beam": 23.0,
        "displacement": 23220.61, "constant": 250, "bunker_fw": 450,
        "draft_full": 8.983, "block_coeff": 0.740,
        "breakwater_lat": 3.45, "api_ref": 20,
        "note": "Dredge depth 2.55 m",
    },
    {
        "name": "MT Santa Monica", "class": "General Purpose",
        "dwt": 6208.83, "grt": 4126,
        "tank_m3_98": 5819.248, "keel": 28.5, "loa": 112.01, "beam": 16.2,
        "displacement": 8761.25, "constant": 20, "bunker_fw": 300,
        "draft_full": 6.125, "block_coeff": 0.680,
        "breakwater_lat": 3.45, "api_ref": 23,
        "note": "Multi-field shuttle; avg API 23°",
    },
    {
        "name": "MT Elizabeth-G Spirit", "class": "General Purpose",
        "dwt": 3200, "grt": 2177,
        "tank_m3_98": 4221.943, "keel": 42.0, "loa": 88.28, "beam": 15.0,
        "displacement": 1123.71, "constant": 20, "bunker_fw": 300,
        "draft_full": 3.974, "block_coeff": 0.660,
        "breakwater_lat": 5.0, "api_ref": 27,
        "note": "Small coaster",
    },
    {
        "name": "Duke", "class": "General Purpose",
        "dwt": 19651, "grt": 11118,
        "tank_m3_98": 19137.0, "keel": 38.62, "loa": 140.0, "beam": 23.0,
        "displacement": 22000.0, "constant": 200, "bunker_fw": 600,
        "draft_full": 8.5, "block_coeff": 0.720,
        "breakwater_lat": 3.45, "api_ref": 41.2,
        "note": "Duke storage barge — Point D (Awoba)",
    },
    {
        "name": "XT Dolphin", "class": "General Purpose",
        "dwt": 28045, "grt": 18492,
        "tank_m3_98": 33445.0, "keel": 42.0, "loa": 176.2, "beam": 27.0,
        "displacement": 33000.0, "constant": 200, "bunker_fw": 800,
        "draft_full": 9.5, "block_coeff": 0.740,
        "breakwater_lat": 3.45, "api_ref": 27,
        "note": "",
    },
    {
        "name": "BROMLEY", "class": "General Purpose",
        "dwt": 18074.48, "grt": 9019,
        "tank_m3_98": 17347.0, "keel": 40.07, "loa": 144.06, "beam": 22.6,
        "displacement": 21000.0, "constant": 200, "bunker_fw": 600,
        "draft_full": 8.3, "block_coeff": 0.720,
        "breakwater_lat": 3.45, "api_ref": 20,
        "note": "",
    },
    {
        "name": "GOLDEN JASMINE", "class": "General Purpose",
        "dwt": 17300, "grt": 11271,
        "tank_m3_98": 18479.4, "keel": 39.48, "loa": 145.0, "beam": 23.0,
        "displacement": 21000.0, "constant": 200, "bunker_fw": 600,
        "draft_full": 8.3, "block_coeff": 0.720,
        "breakwater_lat": 3.45, "api_ref": 20,
        "note": "",
    },
    {
        "name": "EMANTHA", "class": "General Purpose",
        "dwt": 17464, "grt": 11438,
        "tank_m3_98": 19196.0, "keel": 40.5, "loa": 144.71, "beam": 23.0,
        "displacement": 21000.0, "constant": 200, "bunker_fw": 600,
        "draft_full": 8.4, "block_coeff": 0.720,
        "breakwater_lat": 3.45, "api_ref": 20,
        "note": "",
    },
    {
        "name": "Transko Yudhistira", "class": "General Purpose",
        "dwt": 6872.35, "grt": 5339,
        "tank_m3_98": 8309.2, "keel": 32.8, "loa": 108.0, "beam": 19.2,
        "displacement": 9000.0, "constant": 100, "bunker_fw": 400,
        "draft_full": 6.5, "block_coeff": 0.680,
        "breakwater_lat": 3.3, "api_ref": 20,
        "note": "",
    },
]

# Convert to dict keyed by name for fast lookup
VESSEL_DB: dict[str, dict] = {v["name"]: v for v in VESSELS}


# ─────────────────────────────────────────────────────────────────────────────
# ENGINEERING CONSTANTS & HELPERS
# ─────────────────────────────────────────────────────────────────────────────

BBL_PER_M3       = 6.28981        # 1 m³ = 6.28981 US barrels (ASTM)
SEAWATER_DENSITY = 1.025          # t/m³  (standard seawater)
FRESHWATER_DENSITY = 1.000        # t/m³
UKC_MIN_RIVER    = 0.30           # m — NNPC/ops standard for river channel
UKC_MIN_OPEN     = 0.50           # m — offshore / open water minimum
TRIM_ALLOWANCE   = 0.05           # 5% draft reduction allowance for trim


def api_to_sg(api: float) -> float:
    """Convert API gravity to specific gravity at 15°C / 60°F."""
    return 141.5 / (131.5 + api)


def sg_to_api(sg: float) -> float:
    """Convert specific gravity to API gravity."""
    return (141.5 / sg) - 131.5


def m3_to_bbl(m3: float) -> float:
    return m3 * BBL_PER_M3


def bbl_to_m3(bbl: float) -> float:
    return bbl / BBL_PER_M3


def cargo_mass_mt(volume_m3: float, api: float) -> float:
    """Mass of cargo in metric tonnes given volume (m³) and API gravity."""
    sg = api_to_sg(api)
    return volume_m3 * sg


def classify_vessel(dwt: float) -> str:
    """Assign tanker class from DWT per industry convention."""
    if dwt >= 200_000:   return "VLCC"
    if dwt >= 120_000:   return "Suezmax"
    if dwt >= 80_000:    return "Aframax"
    if dwt >= 55_000:    return "LR-2"
    if dwt >= 40_000:    return "LR-1"
    if dwt >= 25_000:    return "MR"
    if dwt >= 10_000:    return "General Purpose"
    return "Small Tanker"


def lightship_mass(vessel: dict) -> float:
    """Lightship displacement = Full displacement - DWT."""
    return vessel["displacement"] - vessel["dwt"]


def total_deductions_mt(vessel: dict, bunker_mt: float, fw_mt: float,
                         constant_mt: float) -> float:
    """Sum of all non-cargo weight deductions."""
    return bunker_mt + fw_mt + constant_mt


def available_dwt_for_cargo(vessel: dict, bunker_mt: float,
                              fw_mt: float, constant_mt: float) -> float:
    """DWT available for cargo after deductions."""
    return vessel["dwt"] - total_deductions_mt(vessel, bunker_mt, fw_mt, constant_mt)


def volume_to_draft(vessel: dict, volume_m3: float, api: float,
                    bunker_mt: float, fw_mt: float, constant_mt: float,
                    seawater_density: float = SEAWATER_DENSITY) -> dict:
    """
    Calculate loaded draft from cargo volume.

    Method (industry standard):
    1. Convert volume to cargo mass using API-derived SG
    2. Total displacement = lightship + cargo + deductions
    3. Draft = displacement / (block coeff × LBP × beam × seawater density)
    4. Apply trim correction
    Returns a dict with all intermediates.
    """
    sg             = api_to_sg(api)
    cargo_mass     = volume_m3 * sg                        # MT
    lightship      = lightship_mass(vessel)
    deductions     = bunker_mt + fw_mt + constant_mt
    total_disp     = lightship + cargo_mass + deductions   # MT loaded displacement
    
    # Underkeel calculation via block coefficient
    Cb   = vessel["block_coeff"]
    LBP  = vessel["loa"]  # using LOA as proxy when LBP not separate
    beam = vessel["beam"]
    
    # T = Displacement / (Cb × L × B × ρ)
    draft_m = total_disp / (Cb * LBP * beam * seawater_density)
    
    # Max draft = full-load draft (structural limit)
    draft_max = vessel["draft_full"]
    
    # Cargo mass in bbls
    volume_bbl = m3_to_bbl(volume_m3)
    
    # Utilisation vs 98% tank capacity
    tank_98_m3  = vessel["tank_m3_98"]
    tank_98_bbl = m3_to_bbl(tank_98_m3)
    utilisation = (volume_m3 / tank_98_m3) * 100
    
    # DWT utilisation
    cargo_plus_ded = cargo_mass + deductions
    dwt_util = (cargo_plus_ded / vessel["dwt"]) * 100
    
    return {
        "sg":                sg,
        "cargo_mass_mt":     cargo_mass,
        "lightship_mt":      lightship,
        "deductions_mt":     deductions,
        "total_displacement_mt": total_disp,
        "draft_m":           round(draft_m, 3),
        "draft_max_m":       draft_max,
        "over_draft":        draft_m > draft_max,
        "volume_m3":         volume_m3,
        "volume_bbl":        round(volume_bbl),
        "tank_98_m3":        tank_98_m3,
        "tank_98_bbl":       round(tank_98_bbl),
        "tank_utilisation_pct": round(utilisation, 1),
        "dwt_utilisation_pct":  round(dwt_util, 1),
        "available_dwt_cargo_mt": round(vessel["dwt"] - deductions, 1),
    }


def draft_to_volume(vessel: dict, draft_m: float, api: float,
                    bunker_mt: float, fw_mt: float, constant_mt: float,
                    seawater_density: float = SEAWATER_DENSITY) -> dict:
    """
    Calculate cargo volume from a given loaded draft.

    Method:
    1. Displacement at draft = Cb × L × B × T × ρ_sw
    2. Cargo mass = Displacement - Lightship - Deductions
    3. Volume = cargo mass / SG
    """
    sg         = api_to_sg(api)
    Cb         = vessel["block_coeff"]
    LBP        = vessel["loa"]
    beam       = vessel["beam"]
    lightship  = lightship_mass(vessel)
    deductions = bunker_mt + fw_mt + constant_mt
    
    total_disp  = Cb * LBP * beam * draft_m * seawater_density   # MT
    cargo_mass  = total_disp - lightship - deductions             # MT cargo
    volume_m3   = cargo_mass / sg if cargo_mass > 0 else 0.0
    volume_bbl  = m3_to_bbl(volume_m3)
    
    tank_98_m3  = vessel["tank_m3_98"]
    tank_98_bbl = m3_to_bbl(tank_98_m3)
    utilisation = (volume_m3 / tank_98_m3) * 100 if tank_98_m3 > 0 else 0
    
    cargo_plus_ded = max(0, cargo_mass) + deductions
    dwt_util = (cargo_plus_ded / vessel["dwt"]) * 100
    
    return {
        "sg":                sg,
        "cargo_mass_mt":     max(0, cargo_mass),
        "lightship_mt":      lightship,
        "deductions_mt":     deductions,
        "total_displacement_mt": total_disp,
        "draft_input_m":     draft_m,
        "draft_max_m":       vessel["draft_full"],
        "over_draft":        draft_m > vessel["draft_full"],
        "volume_m3":         round(max(0, volume_m3), 1),
        "volume_bbl":        round(max(0, volume_bbl)),
        "tank_98_m3":        tank_98_m3,
        "tank_98_bbl":       round(tank_98_bbl),
        "tank_utilisation_pct": round(max(0, utilisation), 1),
        "dwt_utilisation_pct":  round(max(0, dwt_util), 1),
        "available_dwt_cargo_mt": round(vessel["dwt"] - deductions, 1),
    }


def ukc_assessment(vessel: dict, draft_m: float, water_depth: float) -> dict:
    """
    Under Keel Clearance assessment.
    UKC = Water depth - Vessel draft - Keel protrusion
    Keel is structural — not added to draft here; keel field = depth of keel below baseline.
    Standard: UKC ≥ 10% of draft or 0.30 m (whichever greater) for restricted waters.
    """
    ukc = water_depth - draft_m
    # Regulatory minimum (10% rule + absolute floor)
    ukc_required = max(UKC_MIN_RIVER, draft_m * 0.10)
    ukc_status = "ADEQUATE" if ukc >= ukc_required else ("MARGINAL" if ukc >= 0 else "AGROUND RISK")
    return {
        "ukc_m": round(ukc, 2),
        "ukc_required_m": round(ukc_required, 2),
        "ukc_status": ukc_status,
        "margin_m": round(ukc - ukc_required, 2),
    }


def utilisation_color(pct: float) -> str:
    if pct >= 95:  return "#10b981"   # green — excellent
    if pct >= 85:  return "#f59e0b"   # amber — good
    if pct >= 70:  return "#f97316"   # orange — moderate
    return "#ef4444"                  # red — poor


def get_score_label(pct: float) -> tuple[str, str]:
    """(label, css_class)"""
    if pct >= 95: return "EXCELLENT", "badge-ok"
    if pct >= 85: return "GOOD",      "badge-ok"
    if pct >= 70: return "MODERATE",  "badge-warn"
    if pct >= 50: return "LOW",       "badge-warn"
    return "VERY LOW", "badge-risk"


# ─────────────────────────────────────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def metric_card(label: str, value: str, unit: str = "", color: str = ""):
    col_style = f"color:{color};" if color else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="{col_style}">{value}<span class="metric-unit">{unit}</span></div>
    </div>""", unsafe_allow_html=True)


def score_bar(pct: float, label: str = ""):
    color  = utilisation_color(pct)
    slabel, sbadge = get_score_label(pct)
    st.markdown(f"""
    <div style="margin:0.6rem 0">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
            <span style="font-size:0.78rem;font-family:var(--mono);color:var(--muted)">{label}</span>
            <div>
                <span style="font-size:1.1rem;font-weight:600;font-family:var(--mono);color:{color}">{pct:.1f}%</span>
                &nbsp;<span class="badge {sbadge}">{slabel}</span>
            </div>
        </div>
        <div class="score-bar-bg">
            <div class="score-bar-fill" style="width:{min(pct,100):.1f}%;background:{color}"></div>
        </div>
    </div>""", unsafe_allow_html=True)


def ukc_badge(status: str, ukc: float, required: float):
    if status == "ADEQUATE":
        badge_cls, icon = "badge-ok",   "✓"
    elif status == "MARGINAL":
        badge_cls, icon = "badge-warn", "⚠"
    else:
        badge_cls, icon = "badge-risk", "✕"
    st.markdown(f"""
    <div class="metric-card" style="border-color:{'#065f46' if status=='ADEQUATE' else '#92400e' if status=='MARGINAL' else '#991b1b'}">
        <div class="metric-label">Under Keel Clearance (UKC)</div>
        <div style="display:flex;align-items:center;gap:10px;margin-top:4px">
            <span style="font-size:1.5rem;font-family:var(--mono);font-weight:600;color:{'#6ee7b7' if status=='ADEQUATE' else '#fde68a' if status=='MARGINAL' else '#fca5a5'}">
                {ukc:.2f} m
            </span>
            <span class="badge {badge_cls}">{icon} {status}</span>
        </div>
        <div style="font-size:0.78rem;color:var(--muted);font-family:var(--mono);margin-top:4px">
            Required minimum: {required:.2f} m
        </div>
    </div>""", unsafe_allow_html=True)


def section(title: str):
    st.markdown(f"<h2>{title}</h2>", unsafe_allow_html=True)


def info(text: str):
    st.markdown(f'<div class="info-box">{text}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE — custom vessels
# ─────────────────────────────────────────────────────────────────────────────

if "custom_vessels" not in st.session_state:
    st.session_state.custom_vessels = {}


def all_vessels() -> dict[str, dict]:
    db = dict(VESSEL_DB)
    db.update(st.session_state.custom_vessels)
    return db


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR  — vessel selector & deductions
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("<h1 style='font-size:1.1rem;margin-bottom:0.2rem'>🛢️ STOWAGE CALCULATOR</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.72rem;color:var(--muted);font-family:var(--mono);margin-top:0'>Offshore Crude Oil Loading Tool</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:var(--border);margin:0.5rem 0 1rem'>", unsafe_allow_html=True)

    vessel_names = sorted(all_vessels().keys())
    selected_name = st.selectbox("Select Vessel", vessel_names)
    vessel = all_vessels()[selected_name]

    st.markdown("---")
    st.markdown("<span style='font-size:0.75rem;color:var(--muted);font-family:var(--mono)'>CARGO & ENVIRONMENT</span>", unsafe_allow_html=True)

    api = st.number_input(
        "Cargo API Gravity (°)",
        min_value=5.0, max_value=60.0,
        value=float(vessel.get("api_ref", 27)),
        step=0.5,
        help="API gravity of the crude oil. Affects cargo density and hence volume-to-draft relationship.",
    )
    seawater_dens = st.number_input(
        "Seawater Density (t/m³)",
        min_value=1.000, max_value=1.030,
        value=1.025, step=0.001,
        help="Standard seawater = 1.025 t/m³. Adjust for dock water (fresh/brackish).",
        format="%.3f",
    )
    water_depth = st.number_input(
        "Water Depth at Loading Point (m)",
        min_value=1.0, max_value=30.0,
        value=float(vessel.get("breakwater_lat", 3.45) + 2.0),
        step=0.1,
        help="Depth at the specific loading point (LAT + tide height). Used for UKC calculation.",
    )

    st.markdown("---")
    st.markdown("<span style='font-size:0.75rem;color:var(--muted);font-family:var(--mono)'>DEDUCTIONS (non-cargo weight)</span>", unsafe_allow_html=True)

    default_bunker = float(vessel.get("bunker_fw", 1500)) * 0.6   # 60% of default
    default_fw     = float(vessel.get("bunker_fw", 1500)) * 0.4
    default_const  = float(vessel.get("constant", 200))

    bunker_mt = st.number_input(
        "Bunker (fuel) on board (MT)",
        min_value=0.0, max_value=5000.0,
        value=round(default_bunker, 0),
        step=10.0,
        help="Heavy fuel oil + diesel oil + lube oil in metric tonnes. Affects available DWT.",
    )
    fw_mt = st.number_input(
        "Fresh Water on board (MT)",
        min_value=0.0, max_value=2000.0,
        value=round(default_fw, 0),
        step=10.0,
        help="Potable and distilled water. Density = 1.000 t/m³.",
    )
    constant_mt = st.number_input(
        "Ship's Constant (MT)",
        min_value=0.0, max_value=1000.0,
        value=round(default_const, 0),
        step=5.0,
        help="Unmeasured weight: spare parts, stores, ropes, sediment, paint — typically 50–500 MT depending on vessel size.",
    )

    total_ded = bunker_mt + fw_mt + constant_mt
    avail_dwt = vessel["dwt"] - total_ded
    sg_cargo  = api_to_sg(api)

    st.markdown(f"""
    <div class="metric-card" style="margin-top:0.5rem">
        <div class="metric-label">Total Deductions</div>
        <div class="metric-value" style="font-size:1.1rem">{total_ded:,.0f} <span class="metric-unit">MT</span></div>
        <div style="font-size:0.72rem;color:var(--muted);font-family:var(--mono);margin-top:4px">
            Available DWT for cargo: <strong style="color:var(--accent)">{avail_dwt:,.0f} MT</strong>
        </div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Cargo SG @ API {api}°</div>
        <div class="metric-value" style="font-size:1.1rem">{sg_cargo:.4f}</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT — Tabs
# ─────────────────────────────────────────────────────────────────────────────

st.markdown(f"<h1>Vessel Stowage Calculator — {selected_name}</h1>", unsafe_allow_html=True)
st.markdown(f"""
<div style="display:flex;gap:10px;margin-bottom:1rem;flex-wrap:wrap">
    <span class="badge badge-ok">Class: {vessel['class']}</span>
    <span class="badge badge-ok">DWT: {vessel['dwt']:,.0f} MT</span>
    <span class="badge badge-ok">Tank 98%: {m3_to_bbl(vessel['tank_m3_98']):,.0f} bbl</span>
    <span class="badge badge-ok">LOA: {vessel['loa']} m</span>
    <span class="badge badge-ok">Beam: {vessel['beam']} m</span>
    <span class="badge badge-ok">Full Draft: {vessel['draft_full']} m</span>
    <span class="badge badge-warn">Breakwater LAT: {vessel['breakwater_lat']} m</span>
</div>
""", unsafe_allow_html=True)

if vessel.get("note"):
    info(f"📌 {vessel['note']}")

tab1, tab2, tab3, tab4 = st.tabs([
    "📦  Volume → Draft",
    "📐  Draft → Volume",
    "📋  Fleet Browser",
    "➕  Add Vessel",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1  —  Volume → Draft
# ════════════════════════════════════════════════════════════════════════════

with tab1:
    section("Enter Cargo Volume → Predicted Draft")
    info("""
        Enter the intended cargo quantity in US barrels or m³.  
        The calculator applies your API gravity, bunker, fresh water and ship's constant from the sidebar 
        to predict the loaded draft using the <strong>block coefficient method</strong> (IACS standard).  
        The result includes utilisation scoring against the vessel's 98% tank capacity.
    """)

    col_inp, col_res = st.columns([1, 1.2], gap="large")

    with col_inp:
        vol_unit = st.radio("Input unit", ["US Barrels", "Cubic Metres (m³)"], horizontal=True)
        max_bbl  = round(m3_to_bbl(vessel["tank_m3_98"]) * 1.05)
        max_m3   = round(vessel["tank_m3_98"] * 1.05)

        if vol_unit == "US Barrels":
            cargo_input_bbl = st.number_input(
                "Cargo Volume (US Bbls)",
                min_value=0,
                max_value=max_bbl,
                value=round(m3_to_bbl(vessel["tank_m3_98"]) * 0.95),
                step=1000,
            )
            cargo_m3 = bbl_to_m3(cargo_input_bbl)
        else:
            cargo_input_m3 = st.number_input(
                "Cargo Volume (m³)",
                min_value=0.0,
                max_value=float(max_m3),
                value=round(vessel["tank_m3_98"] * 0.95, 1),
                step=100.0,
            )
            cargo_m3  = cargo_input_m3
            cargo_input_bbl = round(m3_to_bbl(cargo_m3))

        st.markdown(f"""
        <div style="font-size:0.78rem;color:var(--muted);font-family:var(--mono);margin-top:0.5rem">
            ≡ {cargo_m3:,.1f} m³ &nbsp;/&nbsp; {cargo_input_bbl:,} US Bbls
        </div>""", unsafe_allow_html=True)

        run1 = st.button("⚡ Calculate Draft", key="btn_v2d", use_container_width=True)

    with col_res:
        if run1 or True:   # auto-calculate
            res = volume_to_draft(vessel, cargo_m3, api, bunker_mt, fw_mt, constant_mt, seawater_dens)
            ukc = ukc_assessment(vessel, res["draft_m"], water_depth)

            draft_color = "#ef4444" if res["over_draft"] else "#0ea5e9"
            over_label  = " ⚠ OVER SCANTLING DRAFT" if res["over_draft"] else ""

            st.markdown(f"""
            <div class="result-panel">
                <div class="metric-label">Predicted Loaded Draft</div>
                <div class="result-primary" style="color:{draft_color}">{res['draft_m']:.3f} m{over_label}</div>
                <div class="result-secondary">Max allowable: {res['draft_max_m']} m</div>
            </div>""", unsafe_allow_html=True)

            # Scores
            score_bar(res["tank_utilisation_pct"], "Tank Utilisation (vs 98% capacity)")
            score_bar(res["dwt_utilisation_pct"],  "DWT Utilisation")

            # UKC
            ukc_badge(ukc["ukc_status"], ukc["ukc_m"], ukc["ukc_required_m"])

            # Detail table
            st.markdown("<hr class='sec-div'>", unsafe_allow_html=True)
            st.markdown("<h3>Loading Calculation Summary</h3>", unsafe_allow_html=True)

            detail_rows = [
                ("Cargo Volume",          f"{res['volume_m3']:,.1f} m³  /  {res['volume_bbl']:,} US Bbls"),
                ("Cargo API",             f"{api:.1f}°  (SG {res['sg']:.4f})"),
                ("Cargo Mass",            f"{res['cargo_mass_mt']:,.1f} MT"),
                ("Lightship Mass",        f"{res['lightship_mt']:,.1f} MT"),
                ("Bunker on board",       f"{bunker_mt:,.0f} MT"),
                ("Fresh water on board",  f"{fw_mt:,.0f} MT"),
                ("Ship's constant",       f"{constant_mt:,.0f} MT"),
                ("Total Deductions",      f"{res['deductions_mt']:,.0f} MT"),
                ("Total Displacement",    f"{res['total_displacement_mt']:,.1f} MT"),
                ("Predicted Draft",       f"{res['draft_m']:.3f} m"),
                ("Scantling Draft",       f"{res['draft_max_m']} m"),
                ("Water Depth",           f"{water_depth:.2f} m"),
                ("UKC",                   f"{ukc['ukc_m']:.2f} m  [{ukc['ukc_status']}]"),
                ("Tank Utilisation",      f"{res['tank_utilisation_pct']}%  of 98% capacity"),
                ("DWT Utilisation",       f"{res['dwt_utilisation_pct']}%"),
            ]
            df_detail = pd.DataFrame(detail_rows, columns=["Parameter", "Value"])
            st.dataframe(df_detail, use_container_width=True, hide_index=True, height=420)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2  —  Draft → Volume
# ════════════════════════════════════════════════════════════════════════════

with tab2:
    section("Enter Target Draft → Calculated Cargo Volume")
    info("""
        Enter the <strong>maximum permissible draft</strong> (tide-constrained, or bar-crossing draft).  
        The calculator back-calculates the cargo volume achievable at that draft, 
        accounting for API density, bunker, fresh water and ship's constant.  
        Used in practice to determine how much you can safely load for a given tidal window.
    """)

    col_d1, col_d2 = st.columns([1, 1.2], gap="large")

    with col_d1:
        draft_inp = st.number_input(
            "Target / Maximum Draft (m)",
            min_value=1.0,
            max_value=float(vessel["draft_full"]),
            value=round(min(vessel["draft_full"] * 0.90, water_depth * 0.90), 3),
            step=0.01,
            format="%.3f",
            help="Enter the tide-adjusted permissible draft. Must be ≤ vessel scantling draft.",
        )

        # Quick tide helper
        with st.expander("🌊 Tidal Draft Helper"):
            lat_d  = st.number_input("River Depth at LAT (m)", 1.0, 20.0,
                                     vessel.get("breakwater_lat", 3.45), 0.05)
            tide_h = st.number_input("Expected High Tide (m)", 0.0, 5.0, 2.0, 0.1)
            safety = st.slider("Safety factor on river draft (%)", 80, 95, 90)
            river_draft = lat_d + tide_h
            max_perm    = river_draft * (safety / 100)
            st.markdown(f"""
            <div class="info-box">
                River Draft = {river_draft:.2f} m<br>
                Max Permissible Draft = {river_draft:.2f} × {safety}% = <strong>{max_perm:.3f} m</strong>
            </div>""", unsafe_allow_html=True)
            if st.button("Apply this draft", key="apply_tide"):
                draft_inp = max_perm

        run2 = st.button("⚡ Calculate Volume", key="btn_d2v", use_container_width=True)

    with col_d2:
        res2 = draft_to_volume(vessel, draft_inp, api, bunker_mt, fw_mt, constant_mt, seawater_dens)
        ukc2 = ukc_assessment(vessel, draft_inp, water_depth)

        st.markdown(f"""
        <div class="result-panel">
            <div class="metric-label">Cargo Volume at {draft_inp:.3f} m draft</div>
            <div class="result-primary">{res2['volume_bbl']:,} <span style="font-size:1.2rem">US Bbls</span></div>
            <div class="result-secondary">{res2['volume_m3']:,.1f} m³ &nbsp;·&nbsp; {res2['cargo_mass_mt']:,.0f} MT cargo</div>
        </div>""", unsafe_allow_html=True)

        score_bar(res2["tank_utilisation_pct"], "Tank Utilisation (vs 98% capacity)")
        score_bar(res2["dwt_utilisation_pct"],  "DWT Utilisation")
        ukc_badge(ukc2["ukc_status"], ukc2["ukc_m"], ukc2["ukc_required_m"])

        st.markdown("<hr class='sec-div'>", unsafe_allow_html=True)
        st.markdown("<h3>Loading Calculation Summary</h3>", unsafe_allow_html=True)

        rows2 = [
            ("Input Draft",              f"{draft_inp:.3f} m"),
            ("Cargo API",                f"{api:.1f}°  (SG {res2['sg']:.4f})"),
            ("Cargo Volume",             f"{res2['volume_m3']:,.1f} m³  /  {res2['volume_bbl']:,} US Bbls"),
            ("Cargo Mass",               f"{res2['cargo_mass_mt']:,.1f} MT"),
            ("Lightship Mass",           f"{res2['lightship_mt']:,.1f} MT"),
            ("Bunker on board",          f"{bunker_mt:,.0f} MT"),
            ("Fresh water on board",     f"{fw_mt:,.0f} MT"),
            ("Ship's constant",          f"{constant_mt:,.0f} MT"),
            ("Total Deductions",         f"{res2['deductions_mt']:,.0f} MT"),
            ("Total Displacement",       f"{res2['total_displacement_mt']:,.1f} MT"),
            ("Scantling Draft",          f"{res2['draft_max_m']} m"),
            ("Water Depth",              f"{water_depth:.2f} m"),
            ("UKC",                      f"{ukc2['ukc_m']:.2f} m  [{ukc2['ukc_status']}]"),
            ("Tank 98% Capacity",        f"{res2['tank_98_bbl']:,} US Bbls  /  {res2['tank_98_m3']:,.1f} m³"),
            ("Tank Utilisation",         f"{res2['tank_utilisation_pct']}%  of 98% capacity"),
            ("DWT Utilisation",          f"{res2['dwt_utilisation_pct']}%"),
            ("Available DWT for cargo",  f"{res2['available_dwt_cargo_mt']:,.1f} MT"),
        ]
        df2 = pd.DataFrame(rows2, columns=["Parameter", "Value"])
        st.dataframe(df2, use_container_width=True, hide_index=True, height=450)


# ════════════════════════════════════════════════════════════════════════════
# TAB 3  —  Fleet Browser
# ════════════════════════════════════════════════════════════════════════════

with tab3:
    section("Fleet Vessel Specification Browser")

    all_v = all_vessels()
    class_filter = st.multiselect(
        "Filter by Class",
        options=sorted(set(v["class"] for v in all_v.values())),
        default=[],
        placeholder="All classes",
    )

    rows_spec = []
    for nm, v in sorted(all_v.items()):
        if class_filter and v["class"] not in class_filter:
            continue
        bbl_98 = round(m3_to_bbl(v["tank_m3_98"]))
        lightship = lightship_mass(v)
        rows_spec.append({
            "Vessel":          nm,
            "Class":           v["class"],
            "DWT (MT)":        f"{v['dwt']:,.0f}",
            "GRT":             f"{v['grt']:,.0f}",
            "Tank 98% (m³)":   f"{v['tank_m3_98']:,.1f}",
            "Tank 98% (Bbls)": f"{bbl_98:,}",
            "LOA (m)":         v["loa"],
            "Beam (m)":        v["beam"],
            "Keel (m)":        v["keel"],
            "Full Draft (m)":  v["draft_full"],
            "Cb":              f"{v['block_coeff']:.4f}",
            "Lightship (MT)":  f"{lightship:,.0f}",
            "Constant (MT)":   v["constant"],
            "Bkwtr LAT (m)":   v["breakwater_lat"],
            "Ref API":         v["api_ref"],
            "Notes":           v.get("note", ""),
        })

    df_spec = pd.DataFrame(rows_spec)
    st.dataframe(df_spec, use_container_width=True, hide_index=True, height=520)

    # Quick comparison tool
    st.markdown("<hr class='sec-div'>", unsafe_allow_html=True)
    section("Quick Comparison — All Vessels at Current Settings")
    info(f"Showing 95% tank utilisation draft for all vessels | API {api}° | Bunker {bunker_mt:.0f} MT | FW {fw_mt:.0f} MT | Constant {constant_mt:.0f} MT")

    comp_rows = []
    for nm, v in sorted(all_v.items()):
        if class_filter and v["class"] not in class_filter:
            continue
        vol_95 = v["tank_m3_98"] * 0.95
        try:
            r = volume_to_draft(v, vol_95, api, bunker_mt, fw_mt, constant_mt, seawater_dens)
            ukc_c = ukc_assessment(v, r["draft_m"], water_depth)
            flag  = "⚠ OVER" if r["over_draft"] else ("⚠ UKC" if ukc_c["ukc_status"] != "ADEQUATE" else "✓ OK")
            comp_rows.append({
                "Vessel":        nm,
                "Class":         v["class"],
                "Vol 95% (Bbls)":f"{r['volume_bbl']:,}",
                "Draft @95% (m)":f"{r['draft_m']:.3f}",
                "Max Draft (m)": v["draft_full"],
                "UKC (m)":       f"{ukc_c['ukc_m']:.2f}",
                "UKC Status":    ukc_c["ukc_status"],
                "Status":        flag,
            })
        except Exception:
            pass

    df_comp = pd.DataFrame(comp_rows)
    st.dataframe(df_comp, use_container_width=True, hide_index=True, height=480)


# ════════════════════════════════════════════════════════════════════════════
# TAB 4  —  Add / Edit Vessel
# ════════════════════════════════════════════════════════════════════════════

with tab4:
    section("Add New Vessel to Fleet")
    info("""
        Enter the vessel's basic parameters.  
        <strong>Vessel class</strong> is assigned automatically from DWT.  
        <strong>US Barrel capacity</strong> is computed from m³ × 6.28981.  
        <strong>Block coefficient</strong> defaults to class-typical value but can be overridden.  
        All fields marked * are required.
    """)

    with st.form("add_vessel_form"):
        c1, c2, c3 = st.columns(3)

        with c1:
            new_name  = st.text_input("Vessel Name *", placeholder="e.g. MT Balham")
            new_dwt   = st.number_input("DWT (MT) *",     1000.0, 350000.0, 20000.0, 500.0)
            new_grt   = st.number_input("GRT (MT) *",      500.0, 200000.0, 10000.0, 500.0)
            new_disp  = st.number_input("Full Load Displacement (MT) *", 1000.0, 400000.0, 25000.0, 500.0,
                                         help="= Lightship + DWT")

        with c2:
            new_tank  = st.number_input("98% Tank Capacity (m³) *", 100.0, 250000.0, 20000.0, 100.0)
            new_keel  = st.number_input("Keel Depth (m)",    0.0,  60.0,  40.0, 0.5)
            new_loa   = st.number_input("LOA (m) *",         50.0, 340.0, 150.0, 1.0)
            new_beam  = st.number_input("Beam (m) *",        10.0,  70.0,  25.0, 0.5)

        with c3:
            new_draft = st.number_input("Scantling / Full Draft (m) *", 2.0, 25.0, 9.0, 0.1)
            new_const = st.number_input("Ship's Constant (MT)",          0.0, 1000.0, 150.0, 5.0)
            new_bfw   = st.number_input("Bunker + FW default (MT)",       0.0, 5000.0, 1000.0, 50.0)
            new_bwlat = st.number_input("Breakwater / Bar LAT (m)",       0.0,  20.0,   3.45, 0.05)

        st.markdown("<hr class='sec-div'>", unsafe_allow_html=True)
        c4, c5 = st.columns(2)
        with c4:
            new_api   = st.number_input("Reference API Gravity (°)", 5.0, 60.0, 27.0, 0.5)
            new_cb    = st.number_input("Block Coefficient Cb (0 = auto)",
                                         0.0, 1.0, 0.0, 0.01,
                                         help="Leave 0 for class-typical value. Range 0.55–0.90 for tankers.")
        with c5:
            new_note  = st.text_area("Notes", placeholder="Operating area, storage role, dredge depth etc.", height=80)

        submitted = st.form_submit_button("➕ Add to Fleet", use_container_width=True)

        if submitted:
            if not new_name.strip():
                st.error("Vessel name is required.")
            elif new_name in all_vessels():
                st.error(f"'{new_name}' already exists in the fleet.")
            else:
                # Auto-classify
                auto_class = classify_vessel(new_dwt)
                # Auto block coefficient from class if not provided
                cb_defaults = {
                    "VLCC": 0.830, "Suezmax": 0.800, "Aframax": 0.785,
                    "LR-2": 0.790, "LR-1": 0.820, "MR": 0.780,
                    "General Purpose": 0.720, "Small Tanker": 0.680,
                }
                cb_use = new_cb if new_cb > 0 else cb_defaults.get(auto_class, 0.750)

                st.session_state.custom_vessels[new_name] = {
                    "name":          new_name,
                    "class":         auto_class,
                    "dwt":           new_dwt,
                    "grt":           new_grt,
                    "tank_m3_98":    new_tank,
                    "keel":          new_keel,
                    "loa":           new_loa,
                    "beam":          new_beam,
                    "displacement":  new_disp,
                    "constant":      new_const,
                    "bunker_fw":     new_bfw,
                    "draft_full":    new_draft,
                    "block_coeff":   cb_use,
                    "breakwater_lat": new_bwlat,
                    "api_ref":       new_api,
                    "note":          new_note,
                }
                bbl_auto = round(m3_to_bbl(new_tank))
                st.success(f"""
                ✅ **{new_name}** added successfully!  
                Class: **{auto_class}** | Cb: **{cb_use:.3f}** | 
                Tank 98%: **{bbl_auto:,} US Bbls** ({new_tank:,.1f} m³)  
                Select it from the sidebar to run calculations.
                """)
                st.rerun()

    # Show & manage custom vessels
    if st.session_state.custom_vessels:
        st.markdown("<hr class='sec-div'>", unsafe_allow_html=True)
        section("Custom Vessels Added This Session")
        for nm, cv in list(st.session_state.custom_vessels.items()):
            col_v, col_del = st.columns([5, 1])
            with col_v:
                bbl_cv = round(m3_to_bbl(cv["tank_m3_98"]))
                st.markdown(f"""
                <div class="metric-card">
                    <strong style="font-family:var(--mono);color:var(--accent)">{nm}</strong>
                    &nbsp;<span class="badge badge-ok">{cv['class']}</span>
                    <div style="font-size:0.78rem;color:var(--muted);font-family:var(--mono);margin-top:4px">
                        DWT {cv['dwt']:,.0f} MT &nbsp;·&nbsp; 
                        Tank {bbl_cv:,} Bbls &nbsp;·&nbsp;
                        Draft {cv['draft_full']} m &nbsp;·&nbsp;
                        Cb {cv['block_coeff']:.3f}
                    </div>
                </div>""", unsafe_allow_html=True)
            with col_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑", key=f"del_{nm}", help=f"Remove {nm}"):
                    del st.session_state.custom_vessels[nm]
                    st.rerun()
