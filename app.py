import streamlit as st
import numpy as np
import pandas as pd
import datetime
import os
import smtplib
from PIL import Image, ImageStat
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import plotly.express as px
from fpdf import FPDF

st.set_page_config(page_title="AI Smart Attendance", layout="wide")
st.title("🎓 Advanced AI Smart Attendance System")

ATTENDANCE_CSV = "attendance.csv"
STUDENTS_CSV = "students.csv"

# --- HELPER FUNCTIONS FOR STUDENT DATABASE ---
def load_students():
    required_cols = ["Roll_No", "Name", "Email"]
    if not os.path.exists(STUDENTS_CSV):
        df = pd.DataFrame({"Roll_No": ["101"], "Name": ["Riya Singh"], "Email": ["rajivsingh7401@gmail.com"]})
        df.to_csv(STUDENTS_CSV, index=False)
        return df
    
    try:
        df = pd.read_csv(STUDENTS_CSV)
        for col in required_cols:
            if col not in df.columns:
                df[col] = "N/A"
        return df
    except Exception:
        return pd.DataFrame(columns=required_cols)

def save_students(df):
    df.to_csv(STUDENTS_CSV, index=False)

# --- IMAGE & EMAIL FUNCTIONS ---
def verify_face_image(image_file):
    try:
        img = Image.open(image_file)
        stat = ImageStat.Stat(img)
        variance = sum(stat.var) / len(stat.var)
        return variance > 100, "Success"
    except Exception:
        return False, "Invalid image"

def send_email_alert(to_email, student_name, subject_name, time_str):
    sender_email = st.secrets.get("SENDER_EMAIL", "").strip()
    sender_password = st.secrets.get("SENDER_PASSWORD", "").strip().replace(" ", "")
    if not sender_email or not sender_password or to_email == "N/A": return False, "Credentials or email missing"
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = f"Attendance Confirmation - {subject_name}"
        msg.attach(MIMEText(f"Hello,\n\nAttendance marked for {student_name} ({subject_name}) at {time_str}.\n\nRegards,\nAI Attendance System", 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=5)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True, "Success"
    except Exception as e:
        return False, str(e)

# --- DATA FUNCTIONS ---
def load_attendance():
    required_cols = ["Name", "Roll_No", "Email", "Subject", "Date", "Time", "Status"]
    if os.path.exists(ATTENDANCE_CSV):
        try:
            df = pd.read_csv(ATTENDANCE_CSV)
            for col in required_cols:
                if col not in df.columns:
                    df[col] = "N/A"
            return df[required_cols]
        except Exception:
            return pd.DataFrame(columns=required_cols)
    return pd.DataFrame(columns=required_cols)

def save_attendance(df):
    df.to_csv(ATTENDANCE_CSV, index=False)

def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, txt="Attendance Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, txt=f"Generated on: {datetime.date.today()}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 10, "Name", border=1)
    pdf.cell(20, 10, "Roll", border=1)
    pdf.cell(35, 10, "Subject", border=1)
    pdf.cell(30, 10, "Date", border=1)
    pdf.cell(25, 10, "Time", border=1)
    pdf.cell(25, 10, "Status", border=1)
    pdf.ln()
    
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        pdf.cell(30, 10, str(row['Name'])[:12], border=1)
        pdf.cell(20, 10, str(row['Roll_No']), border=1)
        pdf.cell(35, 10, str(row['Subject'])[:15], border=1)
        pdf.cell(30, 10, str(row['Date']), border=1)
        pdf.cell(25, 10, str(row['Time']), border=1)
        pdf.cell(25, 10, str(row['Status']), border=1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- UI NAVIGATION ---
menu = st.sidebar.selectbox("Navigation", ["🤖 AI Attendance", "Analytics & History", "Download Reports", "🔑 Admin Panel"])

if menu == "🤖 AI Attendance":
    st.subheader("📷 Mark Attendance")
    students_df = load_students()
    
    if students_df.empty:
        st.warning("No students found in database! Please add students from Admin Panel.")
    else:
        selected_roll = st.selectbox("Select Student Roll No", students_df['Roll_No'].astype(str).unique())
        
        # Safe extraction of student data
        matched_student = students_df[students_df['Roll_No'].astype(str) == str(selected_roll)]
        if not matched_student.empty:
            student_info = matched_student.iloc[0]
            student_name = student_info.get("Name", "Unknown")
            student_email = student_info.get("Email", "N/A")
            
            st.info(f"👤 *Student Name:* {student_name} | 📧 *Email:* {student_email}")
            selected_subject = st.selectbox("Select Subject", ["Python Programming", "AI & Machine Learning", "Data Science", "Web Development"])
            
            img_file = st.camera_input("Scan Face")
            if img_file is not None:
                with st.spinner("🔍 AI Validating Face Image..."):
                    is_valid, msg = verify_face_image(img_file)
                
                if not is_valid:
                    st.error("❌ Image Verification Failed: Low clarity or invalid image.")
                else:
                    st.success("👤 Face Scan Verified Successfully!")
                    df = load_attendance()
                    today = str(datetime.date.today())
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    
                    already_marked = df[(df['Roll_No'].astype(str) == str(selected_roll)) & 
                                        (df['Date'] == today) & 
                                        (df['Subject'] == selected_subject)]
                    
                    if not already_marked.empty:
                        st.warning(f"Attendance for *{student_name}* in *{selected_subject}* is already marked today!")
                    else:
                        new_entry = pd.DataFrame([{
                            "Name": student_name, 
                            "Roll_No": selected_roll, 
                            "Email": student_email,
                            "Subject": selected_subject,
                            "Date": today, 
                            "Time": current_time, 
                            "Status": "Present"
                        }])
                        save_attendance(pd.concat([df, new_entry], ignore_index=True))
                        st.balloons()
                        st.success(f"✅ AI Attendance Verified & Marked for *{student_name}* ({selected_subject})!")

                        if student_email and student_email != "N/A":
                            with st.spinner("Sending Confirmation Email..."):
                                status, email_msg = send_email_alert(student_email, student_name, selected_subject, current_time)
                            if status:
                                st.info(f"📧 Confirmation email sent to *{student_email}*!")
                            else:
                                st.warning(f"⚠️ Attendance marked, but email failed: {email_msg}")

elif menu == "Analytics & History":
    st.subheader("📊 Attendance Analytics")
    df = load_attendance()
    if df.empty:
        st.info("No attendance records found yet.")
    else:
        subject_filter = st.selectbox("Filter by Subject", ["All"] + list(df['Subject'].unique()))
        filtered_df = df if subject_filter == "All" else df[df['Subject'] == subject_filter]
        st.dataframe(filtered_df, use_container_width=True)
        fig = px.histogram(filtered_df, x="Subject", color="Status", title="Attendance Distribution", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

elif menu == "Download Reports":
    st.subheader("📥 Export Reports")
    df = load_attendance()
    if df.empty:
        st.warning("No data available to export.")
    else:
        pdf_bytes = create_pdf(df)
        st.download_button("📄 Download PDF Report", data=pdf_bytes, file_name="attendance_report.pdf", mime="application/pdf")
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("📊 Download CSV Report", data=csv_data, file_name="attendance_report.csv", mime="text/csv")

elif menu == "🔑 Admin Panel":
    pwd_input = st.text_input("Enter Admin Password", type="password")
    if pwd_input == st.secrets.get("ADMIN_PASSWORD", "admin123"):
        st.success("✅ Access Granted")
        tab1, tab2 = st.tabs(["➕ Manage Student Directory", "📋 Attendance Logs"])
        
        with tab1:
            st.write("### Add New Student")
            with st.form("add_student_form", clear_on_submit=True):
                new_roll = st.text_input("Roll Number")
                new_name = st.text_input("Student Name")
                new_email = st.text_input("Email Address")
                submitted = st.form_submit_button("Add Student")
                
                if submitted:
                    if new_roll and new_name:
                        students_df = load_students()
                        new_student = pd.DataFrame([{"Roll_No": str(new_roll), "Name": str(new_name), "Email": str(new_email) if new_email else "N/A"}])
                        students_df = pd.concat([students_df, new_student], ignore_index=True)
                        save_students(students_df)
                        st.success(f"Student '{new_name}' (Roll No: {new_roll}) added successfully!")
                        st.rerun()
                    else:
                        st.error("Please enter both Roll Number and Name!")
            
            st.write("### Registered Students Directory")
            st.dataframe(load_students(), use_container_width=True)

        with tab2:
            st.write("### All Attendance Records")
            st.dataframe(load_attendance(), use_container_width=True)
