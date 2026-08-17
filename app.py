import streamlit as st
import cv2
import numpy as np
import pandas as pd
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import plotly.express as px
from fpdf import FPDF

st.set_page_config(page_title="AI Smart Attendance", layout="wide")
st.title("🎓 Advanced AI Smart Attendance System")

CSV_FILE = "attendance.csv"

# Function to Send Email Notification with TIMEOUT (Fast Execution)
def send_email_alert(to_email, student_name, time_str):
    sender_email = st.secrets.get("SENDER_EMAIL", "").strip()
    sender_password = st.secrets.get("SENDER_PASSWORD", "").strip().replace(" ", "")

    if not sender_email or not sender_password:
        return False, "Email credentials missing in Streamlit Secrets."

    try:
        subject = "Attendance Confirmation Alert"
        body = f"Hello,\n\nAttendance for {student_name} has been successfully marked today at {time_str}.\n\nRegards,\nAI Attendance System"
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Set 5-second timeout so app doesn't hang
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=5)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Email failed: {str(e)}"

def load_data():
    required_cols = ["Name", "Roll_No", "Email", "Date", "Time", "Status"]
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            for col in required_cols:
                if col not in df.columns:
                    df[col] = "N/A"
            return df[required_cols]
        except Exception:
            return pd.DataFrame(columns=required_cols)
    else:
        return pd.DataFrame(columns=required_cols)

def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Attendance Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Generated on: {datetime.date.today()}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(40, 10, "Name", border=1)
    pdf.cell(30, 10, "Roll", border=1)
    pdf.cell(40, 10, "Date", border=1)
    pdf.cell(40, 10, "Status", border=1)
    pdf.ln()
    
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
    col_a, col_b, col_c = st.columns(3)
    student_name = col_a.text_input("Student Name", value="Student_1")
    roll_no = col_b.text_input("Roll Number", value="101")
    user_email = col_c.text_input("Email ID (for alerts)", value="")
    
    img_file = st.camera_input("Take a photo")
    if img_file is not None:
        df = load_data()
        today = str(datetime.date.today())
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        already_marked = df[(df['Roll_No'].astype(str) == str(roll_no)) & (df['Date'] == today)]
        
        if not already_marked.empty:
            st.warning(f"Attendance for *{student_name}* (Roll: {roll_no}) is already marked today!")
        else:
            # 1. Save Attendance First
            new_entry = pd.DataFrame([{
                "Name": student_name, 
                "Roll_No": roll_no, 
                "Email": user_email,
                "Date": today, 
                "Time": current_time, 
                "Status": "Present"
            }])
            df_updated = pd.concat([df, new_entry], ignore_index=True)
            df_updated.to_csv(CSV_FILE, index=False)
            st.balloons()
            st.success(f"✅ Marked attendance for *{student_name}* (Roll: {roll_no})!")

            # 2. Try Sending Email (Fast)
            if user_email:
                with st.spinner("Sending Email Alert..."):
                    status, msg = send_email_alert(user_email, student_name, current_time)
                if status:
                    st.info(f"📧 Confirmation email sent to *{user_email}*!")
                else:
                    st.warning(f"⚠️ Attendance marked, but email failed: {msg}")

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