"""
counter_module.py - Real-Time Domain Traffic, Unified Cross-Studio Navigation & Footer Engine
Tracks page visits across the Master Gateway and all 5 specialized characterization studios
(FTIR, XRD, XPS, UV-Vis, SEM-EDX) and provides a unified scientific UI navigation bar.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import streamlit as st

MASTER_HUB_URL = "https://delerla-plotting-chemistry-app-gu8u0i.streamlit.app/"

DOMAIN_REGISTRY: Dict[str, Dict[str, str]] = {
    "master_hub": {
        "name": "Master Hub Gateway",
        "short": "Master Hub",
        "url": "https://delerla-plotting-chemistry-app-gu8u0i.streamlit.app/",
        "badge_label": "HUB VISITS",
        "color": "0284c7",
        "icon": "🏠"
    },
    "uv_vis_studio": {
        "name": "UV-Vis Photokinetics Studio",
        "short": "UV-Vis Studio",
        "url": "https://delerla-uv-vis-studio.streamlit.app/",
        "badge_label": "UV-VIS VISITS",
        "color": "0284c7",
        "icon": "☀️"
    },
    "xps_studio": {
        "name": "XPS Deep-Intelligence Studio",
        "short": "XPS Studio",
        "url": "https://delerla-xps-studio.streamlit.app/",
        "badge_label": "XPS VISITS",
        "color": "ea580c",
        "icon": "⚡"
    },
    "xrd_studio": {
        "name": "XRD Crystallography Studio",
        "short": "XRD Studio",
        "url": "https://delerla-xrd-studio.streamlit.app/",
        "badge_label": "XRD VISITS",
        "color": "7c3aed",
        "icon": "💎"
    },
    "ftir_studio": {
        "name": "FTIR Spectroscopy Studio",
        "short": "FTIR Studio",
        "url": "https://delerla-ftir-studio.streamlit.app/",
        "badge_label": "FTIR VISITS",
        "color": "059669",
        "icon": "🔬"
    },
    "sem_edx_studio": {
        "name": "SEM-EDX Microstructural Studio",
        "short": "SEM-EDX Studio",
        "url": "https://delerla-sem-edx-studio.streamlit.app/",
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
    Increments automatically on the cloud whenever a user's browser loads the image.
    """
    cfg = DOMAIN_REGISTRY.get(domain_key, {"badge_label": "VISITS", "color": "0284c7"})
    label = cfg.get("badge_label", "VISITS").replace(" ", "%20")
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
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border: 1px solid #334155; border-radius: 6px; padding: 8px 10px; margin-top: 12px; text-align: center;">
        <div style="font-size: 0.67rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 5px;">
            📊 Live Domain Traffic
        </div>
        <img src="{badge_url}" alt="{cfg.get('name')} Visits" style="display: inline-block; vertical-align: middle; max-width: 100%; height: 20px; border-radius: 3px;" />
    </div>
    """, unsafe_allow_html=True)


def render_footer_counter(domain_key: str):
    """
    Renders a tiny visitor badge at the bottom/footer of the page.
    """
    badge_url = get_visitor_badge_url(domain_key)
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; align-items: center; gap: 8px; padding-top: 4px;">
        <span style="font-size: 0.72rem; color: #64748b; font-weight: 600;">Domain Visits:</span>
        <img src="{badge_url}" alt="Visits" style="height: 18px; vertical-align: middle; border-radius: 3px;" />
    </div>
    """, unsafe_allow_html=True)


def render_studio_navigation_bar(active_domain_key: str):
    """
    Renders a unified, scientific top navigation bar across all 5 specialized studios
    so users can seamlessly switch between techniques or return to the Master Hub.
    """
    pills_html = []
    for key, info in DOMAIN_REGISTRY.items():
        if key == "master_hub":
            continue
        is_active = (key == active_domain_key)
        if is_active:
            pills_html.append(
                f'<span style="display:inline-flex; align-items:center; gap:5px; padding: 5px 11px; '
                f'background: #0284c7; color: #ffffff; border-radius: 5px; font-size: 0.78rem; font-weight: 700; '
                f'box-shadow: 0 1px 2px rgba(0,0,0,0.15);">'
                f'{info["icon"]} {info["short"]} (Active)</span>'
            )
        else:
            pills_html.append(
                f'<a href="{info["url"]}" target="_blank" style="display:inline-flex; align-items:center; gap:5px; '
                f'padding: 5px 10px; background: rgba(255,255,255,0.07); color: #e2e8f0 !important; '
                f'border: 1px solid #334155; border-radius: 5px; text-decoration: none !important; '
                f'font-size: 0.77rem; font-weight: 600;">'
                f'{info["icon"]} {info["short"]}</a>'
            )

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border: 1px solid #334155; border-radius: 8px; padding: 9px 14px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <a href="{MASTER_HUB_URL}" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding: 5px 12px; background: #38bdf8; color: #0f172a !important; border-radius: 5px; text-decoration: none !important; font-weight: 700; font-size: 0.80rem;">
                🏠 ⟵ Master Characterization Hub
            </a>
            <span style="color: #475569; font-weight: 600;">|</span>
            <span style="font-size: 0.74rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">Switch Studio:</span>
            {"".join(pills_html)}
        </div>
        <div>
            <a href="{MASTER_HUB_URL}#community-reviews" target="_blank" style="display:inline-flex; align-items:center; gap:5px; padding: 5px 10px; background: rgba(250, 204, 21, 0.14); color: #facc15 !important; border: 1px solid rgba(250, 204, 21, 0.35); border-radius: 5px; text-decoration: none !important; font-size: 0.76rem; font-weight: 600;">
                💬 Reviews & Wishes
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_unified_studio_footer(active_domain_key: str, studio_title: str, studio_subtitle: str):
    """
    Renders a standardized scientific footer across all dedicated studios,
    directing reviews/wishes to the Master Hub and displaying the domain visitor counter.
    """
    badge_url = get_visitor_badge_url(active_domain_key)
    st.markdown(f"""
    <div style="margin-top: 3.2rem; padding: 1.1rem 1.4rem; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div style="font-size: 0.83rem; color: #334155;">
            💬 <strong>Have feedback, a material benchmark request, or a feature wish for {studio_title}?</strong>
            Reviews and wishes are centralized on the Master Characterization Hub.
        </div>
        <a href="{MASTER_HUB_URL}#community-reviews" target="_blank" style="background: #0284c7; color: #ffffff !important; padding: 6px 14px; border-radius: 5px; text-decoration: none !important; font-size: 0.81rem; font-weight: 600; white-space: nowrap;">
            ✍️ Leave a Review or Wish on Master Hub ⟶
        </a>
    </div>
    <div style="margin-top: 1.2rem; padding-top: 1.0rem; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; color: #64748b; font-size: 0.81rem; line-height: 1.6;">
        <div>
            <strong>{studio_title}</strong> • {studio_subtitle}<br>
            Engineered & Maintained by <strong>Dr. Deler Langenberg</strong> •
            <a href="{MASTER_HUB_URL}" target="_blank" style="color: #0284c7; text-decoration: none; font-weight: 600;">Master Hub</a> •
            <a href="https://github.com/delerla/Plotting_Chemistry" target="_blank" style="color: #0284c7; text-decoration: none; font-weight: 600;">GitHub Repository</a> •
            <a href="mailto:delerla@yahoo.de" style="color: #0284c7; text-decoration: none; font-weight: 600;">Contact: delerla@yahoo.de</a>
            <span style="color: #94a3b8; margin-left: 6px;">© 2026 Dr. Deler Langenberg (MIT License)</span>
        </div>
        <div style="display: inline-flex; align-items: center; gap: 8px;">
            <span style="font-size: 0.73rem; color: #64748b; font-weight: 600;">Studio Visits:</span>
            <img src="{badge_url}" alt="{studio_title} Visits" style="height: 19px; vertical-align: middle; border-radius: 3px;" />
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_cross_domain_traffic_panel():
    """
    Renders a sleek multi-domain traffic monitor on the Master Gateway (app.py)
    allowing Dr. Deler Langenberg to see relative engagement across all studios.
    """
    badges_html = []
    for key, info in DOMAIN_REGISTRY.items():
        b_url = get_visitor_badge_url(key)
        badges_html.append(
            f'<div style="display: inline-flex; align-items: center; gap: 6px; background: #ffffff; '
            f'border: 1px solid #cbd5e1; padding: 4px 10px; border-radius: 5px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">'
            f'<span style="font-size: 0.80rem;">{info["icon"]}</span>'
            f'<span style="font-size: 0.73rem; font-weight: 700; color: #1e293b;">{info["short"]}:</span>'
            f'<img src="{b_url}" alt="{info["name"]}" style="height: 18px; vertical-align: middle; border-radius: 2px;" />'
            f'</div>'
        )

    st.markdown(
        f'<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; margin: 14px 0 18px 0;">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">'
        f'<div>'
        f'<span style="font-size: 0.85rem; font-weight: 700; color: #0f172a;">📊 Ecosystem Engagement & Live Visitor Analytics</span>'
        f'<span style="font-size: 0.75rem; color: #64748b; margin-left: 6px;">(Real-time traffic across Master Hub & all 5 Intelligence Studios)</span>'
        f'</div>'
        f'</div>'
        f'<div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center;">'
        f'{"".join(badges_html)}'
        f'</div></div>',
        unsafe_allow_html=True
    )
