import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Competition Judging App", layout="wide")

# --------------------------------
# Session State Initialization
# --------------------------------
if "participants" not in st.session_state:
    st.session_state.participants = []

if "evaluations" not in st.session_state:
    st.session_state.evaluations = []

# --------------------------------
# App Title
# --------------------------------
st.title("🏆 Competition Judging & Evaluation System")

# --------------------------------
# Tabs
# --------------------------------
tab1, tab2, tab3 = st.tabs(
    [
        "👥 Participant Information",
        "📝 Evaluation",
        "📊 Results & Analytics",
    ]
)

# ======================================================
# TAB 1: Participant Teams Information Collection
# ======================================================
with tab1:
    st.header("1️⃣ Participant Team Information")

    with st.form("participant_form"):
        team_name = st.text_input("Team Name")
        team_size = st.number_input("Team Size", min_value=1, max_value=20, step=1)

        description_mode = st.radio(
            "Project description mode",
            ["Text", "Audio Upload"],
            horizontal=True,
        )

        description_text = ""
        if description_mode == "Text":
            description_text = st.text_area("Project Description", height=120)
        else:
            st.file_uploader("Upload audio (MP3/WAV)", type=["mp3", "wav"])

        submitted = st.form_submit_button("Add Team")

        if submitted:
            if not team_name:
                st.error("Team name is required.")
            else:
                st.session_state.participants.append(
                    {
                        "Team Name": team_name,
                        "Team Size": team_size,
                        "Description": description_text
                        if description_mode == "Text"
                        else "Audio Submitted",
                    }
                )
                st.success(f"Team **{team_name}** added!")

    if st.session_state.participants:
        st.subheader("📋 Registered Teams")
        st.dataframe(
            pd.DataFrame(st.session_state.participants),
            use_container_width=True,
        )

# ======================================================
# TAB 2: Evaluation
# ======================================================
with tab2:
    st.header("2️⃣ Judge Evaluation")

    if not st.session_state.participants:
        st.warning("Add participant teams first.")
    else:
        teams = [p["Team Name"] for p in st.session_state.participants]

        with st.form("evaluation_form"):
            selected_team = st.selectbox("Select Team", teams)

            novelty = st.radio("Novelty", [1, 2, 3, 4, 5], horizontal=True)
            scalability = st.radio("Scalability", [1, 2, 3, 4, 5], horizontal=True)
            social_impact = st.radio("Social Impact", [1, 2, 3, 4, 5], horizontal=True)
            feasibility = st.radio("Feasibility", [1, 2, 3, 4, 5], horizontal=True)

            submit_eval = st.form_submit_button("Submit Evaluation")

            if submit_eval:
                st.session_state.evaluations.append(
                    {
                        "Team Name": selected_team,
                        "Novelty": novelty,
                        "Scalability": scalability,
                        "Social Impact": social_impact,
                        "Feasibility": feasibility,
                    }
                )
                st.success(f"Evaluation saved for **{selected_team}**")

# ======================================================
# TAB 3: Results / Charts / Export
# ======================================================
with tab3:
    st.header("3️⃣ Results & Analytics")

    if not st.session_state.evaluations:
        st.info("No evaluations available yet.")
    else:
        df = pd.DataFrame(st.session_state.evaluations)

        # Weights
        weights = {
            "Novelty": 0.30,
            "Scalability": 0.25,
            "Social Impact": 0.25,
            "Feasibility": 0.20,
        }

        df["Total Score"] = (
            df["Novelty"] * weights["Novelty"]
            + df["Scalability"] * weights["Scalability"]
            + df["Social Impact"] * weights["Social Impact"]
            + df["Feasibility"] * weights["Feasibility"]
        )

        summary = df.groupby("Team Name").mean().reset_index()

        st.subheader("📋 Final Scores")
        st.dataframe(summary, use_container_width=True)

        # -------------------------
        # Bar Chart
        # -------------------------
        fig, ax = plt.subplots()
        ax.bar(summary["Team Name"], summary["Total Score"])
        ax.set_ylim(0, 5)
        ax.set_ylabel("Score")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # ======================================================
        # EXPORT SECTION
        # ======================================================
        st.subheader("⬇️ Export Results")

        col1, col2 = st.columns(2)

        # ---------- Excel Export ----------
        with col1:
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Raw Evaluations", index=False)
                summary.to_excel(writer, sheet_name="Final Scores", index=False)

            st.download_button(
                label="📥 Download Excel Report",
                data=excel_buffer.getvalue(),
                file_name="competition_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        # ---------- PDF Export ----------
        with col2:
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            width, height = A4

            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Competition Results Summary")

            c.setFont("Helvetica", 11)
            y = height - 100

            for _, row in summary.iterrows():
                text = (
                    f"{row['Team Name']} | "
                    f"Score: {row['Total Score']:.2f}"
                )
                c.drawString(50, y, text)
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50

            c.save()

            st.download_button(
                label="📄 Download PDF Summary",
                data=pdf_buffer.getvalue(),
                file_name="competition_results.pdf",
                mime="application/pdf",
            )
