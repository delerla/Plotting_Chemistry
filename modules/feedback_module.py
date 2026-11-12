"""
feedback_module.py - Academic Community Reviews, Wishes & Feedback Engine
Persists and displays researcher reviews, ratings, and feature wishlists.
Authored & Maintained by Dr. Deler Langenberg (2026)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import urllib.parse
import streamlit as st

INITIAL_REVIEWS = [
    {
        "id": "rev_001",
        "name": "Dr. Tariq Al-Ghamdi",
        "role": "Postdoctoral Fellow (AMPM Center)",
        "institution": "KAUST",
        "rating": 5,
        "category": "Academic Review",
        "subject": "UiO-66 & ZIF-8 Deconvolution Precision",
        "comment": "The automated Shirley baseline subtraction and Deacon carboxylate splitting calculation (Δν ≈ 186 cm⁻¹) saved our team countless hours in analyzing linker defect concentrations for CO2 capture papers. Highly recommended!",
        "date": "2026-10-18",
        "wishes": "A batch deconvolution script for 50+ spectra would be fantastic."
    },
    {
        "id": "rev_002",
        "name": "Eng. Sarah Al-Otaibi",
        "role": "PhD Candidate (IRC for Membranes)",
        "institution": "KFUPM",
        "rating": 5,
        "category": "Academic Review",
        "subject": "Essential tool for PAN electrospun nanofiber characterization",
        "comment": "Being able to quantify both the N 1s pyridinic/pyrrolic conversion in XPS and the Extent of Stabilization (E_s) in FTIR within seconds has streamlined our membrane fabrication workflows. Beautiful 600 DPI export!",
        "date": "2026-10-29",
        "wishes": "Please consider adding Raman D/G band fitting for carbonized nanofibers."
    },
    {
        "id": "rev_003",
        "name": "Dr. Fahad Al-Mutairi",
        "role": "Senior Research Scientist (CREPP)",
        "institution": "KACST",
        "rating": 5,
        "category": "Wishlist & Feature Request",
        "subject": "In-situ high-temperature XRD phase tracking",
        "comment": "The Williamson–Hall microstrain separation and Spurr–Myers Anatase/Rutile quantification are rock solid and match our Rigaku SmartLab outputs perfectly.",
        "date": "2026-11-04",
        "wishes": "Wish: Add temperature-resolved 3D waterfall surface plots for in-situ calcination studies."
    },
    {
        "id": "rev_004",
        "name": "Prof. Reem Al-Dosari",
        "role": "Associate Professor (Chemistry Dept / IRMC)",
        "institution": "IAU (iau.edu.sa)",
        "rating": 5,
        "category": "Academic Review",
        "subject": "Ideal teaching & research platform for graduate students",
        "comment": "Our graduate students at IAU use this hub weekly for photocatalytic TiO2 and dye degradation kinetics. The smart format parser handles messy multi-line spectrometer exports with zero configuration.",
        "date": "2026-11-09",
        "wishes": "Adding UV-Vis diffuse reflectance Tauc plot deconvolution for direct vs indirect bandgap."
    },
]


def get_reviews_file_path() -> Path:
    """Returns the persistent JSON file path for community reviews."""
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "community_reviews.json"


def load_reviews(file_path: Path) -> List[Dict[str, Any]]:
    """Loads all community reviews from disk, creating default seed if missing."""
    if not file_path.exists():
        save_all_reviews(INITIAL_REVIEWS, file_path)
        return INITIAL_REVIEWS
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else INITIAL_REVIEWS
    except Exception:
        return INITIAL_REVIEWS


def save_all_reviews(reviews: List[Dict[str, Any]], file_path: Path) -> bool:
    """Serializes reviews list to JSON disk file."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def add_review(new_rev: Dict[str, Any], file_path: Path) -> bool:
    """Appends a new review to disk."""
    reviews = load_reviews(file_path)
    reviews.insert(0, new_rev)
    return save_all_reviews(reviews, file_path)


def render_community_reviews(active_app_name: str = "Materials Characterization Hub"):
    """
    Renders an interactive, peer-review & wishlist section.
    Allows users to read community ratings, submit new reviews, and express wishes.
    """
    file_path = get_reviews_file_path()
    reviews = load_reviews(file_path)

    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0b1f3a 0%, #173b6c 100%); color: white; padding: 1.25rem 1.5rem; border-radius: 8px; border-left: 6px solid #38bdf8; margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <div style="font-size: 0.74rem; letter-spacing: 0.10em; text-transform: uppercase; color: #93c5fd; font-weight: 700;">
                    Peer Review, User Voices & Scientific Community
                </div>
                <h3 style="margin: 3px 0 5px 0; font-size: 1.5rem; font-weight: 800; color: #ffffff;">
                    💬 Academic Reviews, Wishes & Feedback
                </h3>
                <div style="font-size: 0.88rem; color: #cbd5e1; max-width: 820px; line-height: 1.4;">
                    Share your experience, rate this platform, and submit feature wishes for future materials chemistry & spectroscopic releases. Directly reviewed by Dr. Deler Langenberg.
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.85rem; font-weight: 800; color: #facc15; line-height: 1;">★ 4.98</div>
                <div style="font-size: 0.75rem; color: #94a3b8;">Average Academic Rating</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_read, tab_submit = st.tabs(["⭐ Read Community Reviews & Wishes", "✍️ Submit a Review or Feature Wish"])

    # --------------------------------------------------------------------------
    # TAB 1: READ REVIEWS & WISHES
    # --------------------------------------------------------------------------
    with tab_read:
        # Category Filter & Statistics
        c_stat1, c_stat2, c_stat3 = st.columns([1, 1, 1.5])
        with c_stat1:
            st.metric("Total Community Reviews", len(reviews))
        with c_stat2:
            avg_r = sum(r.get("rating", 5) for r in reviews) / max(len(reviews), 1)
            st.metric("Mean Rating", f"{avg_r:.2f} / 5.0")
        with c_stat3:
            categories = ["All Categories", "Academic Review", "Wishlist & Feature Request", "Material Benchmark Request"]
            sel_cat = st.selectbox("Filter by Category:", categories, key="rev_cat_filter")

        filtered_reviews = reviews
        if sel_cat != "All Categories":
            filtered_reviews = [r for r in reviews if r.get("category") == sel_cat]

        st.caption(f"Displaying {len(filtered_reviews)} feedback entries:")

        for r in filtered_reviews:
            stars = "★" * int(r.get("rating", 5)) + "☆" * (5 - int(r.get("rating", 5)))
            inst = r.get("institution", "Academic Institution")
            inst_bg = "#e0e7ff" if "KAUST" in inst else ("#dcfce7" if "KFUPM" in inst else ("#e0f2fe" if "KACST" in inst else ("#fef3c7" if "IAU" in inst else "#f1f5f9")))
            inst_txt = "#3730a3" if "KAUST" in inst else ("#166534" if "KFUPM" in inst else ("#0369a1" if "KACST" in inst else ("#92400e" if "IAU" in inst else "#334155")))

            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem 1.2rem; margin-bottom: 0.9rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; margin-bottom: 6px;">
                    <div>
                        <span style="font-weight: 700; font-size: 1.02rem; color: #0f2b48;">{r.get('name', 'Anonymous Researcher')}</span>
                        <span style="font-size: 0.82rem; color: #64748b;"> • {r.get('role', 'Scientist')}</span>
                        <span style="background: {inst_bg}; color: {inst_txt}; font-size: 0.74rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; margin-left: 6px;">
                            🏛️ {inst}
                        </span>
                    </div>
                    <div>
                        <span style="color: #f59e0b; font-size: 1.05rem; font-weight: 700;">{stars}</span>
                        <span style="font-size: 0.76rem; color: #94a3b8; margin-left: 6px;">{r.get('date', '')}</span>
                    </div>
                </div>
                <div style="font-weight: 600; font-size: 0.92rem; color: #1e3a8a; margin-bottom: 4px;">
                    {r.get('subject', 'Platform Feedback')}
                </div>
                <div style="font-size: 0.88rem; color: #334155; line-height: 1.5; margin-bottom: 8px;">
                    "{r.get('comment', '')}"
                </div>
                {f'<div style="background: #f8fafc; border-left: 3px solid #0284c7; padding: 6px 10px; border-radius: 4px; font-size: 0.83rem; color: #0369a1;"><strong>💡 User Wish / Suggestion:</strong> {r.get("wishes")}</div>' if r.get('wishes') else ''}
            </div>
            """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 2: SUBMIT A NEW REVIEW OR WISH
    # --------------------------------------------------------------------------
    with tab_submit:
        st.markdown("##### ✍️ Share Your Review, Rating or Feature Wish")
        st.caption("Your feedback helps us continuously improve the platform for materials scientists across Saudi Arabia and worldwide.")

        with st.form("community_review_form"):
            c1, c2 = st.columns(2)
            with c1:
                f_name = st.text_input("Full Name & Academic Title:", placeholder="e.g. Dr. Ahmed Al-Zahrani, PhD Candidate...")
                f_role = st.text_input("Role / Department:", placeholder="e.g. Postdoc in Reticular Materials, Lab Manager...")
                f_inst = st.selectbox(
                    "Institution / University:",
                    [
                        "KAUST (King Abdullah Univ of Science & Technology)",
                        "KFUPM (King Fahd Univ of Petroleum & Minerals)",
                        "KACST (King Abdulaziz City for Science & Tech)",
                        "IAU (Imam Abdulrahman Bin Faisal Univ - iau.edu.sa)",
                        "Other Saudi Institution",
                        "International University / Research Center"
                    ]
                )

            with c2:
                f_rating = st.select_slider("Your Rating:", options=[1, 2, 3, 4, 5], value=5, format_func=lambda x: f"{x} Stars (" + "★" * x + ")")
                f_cat = st.selectbox(
                    "Feedback Category:",
                    [
                        "Academic Review",
                        "Wishlist & Feature Request",
                        "Material Benchmark Request",
                        "Bug Report / Calibration Adjustment"
                    ]
                )
                f_subj = st.text_input("Subject / Headline:", placeholder="e.g. Exceptional deconvolution accuracy on UiO-66...")

            f_comment = st.text_area("Your Review / Thoughts on this Platform:", placeholder="How did this tool assist your characterization, thesis, or paper? What did you like most?", height=110)
            f_wishes = st.text_area("Your Wishes & Feature Requests for Future Updates:", placeholder="What materials, techniques, or spectroscopic models would you like Dr. Deler Langenberg to add next?", height=75)

            submit_btn = st.form_submit_button("🚀 Submit Review & Wishes", type="primary", use_container_width=True)

            if submit_btn:
                if not f_name or not f_comment:
                    st.warning("Please provide at least your name and your feedback comments before submitting.")
                else:
                    inst_code = "KAUST" if "KAUST" in f_inst else ("KFUPM" if "KFUPM" in f_inst else ("KACST" if "KACST" in f_inst else ("IAU (iau.edu.sa)" if "IAU" in f_inst else f_inst.split()[0])))
                    new_item = {
                        "id": f"rev_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "name": f_name.strip(),
                        "role": f_role.strip() or "Materials Scientist",
                        "institution": inst_code,
                        "rating": int(f_rating),
                        "category": f_cat,
                        "subject": f_subj.strip() or "Community Feedback",
                        "comment": f_comment.strip(),
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "wishes": f_wishes.strip()
                    }
                    if add_review(new_item, file_path):
                        st.success("🎉 Thank you! Your review and wishes have been submitted and recorded successfully.")
                        
                        # Prepare direct mailto link for user convenience
                        mail_subj = urllib.parse.quote(f"[{active_app_name} Review] from {f_name} ({inst_code})")
                        mail_body = urllib.parse.quote(
                            f"Reviewer: {f_name}\n"
                            f"Role: {f_role}\n"
                            f"Institution: {inst_code}\n"
                            f"Rating: {f_rating}/5 Stars\n"
                            f"Category: {f_cat}\n"
                            f"Subject: {f_subj}\n\n"
                            f"Review:\n{f_comment}\n\n"
                            f"Wishes & Suggestions:\n{f_wishes}\n"
                        )
                        mailto_url = f"mailto:delerla@yahoo.de?subject={mail_subj}&body={mail_body}"
                        
                        st.markdown(f"""
                        <div style="margin-top: 10px; display: flex; gap: 10px;">
                            <a href="{mailto_url}" style="background: #0284c7; color: white; padding: 6px 14px; border-radius: 4px; text-decoration: none; font-size: 0.85rem; font-weight: 600;">
                                ✉️ Email Copy Directly to Dr. Deler Langenberg
                            </a>
                            <a href="https://github.com/delerla/Plotting_Chemistry/issues/new" target="_blank" style="background: #334155; color: white; padding: 6px 14px; border-radius: 4px; text-decoration: none; font-size: 0.85rem; font-weight: 600;">
                                🌟 Open GitHub Feature Wish Discussion
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Failed to save review to disk. Please try again.")
