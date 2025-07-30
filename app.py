# import streamlit as st
# import pandas as pd
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# # ------------------ CONFIG ------------------
# GOOGLE_SHEET_NAME = "Electrical Coating Data"
# WORKSHEET_NAMES = {
#     "Anti Fog": "Anti Fog",
#     "Dip Coat": "Dip Coat",  # ✅ Updated from "Deep Coat"
#     "Hard Coat": "Hard Coat"
# }

# # ------------------ GOOGLE AUTH ------------------
# scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
# client = gspread.authorize(creds)

# # ------------------ PAGE SETUP ------------------
# st.set_page_config(page_title="Electrical Data Viewer", layout="wide")
# st.markdown("<h1 style='text-align: center;'>⚡ Electrical Data Viewer</h1>", unsafe_allow_html=True)
# st.markdown("---")

# # ------------------ SESSION STATE ------------------
# if "clicked_button" not in st.session_state:
#     st.session_state.clicked_button = None

# col1, col2, col3 = st.columns(3)
# with col1:
#     if st.button("Anti Fog"):
#         st.session_state.clicked_button = "Anti Fog"
# with col2:
#     if st.button("Dip Coat"):  # ✅ Updated from "Deep Coat"
#         st.session_state.clicked_button = "Dip Coat"
# with col3:
#     if st.button("Hard Coat"):
#         st.session_state.clicked_button = "Hard Coat"

# clicked_button = st.session_state.clicked_button

# # ------------------ MAIN LOGIC ------------------
# if clicked_button:
#     st.success(f"{clicked_button} selected")

#     try:
#         worksheet_name = WORKSHEET_NAMES[clicked_button]
#         sheet = client.open(GOOGLE_SHEET_NAME).worksheet(worksheet_name)
#         data = sheet.get_all_records()

#         if not data:
#             st.warning("⚠️ This sheet is currently empty. Please add headers and at least one row in Google Sheets.")
#         else:
#             df = pd.DataFrame(data)

#             # ✅ Convert all values to editable strings
#             for col in df.columns:
#                 df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else "")

#             st.markdown(f"### ✏️ Edit '{clicked_button}' Data (Live from Google Sheets)")
#             edited_df = st.data_editor(
#                 df,
#                 use_container_width=True,
#                 hide_index=True,
#                 num_rows="dynamic"
#             )

#             if st.button("💾 Save Changes to Google Sheets"):
#                 try:
#                     # Clear existing data and update with edited data
#                     sheet.clear()
#                     sheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
#                     st.success(f"✅ Successfully saved to '{worksheet_name}' tab in Google Sheets.")
#                 except Exception as e:
#                     st.error(f"❌ Failed to save: {e}")
#     except Exception as e:
#         st.error(f"❌ Could not load data from Google Sheets: {e}")
# else:
#     st.info("👆 Select a category to view and edit its data.")

import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------ CONFIG ------------------
GOOGLE_SHEET_NAME = "Electrical Coating Data"
WORKSHEET_NAMES = {
    "Anti Fog": "Anti Fog",
    "Dip Coat": "Dip Coat",  # Renamed from Deep Coat
    "Hard Coat": "Hard Coat"
}

CHECKLIST_SHEETS = {
    "Anti Fog": "Anti_Fog_Checklist",
    "Dip Coat": "Dip_Coat_Checklist",
    "Hard Coat": "Hard_Coat_Checklist"
}

# ------------------ GOOGLE AUTH ------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="Electrical Data Viewer", layout="wide")
st.markdown("<h1 style='text-align: center;'>⚡ Electrical Data Viewer</h1>", unsafe_allow_html=True)
st.markdown("---")

# ------------------ SESSION STATE ------------------
if "clicked_button" not in st.session_state:
    st.session_state.clicked_button = None

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Anti Fog"):
        st.session_state.clicked_button = "Anti Fog"
with col2:
    if st.button("Dip Coat"):
        st.session_state.clicked_button = "Dip Coat"
with col3:
    if st.button("Hard Coat"):
        st.session_state.clicked_button = "Hard Coat"

clicked_button = st.session_state.clicked_button

# ------------------ MAIN LOGIC ------------------
if clicked_button:
    st.success(f"{clicked_button} selected")

    tabs = st.tabs(["📄 Data", "📋 Checklist"])

    # -------- Tab 1: Data --------
    with tabs[0]:
        try:
            worksheet_name = WORKSHEET_NAMES[clicked_button]
            sheet = client.open(GOOGLE_SHEET_NAME).worksheet(worksheet_name)
            data = sheet.get_all_records()

            if not data:
                st.warning("⚠️ This sheet is currently empty. Please add headers and at least one row in Google Sheets.")
            else:
                df = pd.DataFrame(data)
                for col in df.columns:
                    df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else "")

                st.markdown(f"### ✏️ Edit '{clicked_button}' Data")
                edited_df = st.data_editor(df, use_container_width=True, hide_index=True, num_rows="dynamic")

                if st.button("💾 Save Changes to Google Sheets", key=f"save_data_{clicked_button}"):
                    try:
                        sheet.clear()
                        sheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
                        st.success(f"✅ Successfully saved to '{worksheet_name}' tab.")
                    except Exception as e:
                        st.error(f"❌ Failed to save: {e}")

        except Exception as e:
            st.error(f"❌ Could not load data: {e}")

    # -------- Tab 2: Checklist --------
    with tabs[1]:
        try:
            checklist_sheet_name = CHECKLIST_SHEETS[clicked_button]
            checklist_sheet = client.open(GOOGLE_SHEET_NAME).worksheet(checklist_sheet_name)
            raw_values = checklist_sheet.get_all_values()

            if not raw_values:
                st.warning("⚠️ Checklist sheet is empty.")
            else:
                max_len = max(len(row) for row in raw_values)
                normalized_rows = []
                for row in raw_values:
                    if any(cell.strip() != "" for cell in row):
                        normalized = row + ["" for _ in range(max_len - len(row))]
                        normalized_rows.append(normalized)
                    else:
                        normalized_rows.append(["" for _ in range(max_len)])

                checklist_df = pd.DataFrame(normalized_rows)
                st.markdown(f"### ✅ Edit '{clicked_button}' Checklist")
                edited_checklist_df = st.data_editor(
                    checklist_df,
                    use_container_width=True,
                    hide_index=True,
                    num_rows="dynamic"
                )

                if st.button("💾 Save Checklist to Google Sheets", key=f"save_checklist_{clicked_button}"):
                    try:
                        checklist_sheet.clear()
                        checklist_sheet.update(edited_checklist_df.values.tolist())
                        st.success(f"✅ Checklist saved to '{checklist_sheet_name}' tab.")
                    except Exception as e:
                        st.error(f"❌ Failed to save checklist: {e}")

        except Exception as e:
            st.error(f"❌ Could not load checklist: {e}")
else:
    st.info("👆 Select a category to view and edit its data.")



