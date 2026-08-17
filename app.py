import streamlit as st
import cv2
import numpy as np
import pandas as pd
import datetime
import os
import plotly.express as px
from fpdf import FPDF

st.set_page_config(page_title="AI Smart Attendance", layout="wide")
st.title("🎓 Advanced AI Smart Attendance System")

CSV_FILE = "attendance.csv"

def load_data():
    required_cols = ["Name", "Roll_No", "Date", "Time", "Status"]
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            # Ensure all required columns exist
            for col in required_cols:
                if col not in df.columns:
                    df[col] = "N/A"
            return df[required_cols]
        except Exception:
            return pd.DataFrame(columns=required_cols)
    else:
        return pd.DataFrame(columns=required_cols)

# PDF Generation Function
def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Attendance Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Generated on: {datetime.date.today()}", ln=True, align='C')
    pdf.ln(10)
    
    # Table Header
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, "Name", border=1)
    pdf.cell(30, 10, "Roll", border=1)
    pdf.cell(40, 10, "Date", border=1)
    pdf.cell(40, 10, "Status", border=1)
    pdf.ln()
    
    # Table Rows
    pdf.set_font("Arial", size=12)
    for _, row in df.iterrows():
        pdf.cell(40, 10, str(row['Name']), border=1)
        pdf.cell(30, 10, str(row['Roll_No']), border=1)
        pdf.cell(40, 10, str(row['Date']), border=1)
        pdf.cell(40, 10, str(row['Status']), border=1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

menu = st.sidebar.selectbox("Navigation", ["Mark Attendance", "Analytics & History", "Download Reports"])

if menu == "Mark Attendance":
    st.subheader("📷 Live Camera Attendance")
    col_a, col_b = st.columns(2)
    student_name = col_a.text_input("Enter Student Name", value="Student_1")
    roll_no = col_b.text_input("Enter Roll Number", value="101")
    
    img_file = st.camera_input("Take a photo")
    if img_file is not None:
        df = load_data()
        today = str(datetime.date.today())
        
        # Check duplicate safely
        already_marked = df[(df['Roll_No'].astype(str) == str(roll_no)) & (df['Date'] == today)]
        
        if not already_marked.empty:
            st.warning(f"Attendance for **{student_name}** (Roll: {roll_no}) is already marked today!")
        else:
            new_entry = pd.DataFrame([{
                "Name": student_name, 
                "Roll_No": roll_no, 
                "Date": today, 
                "Time": datetime.datetime.now().strftime("%H:%M:%S"), 
                "Status": "Present"
            }])
            df_updated = pd.concat([df, new_entry], ignore_index=True)
            df_updated.to_csv(CSV_FILE, index=False)
            st.balloons()
            st.success(f"Marked attendance for **{student_name}** (Roll: {roll_no})!")

elif menu == "Analytics & History":
    st.subheader("📊 Analytics & Percentage")
    df = load_data()
    if df.empty:
        st.info("No attendance records found yet.")
    else:
        total_days = df['Date'].nunique()
        student_stats = df.groupby(['Name', 'Roll_No']).size().reset_index(name='Days_Present')
        student_stats['Percentage (%)'] = ((student_stats['Days_Present'] / total_days) * 100).round(2)
        
        st.write("### Student Attendance Percentage")
        st.dataframe(student_stats, use_container_width=True)
        
        fig = px.bar(student_stats, x='Name', y='Percentage (%)', title="Attendance % by Student", color='Percentage (%)')
        st.plotly_chart(fig, use_container_width=True)

elif menu == "Download Reports":
    st.subheader("📥 Export Reports")
    df = load_data()
    if df.empty:
        st.warning("No data available to export.")
    else:
        pdf_bytes = create_pdf(df)
        st.download_button("📄 Download Report as PDF", data=pdf_bytes, file_name="report.pdf", mime="application/pdf")
        
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("📊 Download Report as CSV", data=csv_data, file_name="report.csv", mime="text/csv")
        
