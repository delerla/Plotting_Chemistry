"""
feedback_module.py - Academic Community Reviews, Wishes & Feedback Engine
Centralized on the Master Characterization Gateway for authentic researcher reviews,
ratings, and feature wishlists across all characterization domains.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import urllib.parse
import streamlit as st

# Starts completely empty; only records real user submissions.
INITIAL_REVIEWS: List[Dict[str, Any]] = []


def get_reviews_file_path() -> Path:
    """Returns the persistent JSON file path for community reviews."""
    current = Path(__file__).resolve().parent
    for candidate in [current.parent, current.parent.parent]:
        if (candidate / "data").exists() or (candidate / "app.py").exists():
            data_dir = candidate / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            return data_dir / "community_reviews.json"
    data_dir = current.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "community_reviews.json"


def load_reviews(file_path: Path) -> List[Dict[str, Any]]:
    """Loads all community reviews from disk, initializing an empty JSON list if missing."""
    if not file_path.exists():
        save_all_reviews(INITIAL_REVIEWS, file_path)
        return list(INITIAL_REVIEWS)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else list(INITIAL_REVIEWS)
    except Exception:
        return list(INITIAL_REVIEWS)


def save_all_reviews(reviews: List[Dict[str, Any]], file_path: Path) -> bool:
    """Serializes reviews list to JSON disk file."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def add_review(new_rev: Dict[str, Any], file_path: Path) -> bool:
    """Appends a new real user review to disk and updates session cache."""
    reviews = load_reviews(file_path)
    reviews.insert(0, new_rev)
    success = save_all_reviews(reviews, file_path)
    st.session_state["community_reviews_cache"] = reviews
    return success


def render_community_reviews(active_app_name: str = "Materials Characterization Hub"):
    """
    Renders an interactive, peer-review & wishlist section on the Master Gateway.
    Allows real users to read authentic community ratings, submit new reviews, and express wishes.
    """
    file_path = get_reviews_file_path()
    st.session_state["community_reviews_cache"] = load_reviews(file_path)

    st.markdown("---")
    st.markdown('<div id="community-reviews"></div>', unsafe_allow_html=True)
    header_placeholder = st.container()

    tab_read, tab_submit = st.tabs([
        "⭐ Read User Reviews & Wishes",
        "✍️ Submit a Review, Suggestion or Feature Wish"
    ])

    # --------------------------------------------------------------------------
    # TAB 2: SUBMIT A NEW REVIEW OR WISH (Executed first so submissions update Tab 1 & Header immediately)
    # --------------------------------------------------------------------------
    with tab_submit:
        st.markdown("##### ✍️ Share Your Real Review, Suggestion, Rating or Feature Wish")
        st.caption("Your feedback is saved immediately to the platform databank and can be forwarded directly to Dr. Deler Langenberg.")

        with st.form(f"community_review_form_{active_app_name}", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                f_name = st.text_input(
                    "Full Name & Academic Title: *",
                    placeholder="e.g. Dr. Ahmed Al-Zahrani, PhD Candidate..."
                )
                f_role = st.text_input(
                    "Role / Department:",
                    placeholder="e.g. Postdoc in Reticular Materials, Lab Researcher..."
                )
                f_inst = st.selectbox(
                    "Institution / University:",
                    [
                        "KAUST (King Abdullah Univ of Science & Technology)",
                        "KFUPM (King Fahd Univ of Petroleum & Minerals)",
                        "KACST (King Abdulaziz City for Science & Tech)",
                        "IAU (Imam Abdulrahman Bin Faisal Univ - iau.edu.sa)",
                        "Other Saudi Institution",
                        "International University / Research Institute",
                        "Industry / R&D Laboratory"
                    ]
                )
                f_domain = st.selectbox(
                    "Target Domain / Studio:",
                    [
                        "Entire Characterization Hub (General)",
                        "UV-Vis & Photokinetics Studio",
                        "XPS Deep-Intelligence Studio",
                        "XRD Crystallography Studio",
                        "FTIR Spectroscopy Studio",
                        "SEM-EDX Microstructural Studio"
                    ]
                )

            with c2:
                f_rating = st.select_slider(
                    "Your Rating:",
                    options=[1, 2, 3, 4, 5],
                    value=5,
                    format_func=lambda x: f"{x} Stars (" + "★" * x + ")"
                )
                f_cat = st.selectbox(
                    "Feedback Category:",
                    [
                        "Academic Review",
                        "Wishlist & Feature Request",
                        "Material Benchmark Request",
                        "Bug Report / Calibration Suggestion"
                    ]
                )
                f_subj = st.text_input(
                    "Subject / Headline:",
                    placeholder="e.g. Deconvolution experience, requested technique..."
                )

            f_comment = st.text_area(
                "Your Review / Thoughts on this Platform: *",
                placeholder="How did this tool assist your characterization, thesis, or paper? What worked well?",
                height=110
            )
            f_wishes = st.text_area(
                "Your Wishes & Feature Suggestions for Future Updates:",
                placeholder="What materials, techniques, or spectroscopic models would you like Dr. Deler Langenberg to add next?",
                height=75
            )

            submit_btn = st.form_submit_button(
                "🚀 Publish Review & Submit Wishes",
                type="primary",
                use_container_width=True
            )

            if submit_btn:
                if not f_name.strip() or not f_comment.strip():
                    st.warning("⚠️ Please provide at least your **Name** and **Review / Thoughts** before submitting.")
                else:
                    inst_code = (
                        "KAUST" if "KAUST" in f_inst else
                        ("KFUPM" if "KFUPM" in f_inst else
                         ("KACST" if "KACST" in f_inst else
                          ("IAU (iau.edu.sa)" if "IAU" in f_inst else f_inst.split("(")[0].strip())))
                    )
                    new_item = {
                        "id": f"rev_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "name": f_name.strip(),
                        "role": f_role.strip() or "Materials Researcher",
                        "institution": inst_code,
                        "domain": f_domain,
                        "rating": int(f_rating),
                        "category": f_cat,
                        "subject": f_subj.strip() or "Platform Review & Feedback",
                        "comment": f_comment.strip(),
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "wishes": f_wishes.strip()
                    }
                    if add_review(new_item, file_path):
                        st.session_state["last_submitted_review"] = new_item
                        st.success("🎉 Thank you! Your review has been published live to the Community Reviews board.")
                    else:
                        st.error("Failed to save review to disk. Please try again.")

        # If a review was just submitted in this session, show direct communication links
        if "last_submitted_review" in st.session_state:
            last_rev = st.session_state["last_submitted_review"]
            mail_subj = urllib.parse.quote(f"[{active_app_name} Review] from {last_rev['name']} ({last_rev['institution']})")
            mail_body = urllib.parse.quote(
                f"Reviewer: {last_rev['name']}\n"
                f"Role: {last_rev['role']}\n"
                f"Institution: {last_rev['institution']}\n"
                f"Target Studio: {last_rev.get('domain', 'General')}\n"
                f"Rating: {last_rev['rating']}/5 Stars\n"
                f"Category: {last_rev['category']}\n"
                f"Subject: {last_rev['subject']}\n\n"
                f"Review:\n{last_rev['comment']}\n\n"
                f"Wishes & Suggestions:\n{last_rev.get('wishes', '')}\n"
            )
            mailto_url = f"mailto:delerla@yahoo.de?subject={mail_subj}&body={mail_body}"

            gh_title = urllib.parse.quote(f"[{last_rev.get('domain', 'Hub')}] {last_rev['subject']}")
            gh_body = urllib.parse.quote(
                f"### Community Feedback from {last_rev['name']} ({last_rev['institution']})\n\n"
                f"- **Role:** {last_rev['role']}\n"
                f"- **Target Studio:** {last_rev.get('domain', 'General')}\n"
                f"- **Rating:** {last_rev['rating']}/5 Stars\n"
                f"- **Category:** {last_rev['category']}\n\n"
                f"#### Review\n{last_rev['comment']}\n\n"
                f"#### Wishes & Feature Suggestions\n{last_rev.get('wishes', 'None specified')}\n"
            )
            gh_url = f"https://github.com/delerla/Plotting_Chemistry/issues/new?title={gh_title}&body={gh_body}"

            st.markdown(f"""
            <div style="background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 12px 16px; margin-top: 10px;">
                <div style="font-size: 0.86rem; font-weight: 700; color: #0369a1; margin-bottom: 6px;">
                    📬 Direct Author Notification Options (Optional)
                </div>
                <div style="font-size: 0.81rem; color: #334155; margin-bottom: 10px;">
                    Your review is already live in the <strong>"⭐ Read User Reviews & Wishes"</strong> tab. You can also send a direct copy to Dr. Deler Langenberg's inbox or open a GitHub discussion ticket:
                </div>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <a href="{mailto_url}" style="background: #0284c7; color: white; padding: 7px 14px; border-radius: 5px; text-decoration: none; font-size: 0.83rem; font-weight: 600;">
                        ✉️ Email Copy Directly to Dr. Deler Langenberg
                    </a>
                    <a href="{gh_url}" target="_blank" style="background: #1e293b; color: white; padding: 7px 14px; border-radius: 5px; text-decoration: none; font-size: 0.83rem; font-weight: 600;">
                        🌟 Open GitHub Feature Wish Ticket
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # REFRESH STATE FOR HEADER & TAB 1 (READ REVIEWS)
    # --------------------------------------------------------------------------
    reviews = st.session_state.get("community_reviews_cache", [])
    has_reviews = len(reviews) > 0
    if has_reviews:
        avg_r = sum(int(r.get("rating", 5)) for r in reviews) / len(reviews)
        rating_display = f"★ {avg_r:.1f}"
        rating_sub = f"{len(reviews)} Community Review{'s' if len(reviews) > 1 else ''}"
    else:
        rating_display = "★ New"
        rating_sub = "Ready for First Review"

    with header_placeholder:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0b1f3a 0%, #173b6c 100%); color: white; padding: 1.25rem 1.5rem; border-radius: 8px; border-left: 6px solid #38bdf8; margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div style="font-size: 0.74rem; letter-spacing: 0.10em; text-transform: uppercase; color: #93c5fd; font-weight: 700;">
                        Peer Review, User Voices & Scientific Community
                    </div>
                    <h3 style="margin: 3px 0 5px 0; font-size: 1.5rem; font-weight: 800; color: #ffffff;">
                        💬 Community Reviews, Suggestions & Feature Wishlist
                    </h3>
                    <div style="font-size: 0.88rem; color: #cbd5e1; max-width: 820px; line-height: 1.4;">
                        Centralized peer-review board for the Materials Characterization Hub and all 5 dedicated studios (FTIR, XRD, XPS, UV-Vis, SEM-EDX). Share your experience, suggestions, and wishes directly with Dr. Deler Langenberg.
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.85rem; font-weight: 800; color: #facc15; line-height: 1;">{rating_display}</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 3px;">{rating_sub}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 1: READ REVIEWS & WISHES
    # --------------------------------------------------------------------------
    with tab_read:
        if not has_reviews:
            st.info(
                "🌟 **No community reviews submitted yet.** "
                "Switch to the **'✍️ Submit a Review, Suggestion or Feature Wish'** tab above to post the first review!"
            )
        else:
            c_stat1, c_stat2, c_stat3 = st.columns([1, 1, 1.5])
            with c_stat1:
                st.metric("Total Published Reviews", len(reviews))
            with c_stat2:
                st.metric("Mean Community Rating", f"{avg_r:.2f} / 5.0")
            with c_stat3:
                categories = [
                    "All Categories",
                    "Academic Review",
                    "Wishlist & Feature Request",
                    "Material Benchmark Request",
                    "Bug Report / Calibration Suggestion"
                ]
                sel_cat = st.selectbox("Filter by Category:", categories, key=f"rev_cat_filter_{active_app_name}")

            filtered_reviews = reviews
            if sel_cat != "All Categories":
                filtered_reviews = [r for r in reviews if r.get("category") == sel_cat]

            st.caption(f"Displaying {len(filtered_reviews)} published community feedback entries:")

            for r in filtered_reviews:
                stars = "★" * int(r.get("rating", 5)) + "☆" * (5 - int(r.get("rating", 5)))
                inst = r.get("institution", "Academic Institution")
                dom_badge = r.get("domain", "Characterization Hub")
                cat_badge = r.get("category", "Academic Review")
                inst_bg = "#e0e7ff" if "KAUST" in inst else ("#dcfce7" if "KFUPM" in inst else ("#e0f2fe" if "KACST" in inst else ("#fef3c7" if "IAU" in inst else "#f1f5f9")))
                inst_txt = "#3730a3" if "KAUST" in inst else ("#166534" if "KFUPM" in inst else ("#0369a1" if "KACST" in inst else ("#92400e" if "IAU" in inst else "#334155")))

                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 0.9rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; margin-bottom: 6px; gap: 6px;">
                        <div>
                            <span style="font-weight: 700; font-size: 1.02rem; color: #0f2b48;">{r.get('name', 'Anonymous Researcher')}</span>
                            <span style="font-size: 0.82rem; color: #64748b;"> • {r.get('role', 'Scientist')}</span>
                            <span style="background: {inst_bg}; color: {inst_txt}; font-size: 0.73rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; margin-left: 6px;">
                                🏛️ {inst}
                            </span>
                            <span style="background: #f1f5f9; color: #475569; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; margin-left: 4px;">
                                🔬 {dom_badge}
                            </span>
                        </div>
                        <div>
                            <span style="color: #f59e0b; font-size: 1.05rem; font-weight: 700;">{stars}</span>
                            <span style="font-size: 0.75rem; color: #94a3b8; margin-left: 6px;">{r.get('date', '')}</span>
                        </div>
                    </div>
                    <div style="font-weight: 700; font-size: 0.93rem; color: #1e3a8a; margin-bottom: 4px;">
                        [{cat_badge}] {r.get('subject', 'Platform Feedback')}
                    </div>
                    <div style="font-size: 0.88rem; color: #334155; line-height: 1.5; margin-bottom: 8px;">
                        "{r.get('comment', '')}"
                    </div>
                    {f'<div style="background: #f8fafc; border-left: 3px solid #0284c7; padding: 6px 10px; border-radius: 4px; font-size: 0.83rem; color: #0369a1;"><strong>💡 Wish / Suggestion:</strong> {r.get("wishes")}</div>' if r.get('wishes') else ''}
                </div>
                """, unsafe_allow_html=True)
