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
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=["Name", "Roll_No", "Date", "Time", "Status"])

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
    if img_file:
        df = load_data()
        today = str(datetime.date.today())
        # Check duplicate
        if not df[(df['Roll_No'] == str(roll_no)) & (df['Date'] == today)].empty:
            st.warning("Already marked today!")
        else:
            new_entry = pd.DataFrame([{"Name": student_name, "Roll_No": roll_no, "Date": today, "Time": datetime.datetime.now().strftime("%H:%M:%S"), "Status": "Present"}])
            pd.concat([df, new_entry], ignore_index=True).to_csv(CSV_FILE, index=False)
            st.success(f"Marked for {student_name}!")

elif menu == "Analytics & History":
    st.subheader("📊 Analytics & Percentage")
    df = load_data()
    if not df.empty:
        # Percentage Calculation
        total_days = df['Date'].nunique()
        student_stats = df.groupby('Name').size().reset_index(name='Days_Present')
        student_stats['Percentage'] = (student_stats['Days_Present'] / total_days * 100).round(2)
        
        st.write("### Student Attendance Percentage")
        st.table(student_stats)
        
        fig = px.bar(student_stats, x='Name', y='Percentage', title="Attendance % by Student", color='Percentage')
        st.plotly_chart(fig, use_container_width=True)

elif menu == "Download Reports":
    st.subheader("📥 Export Reports")
    df = load_data()
    if not df.empty:
        # PDF Button
        pdf_bytes = create_pdf(df)
        st.download_button("📄 Download Report as PDF", data=pdf_bytes, file_name="report.pdf", mime="application/pdf")
        
        # CSV Button
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("📊 Download Report as CSV", data=csv_data, file_name="report.csv", mime="text/csv")
            
