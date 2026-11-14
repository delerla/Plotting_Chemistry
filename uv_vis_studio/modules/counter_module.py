"""
counter_module.py - Domain Telemetry, Unified Cross-Studio Navigation & Institutional Footer
Tracks page visits across the Master Gateway and all 5 specialized characterization studios
(FTIR, XRD, XPS, UV-Vis, SEM-EDX) and provides a standardized scientific UI navigation bar.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import streamlit as st

MASTER_HUB_URL = "https://delerla-plotting-chemistry-app-gu8u0i.streamlit.app/"

DOMAIN_REGISTRY: Dict[str, Dict[str, str]] = {
    "master_hub": {
        "name": "Materials Characterization Hub",
        "short": "Master Hub",
        "url": "https://delerla-plotting-chemistry-app-gu8u0i.streamlit.app/",
        "badge_label": "HUB",
        "color": "0f172a",
        "icon": ""
    },
    "uv_vis_studio": {
        "name": "UV-Vis & Photokinetics Studio",
        "short": "UV-Vis",
        "url": "https://delerla-uv-vis-studio.streamlit.app/",
        "badge_label": "UV-VIS",
        "color": "0284c7",
        "icon": ""
    },
    "xps_studio": {
        "name": "XPS Core-Level Studio",
        "short": "XPS",
        "url": "https://delerla-xps-studio.streamlit.app/",
        "badge_label": "XPS",
        "color": "0f172a",
        "icon": ""
    },
    "xrd_studio": {
        "name": "XRD Crystallography Studio",
        "short": "XRD",
        "url": "https://delerla-xrd-studio.streamlit.app/",
        "badge_label": "XRD",
        "color": "0284c7",
        "icon": ""
    },
    "ftir_studio": {
        "name": "FTIR Spectroscopy Studio",
        "short": "FTIR",
        "url": "https://delerla-ftir-studio.streamlit.app/",
        "badge_label": "FTIR",
        "color": "0f172a",
        "icon": ""
    },
    "sem_edx_studio": {
        "name": "SEM-EDX Microstructural Studio",
        "short": "SEM-EDX",
        "url": "https://delerla-sem-edx-studi.streamlit.app/",
        "badge_label": "SEM-EDX",
        "color": "0284c7",
        "icon": ""
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
    """
    cfg = DOMAIN_REGISTRY.get(domain_key, {"badge_label": "VISITS", "color": "0f172a"})
    label = cfg.get("badge_label", "VISITS").replace(" ", "%20")
    color = cfg.get("color", "0f172a")
    return f"https://api.visitorbadge.io/api/visitors?path=delerla.plotting_chemistry.{domain_key}&label={label}&countColor=%23{color}&style=flat"


def render_sidebar_counter(domain_key: str):
    """
    Renders a clean, understated visitor telemetry row at the bottom of the sidebar.
    """
    record_page_visit(domain_key)
    badge_url = get_visitor_badge_url(domain_key)
    cfg = DOMAIN_REGISTRY.get(domain_key, {"name": "Domain Studio"})

    st.sidebar.markdown(f"""
    <div style="border-top: 1px solid #e2e8f0; padding-top: 10px; margin-top: 14px; display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 0.70rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">
            Module Telemetry
        </span>
        <img src="{badge_url}" alt="{cfg.get('name')} Visits" style="height: 18px; vertical-align: middle; border-radius: 2px;" />
    </div>
    """, unsafe_allow_html=True)


def render_footer_counter(domain_key: str):
    """
    Renders a minimal visitor badge in the footer of the Master Hub.
    """
    badge_url = get_visitor_badge_url(domain_key)
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; align-items: center; gap: 8px; padding-top: 4px;">
        <span style="font-size: 0.72rem; color: #64748b; font-weight: 500;">Telemetry:</span>
        <img src="{badge_url}" alt="Visits" style="height: 18px; vertical-align: middle; border-radius: 2px;" />
    </div>
    """, unsafe_allow_html=True)


def render_studio_navigation_bar(active_domain_key: str):
    """
    Renders a standardized, institutional top navigation bar across all 5 specialized studios.
    """
    pills_html = []
    for key, info in DOMAIN_REGISTRY.items():
        if key == "master_hub":
            continue
        is_active = (key == active_domain_key)
        if is_active:
            pills_html.append(
                f'<span style="display:inline-flex; align-items:center; padding: 4px 11px; '
                f'background: #0f172a; color: #ffffff; border-radius: 4px; font-size: 0.76rem; font-weight: 600; '
                f'letter-spacing: 0.01em;">'
                f'{info["short"]}</span>'
            )
        else:
            pills_html.append(
                f'<a href="{info["url"]}" target="_blank" style="display:inline-flex; align-items:center; '
                f'padding: 4px 10px; background: #ffffff; color: #475569 !important; '
                f'border: 1px solid #cbd5e1; border-radius: 4px; text-decoration: none !important; '
                f'font-size: 0.76rem; font-weight: 500;">'
                f'{info["short"]}</a>'
            )

    st.markdown(f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-top: 3px solid #0f172a; border-radius: 6px; padding: 8px 14px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
        <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
            <a href="{MASTER_HUB_URL}" target="_blank" style="display:inline-flex; align-items:center; gap:5px; padding: 4px 11px; background: #ffffff; color: #0f172a !important; border: 1px solid #94a3b8; border-radius: 4px; text-decoration: none !important; font-weight: 600; font-size: 0.76rem;">
                ← Master Hub
            </a>
            <span style="color: #cbd5e1; margin: 0 2px;">|</span>
            <span style="font-size: 0.71rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-right: 2px;">Modules:</span>
            {"".join(pills_html)}
        </div>
        <div>
            <a href="{MASTER_HUB_URL}#community-reviews" target="_blank" style="display:inline-flex; align-items:center; padding: 4px 10px; background: #ffffff; color: #475569 !important; border: 1px solid #cbd5e1; border-radius: 4px; text-decoration: none !important; font-size: 0.74rem; font-weight: 500;">
                Community Feedback &amp; Wishes →
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_unified_studio_footer(active_domain_key: str, studio_title: str, studio_subtitle: str):
    """
    Renders a single standardized institutional footer across all dedicated studios.
    Attribution appears strictly once in the footer.
    """
    badge_url = get_visitor_badge_url(active_domain_key)
    st.markdown(f"""
    <div style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; color: #64748b; font-size: 0.78rem; line-height: 1.5;">
        <div>
            <strong style="color: #334155;">{studio_title}</strong> — {studio_subtitle}<br/>
            <span>© 2026 Dr. Deler Langenberg • MIT Open-Source License</span> •
            <a href="{MASTER_HUB_URL}" target="_blank" style="color: #0284c7; text-decoration: none; font-weight: 500;">Master Hub</a> •
            <a href="{MASTER_HUB_URL}#community-reviews" target="_blank" style="color: #0284c7; text-decoration: none; font-weight: 500;">Reviews &amp; Feature Requests</a> •
            <a href="https://github.com/delerla/Plotting_Chemistry" target="_blank" style="color: #0284c7; text-decoration: none; font-weight: 500;">GitHub</a> •
            <a href="mailto:delerla@yahoo.de" style="color: #0284c7; text-decoration: none; font-weight: 500;">Contact</a>
        </div>
        <div style="display: inline-flex; align-items: center; gap: 8px;">
            <img src="{badge_url}" alt="{studio_title} Visits" style="height: 18px; vertical-align: middle; border-radius: 2px;" />
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_cross_domain_traffic_panel():
    """
    Renders a compact, institutional multi-domain telemetry bar on the Master Gateway (app.py).
    """
    badges_html = []
    for key, info in DOMAIN_REGISTRY.items():
        b_url = get_visitor_badge_url(key)
        badges_html.append(
            f'<div style="display: inline-flex; align-items: center; gap: 6px; background: #ffffff; '
            f'border: 1px solid #e2e8f0; padding: 3px 9px; border-radius: 4px;">'
            f'<span style="font-size: 0.72rem; font-weight: 600; color: #334155;">{info["short"]}</span>'
            f'<img src="{b_url}" alt="{info["name"]}" style="height: 17px; vertical-align: middle; border-radius: 2px;" />'
            f'</div>'
        )

    st.markdown(
        f'<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 14px; margin: 12px 0 16px 0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">'
        f'<div style="font-size: 0.76rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.04em;">'
        f'Platform Module Telemetry'
        f'</div>'
        f'<div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center;">'
        f'{"".join(badges_html)}'
        f'</div></div>',
        unsafe_allow_html=True
    )
