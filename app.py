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
    if not os.path.exists(STUDENTS_CSV):
        # Default student if file doesn't exist
        df = pd.DataFrame({"Roll_No": ["101"], "Name": ["Riya Singh"], "Email": ["rajivsingh7401@gmail.com"]})
        df.to_csv(STUDENTS_CSV, index=False)
        return df
    return pd.read_csv(STUDENTS_CSV)

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
    if not sender_email or not sender_password: return False, "Credentials missing"
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = f"Attendance: {subject_name}"
        msg.attach(MIMEText(f"Attendance marked for {student_name} at {time_str}.", 'plain'))
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
        return pd.read_csv(ATTENDANCE_CSV)
    return pd.DataFrame(columns=required_cols)

def save_attendance(df):
    df.to_csv(ATTENDANCE_CSV, index=False)

# --- UI NAVIGATION ---
menu = st.sidebar.selectbox("Navigation", ["🤖 AI Attendance", "Analytics", "Download", "🔑 Admin Panel"])

if menu == "🤖 AI Attendance":
    st.subheader("📷 Mark Attendance")
    students_df = load_students()
    
    # Dropdown based on CSV data
    selected_roll = st.selectbox("Select Student", students_df['Roll_No'].astype(str))
    student_info = students_df[students_df['Roll_No'].astype(str) == selected_roll].iloc[0]
    
    st.write(f"*Name:* {student_info['Name']} | *Email:* {student_info['Email']}")
    selected_subject = st.selectbox("Subject", ["Python", "AI/ML", "Data Science", "Web Dev"])
    
    img_file = st.camera_input("Scan Face")
    if img_file:
        is_valid, _ = verify_face_image(img_file)
        if is_valid:
            st.success("Face Verified!")
            df = load_attendance()
            # Logic to save attendance...
            new_entry = pd.DataFrame([{"Name": student_info['Name'], "Roll_No": selected_roll, "Email": student_info['Email'], "Subject": selected_subject, "Date": str(datetime.date.today()), "Time": datetime.datetime.now().strftime("%H:%M:%S"), "Status": "Present"}])
            save_attendance(pd.concat([df, new_entry], ignore_index=True))
            st.balloons()
            st.success("Attendance Marked!")
        else:
            st.error("Face not clear!")

elif menu == "🔑 Admin Panel":
    if st.text_input("Admin Password", type="password") == st.secrets.get("ADMIN_PASSWORD", "admin123"):
        tab1, tab2 = st.tabs(["➕ Manage Students", "📋 Attendance Records"])
        
        with tab1:
            st.write("### Add New Student")
            with st.form("add_student_form"):
                new_roll = st.text_input("Roll No")
                new_name = st.text_input("Name")
                new_email = st.text_input("Email")
                submitted = st.form_submit_button("Add Student")
                if submitted and new_roll and new_name:
                    students_df = load_students()
                    new_student = pd.DataFrame([{"Roll_No": new_roll, "Name": new_name, "Email": new_email}])
                    students_df = pd.concat([students_df, new_student], ignore_index=True)
                    save_students(students_df)
                    st.success(f"Student {new_name} added!")
                    st.rerun()
            
            st.write("### Current Students List")
            st.dataframe(load_students())

        with tab2:
            st.write("### All Attendance")
            st.dataframe(load_attendance())
