import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import gspread
from google.oauth2.service_account import Credentials

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(page_title="Capstone Mela - PESU - Judging App", layout="wide")

# -------------------------------------------------
# Google Sheets Helpers
# -------------------------------------------------
@st.cache_resource
def get_gsheet_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    return gspread.authorize(creds)


def get_worksheet(sheet_name):
    client = get_gsheet_client()
    sheet = client.open_by_key(
        st.secrets["google_sheets"]["spreadsheet_id"]
    )
    return sheet.worksheet(sheet_name)

# -------------------------------------------------
# Load data on startup
# -------------------------------------------------
if "participants" not in st.session_state:
    try:
        st.session_state.participants = get_worksheet("participants").get_all_records()
    except Exception:
        st.session_state.participants = []

if "evaluations" not in st.session_state:
    try:
        st.session_state.evaluations = get_worksheet("evaluations").get_all_records()
    except Exception:
        st.session_state.evaluations = []

# -------------------------------------------------
# App Title & Tabs
# -------------------------------------------------
st.title("🏆 Competition Judging & Evaluation System")

tab1, tab2, tab3 = st.tabs(
    ["👥 Participant Information", "📝 Evaluation", "📊 Results & Export"]
)

# =================================================
# TAB 1 — PARTICIPANTS
# =================================================
with tab1:
    st.header("1️⃣ Participant Team Information")

    with st.form("participant_form"):
        team_name = st.text_input("Team Name")
        team_size = st.number_input("Team Size", 1, 20, 1)
        description = st.text_area("Project Description", height=120)

        submitted = st.form_submit_button("Add Team")

        if submitted:
            if not team_name:
                st.error("Team name is required.")
            else:
                participant = {
                    "Team Name": team_name,
                    "Team Size": team_size,
                    "Description": description,
                }

                st.session_state.participants.append(participant)
                get_worksheet("participants").append_row(list(participant.values()))
                st.success(f"Team **{team_name}** added successfully!")

    if st.session_state.participants:
        st.subheader("📋 Registered Teams")
        st.dataframe(
            pd.DataFrame(st.session_state.participants),
            use_container_width=True,
        )

# =================================================
# TAB 2 — EVALUATION
# =================================================
with tab2:
    st.header("2️⃣ Judge Evaluation")

    if not st.session_state.participants:
        st.warning("Please add teams first.")
    else:
        teams = [p["Team Name"] for p in st.session_state.participants]

        with st.form("evaluation_form"):
            team = st.selectbox("Select Team", teams)

            novelty = st.radio("Creativity & Innovation", [1, 2, 3, 4, 5], horizontal=True)
            scalability = st.radio("Technical Complexity", [1, 2, 3, 4, 5], horizontal=True)
            impact = st.radio("Use Cases", [1, 2, 3, 4, 5], horizontal=True)
            feasibility = st.radio("Impact on Society/Industry/Research", [1, 2, 3, 4, 5], horizontal=True)

            submit_eval = st.form_submit_button("Submit Evaluation")

            if submit_eval:
                evaluation = {
                    "Team Name": team,
                    "Novelty": novelty,
                    "Scalability": scalability,
                    "Social Impact": impact,
                    "Feasibility": feasibility,
                }

                st.session_state.evaluations.append(evaluation)
                get_worksheet("evaluations").append_row(list(evaluation.values()))
                st.success(f"Evaluation submitted for **{team}**")

# =================================================
# TAB 3 — RESULTS & EXPORT
# =================================================
with tab3:
    st.header("3️⃣ Results & Analytics")

    if not st.session_state.evaluations:
        st.info("No evaluations available yet.")
    else:
        df = pd.DataFrame(st.session_state.evaluations)

        weights = {
            "Novelty": 1.00,
            "Scalability": 1.00,
            "Social Impact": 1.00,
            "Feasibility": 1.00,
        }

        df["Total Score"] = sum(df[c] * w for c, w in weights.items())
        summary = df.groupby("Team Name").mean().reset_index()

        st.subheader("📋 Final Scores")
        st.dataframe(summary, use_container_width=True)

        # -------------------------
        # Bar Chart
        # -------------------------
        fig, ax = plt.subplots()
        ax.bar(summary["Team Name"], summary["Total Score"], color="cornflowerblue")
        ax.set_ylim(0, 5)
        ax.set_ylabel("Score")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # -------------------------
        # EXPORT SECTION
        # -------------------------
        st.subheader("⬇️ Export Results")

        col1, col2 = st.columns(2)

        # Excel
        with col1:
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Raw Evaluations", index=False)
                summary.to_excel(writer, sheet_name="Final Scores", index=False)

            st.download_button(
                "📥 Download Excel",
                excel_buffer.getvalue(),
                "competition_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        # PDF
        with col2:
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            width, height = A4

            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Competition Results Summary")

            c.setFont("Helvetica", 11)
            y = height - 100

            for _, row in summary.iterrows():
                c.drawString(
                    50,
                    y,
                    f"{row['Team Name']} — Score: {row['Total Score']:.2f}",
                )
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50

            c.save()

            st.download_button(
                "📄 Download PDF",
                pdf_buffer.getvalue(),
                "competition_results.pdf",
                mime="application/pdf",
            )
