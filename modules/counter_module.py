"""
counter_module.py - Real-Time Domain Traffic & Visitor Tracking Engine
Tracks page visits across the Master Gateway and all 5 specialized characterization studios:
(FTIR, XRD, XPS, UV-Vis, SEM-EDX).
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import streamlit as st

DOMAIN_REGISTRY: Dict[str, Dict[str, str]] = {
    "master_hub": {
        "name": "Master Hub Gateway",
        "badge_label": "HUB VISITS",
        "color": "0284c7",
        "icon": "🏠"
    },
    "ftir_studio": {
        "name": "FTIR Spectroscopy Studio",
        "badge_label": "FTIR VISITS",
        "color": "059669",
        "icon": "🔬"
    },
    "xrd_studio": {
        "name": "XRD Crystallography Studio",
        "badge_label": "XRD VISITS",
        "color": "7c3aed",
        "icon": "💎"
    },
    "xps_studio": {
        "name": "XPS Deep-Intelligence Studio",
        "badge_label": "XPS VISITS",
        "color": "ea580c",
        "icon": "⚡"
    },
    "uv_vis_studio": {
        "name": "UV-Vis Photokinetics Studio",
        "badge_label": "UV-VIS VISITS",
        "color": "0284c7",
        "icon": "☀️"
    },
    "sem_edx_studio": {
        "name": "SEM-EDX Microstructural Studio",
        "badge_label": "SEM-EDX VISITS",
        "color": "4f46e5",
        "icon": "🔍"
    }
}


def get_counter_file_path() -> Path:
    """Returns persistent file path for local traffic logging."""
    current = Path(__file__).resolve().parent
    for candidate in [current.parent, current.parent.parent]:
        if (candidate / "data").exists() or (candidate / "app.py").exists():
            data_dir = candidate / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            return data_dir / "page_views.json"
    data_dir = current.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "page_views.json"


def record_page_visit(domain_key: str) -> int:
    """
    Records a page visit in the local persistent store if this is a new browser session.
    Returns the total local session visit count for this domain.
    """
    file_path = get_counter_file_path()
    views_data: Dict[str, Any] = {}
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                views_data = json.load(f)
        except Exception:
            views_data = {}

    session_flag = f"_session_view_counted_{domain_key}"
    if session_flag not in st.session_state:
        st.session_state[session_flag] = True
        domain_info = views_data.get(domain_key, {"total_views": 0, "last_visit": ""})
        domain_info["total_views"] = int(domain_info.get("total_views", 0)) + 1
        domain_info["last_visit"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        views_data[domain_key] = domain_info
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(views_data, f, indent=2)
        except Exception:
            pass

    return int(views_data.get(domain_key, {}).get("total_views", 1))


def get_visitor_badge_url(domain_key: str) -> str:
    """
    Generates the visitorbadge.io dynamic SVG badge URL.
    This increments automatically on the cloud whenever a user's browser loads the image.
    """
    cfg = DOMAIN_REGISTRY.get(domain_key, {"badge_label": "VISITS", "color": "0284c7"})
    label = cfg.get("badge_label", "VISITS")
    color = cfg.get("color", "0284c7")
    return f"https://api.visitorbadge.io/api/visitors?path=delerla.plotting_chemistry.{domain_key}&label={label}&countColor=%23{color}&style=flat"


def render_sidebar_counter(domain_key: str):
    """
    Renders a compact, professional visitor counter badge in the Streamlit sidebar.
    """
    record_page_visit(domain_key)
    badge_url = get_visitor_badge_url(domain_key)
    cfg = DOMAIN_REGISTRY.get(domain_key, {"name": "Domain Studio"})

    st.sidebar.markdown(f"""
    <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid #334155; border-radius: 6px; padding: 8px 10px; margin-top: 14px; text-align: center;">
        <div style="font-size: 0.68rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 5px;">
            📊 Live Visitor Counter
        </div>
        <img src="{badge_url}" alt="{cfg.get('name')} Visits" style="display: inline-block; vertical-align: middle; max-width: 100%; height: 20px; border-radius: 3px;" />
        <div style="font-size: 0.65rem; color: #64748b; margin-top: 4px;">
            Real-time multi-user analytics
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_footer_counter(domain_key: str):
    """
    Renders a tiny visitor badge at the bottom/footer of the page.
    """
    badge_url = get_visitor_badge_url(domain_key)
    st.markdown(f"""
    <div style="display: inline-flex; align-items: center; gap: 8px; margin-left: 12px; vertical-align: middle;">
        <span style="font-size: 0.72rem; color: #64748b; font-weight: 600;">Total Traffic:</span>
        <img src="{badge_url}" alt="Visits" style="height: 18px; vertical-align: middle;" />
    </div>
    """, unsafe_allow_html=True)


def render_cross_domain_traffic_panel():
    """
    Renders a sleek multi-domain traffic monitor on the Master Gateway (app.py)
    allowing Dr. Deler Langenberg to see relative engagement across all studios.
    """
    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; margin: 15px 0 20px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
                <span style="font-size: 0.85rem; font-weight: 700; color: #0f172a;">📊 Ecosystem Engagement & Live Visitor Analytics</span>
                <span style="font-size: 0.75rem; color: #64748b; margin-left: 6px;">(Real-time traffic across Master Hub & all 5 Intelligence Studios)</span>
            </div>
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 14px; margin-top: 10px; align-items: center;">
    """, unsafe_allow_html=True)

    badges_html = []
    for key, info in DOMAIN_REGISTRY.items():
        b_url = get_visitor_badge_url(key)
        badges_html.append(f"""
        <div style="display: inline-flex; align-items: center; gap: 5px; background: white; border: 1px solid #cbd5e1; padding: 3px 8px; border-radius: 4px;">
            <span style="font-size: 0.75rem;">{info['icon']}</span>
            <span style="font-size: 0.70rem; font-weight: 600; color: #334155;">{info['name'].replace(' Studio', '')}:</span>
            <img src="{b_url}" alt="{info['name']}" style="height: 18px; vertical-align: middle;" />
        </div>
        """)

    st.markdown("".join(badges_html) + "</div></div>", unsafe_allow_html=True)
