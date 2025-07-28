# import streamlit as st
# import pandas as pd
# from io import BytesIO

# # Set page config
# st.set_page_config(page_title="Electrical Data Viewer", layout="wide")

# st.markdown("<h1 style='text-align: center;'>⚡ Electrical Data Viewer</h1>", unsafe_allow_html=True)
# st.markdown("---")

# # Excel file paths
# files = {
#     "Anti Fog": "anti_fog.xlsx",
#     "Deep Coat": "deep_coat.xlsx",
#     "Hard Coat": "hard_coat.xlsx"
# }

# # Function to detect the first valid header row
# def find_first_non_empty_row(path):
#     preview = pd.read_excel(path, header=None, nrows=5)
#     for i, row in preview.iterrows():
#         if row.notna().sum() > 2:
#             return i
#     return 0

# # Layout for buttons
# col1, col2, col3 = st.columns(3)
# clicked_button = None

# with col1:
#     if st.button("Anti Fog"):
#         clicked_button = "Anti Fog"

# with col2:
#     if st.button("Deep Coat"):
#         clicked_button = "Deep Coat"

# with col3:
#     if st.button("Hard Coat"):
#         clicked_button = "Hard Coat"

# # On button click
# if clicked_button:
#     st.success(f"{clicked_button} button is clicked")

#     try:
#         # Load Excel
#         header_row = find_first_non_empty_row(files[clicked_button])
#         df = pd.read_excel(files[clicked_button], header=header_row)

#         # Drop fully empty rows
#         df_cleaned = df.dropna(how='all').reset_index(drop=True)

#         # Convert Sr. No. to integer if numeric
#         for col in df_cleaned.columns:
#             col_lower = col.strip().lower()
#             if col_lower in ["sr no", "sr. no", "srno", "s.no", "serial no"]:
#                 if pd.api.types.is_numeric_dtype(df_cleaned[col]):
#                     df_cleaned[col] = df_cleaned[col].astype(pd.Int64Dtype())  # Nullable integer

#         # For display: format Sr. No column without .0
#         df_display = df_cleaned.copy()
#         for col in df_display.columns:
#             col_lower = col.strip().lower()
#             if col_lower in ["sr no", "sr. no", "srno", "s.no", "serial no"]:
#                 df_display[col] = df_display[col].apply(lambda x: str(int(x)) if pd.notna(x) else "")
#             else:
#                 df_display[col] = df_display[col].astype(str).replace("nan", "")

#         # Show table (hide index)
#         st.markdown(f"### 📊 {clicked_button} Sheet (Excel-Like View)")
#         st.dataframe(df_display, use_container_width=True, hide_index=True)

#         # Prepare download
#         def to_excel(df):
#             output = BytesIO()
#             with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#                 df.to_excel(writer, index=False)
#             return output.getvalue()

#         st.download_button(
#             label="📥 Download Excel File",
#             data=to_excel(df_cleaned),
#             file_name=f"{clicked_button.lower().replace(' ', '_')}_cleaned.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )

#     except FileNotFoundError:
#         st.error(f"⚠️ File for {clicked_button} not found.")
#     except Exception as e:
#         st.error(f"❌ Error loading file: {e}")

import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------ CONFIG ------------------
GOOGLE_SHEET_NAME = "Electrical Coating Data"
WORKSHEET_NAMES = {
    "Anti Fog": "Anti Fog",
    "Deep Coat": "Deep Coat",
    "Hard Coat": "Hard Coat"
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
    if st.button("Deep Coat"):
        st.session_state.clicked_button = "Deep Coat"
with col3:
    if st.button("Hard Coat"):
        st.session_state.clicked_button = "Hard Coat"

clicked_button = st.session_state.clicked_button

# ------------------ MAIN LOGIC ------------------
if clicked_button:
    st.success(f"{clicked_button} selected")

    try:
        # Fetch sheet
        worksheet_name = WORKSHEET_NAMES[clicked_button]
        sheet = client.open(GOOGLE_SHEET_NAME).worksheet(worksheet_name)
        records = sheet.get_all_records()
        df = pd.DataFrame(records)

        # Show and edit
        st.markdown(f"### ✏️ Edit '{clicked_button}' Data (Live from Google Sheets)")
        edited_df = st.data_editor(df, use_container_width=True, hide_index=True, num_rows="dynamic")

        if st.button("💾 Save Changes to Google Sheets"):
            try:
                sheet.clear()
                sheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
                st.success(f"✅ Successfully saved to '{worksheet_name}' tab in Google Sheets.")
            except Exception as e:
                st.error(f"❌ Failed to save: {e}")

    except Exception as e:
        st.error(f"❌ Could not load data from Google Sheets: {e}")
else:
    st.info("👆 Select a category to view and edit its data.")

