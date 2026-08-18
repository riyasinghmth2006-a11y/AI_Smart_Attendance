import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fpdf import FPDF

# --- Configuration ---
st.set_page_config(
    page_title="AI Smart Attendance System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Light Theme Styling ---
st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF;
        color: #1E293B;
    }
    div[data-baseweb="input"] > div {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }
    input {
        color: #0F172A !important;
    }
    label, p, h1, h2, h3, h4, h5, h6, span {
        color: #0F172A !important;
    }
    .stButton>button {
        background-color: #0284C7;
        color: white !important;
        border-radius: 8px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🤖 AI Smart Attendance Portal")
st.subheader("Automated Tracking & Admin Management")
st.markdown("---")

# --- Helper Functions (With Error Proofing) ---
def get_students():
    if not os.path.exists('students.csv'):
        df = pd.DataFrame(columns=['Roll_Number', 'Name', 'Email'])
        df.to_csv('students.csv', index=False)
        return df
    try:
        df = pd.read_csv('students.csv')
        df.columns = df.columns.str.strip().str.title().str.replace(' ', '_')
        if 'Roll_Number' not in df.columns or 'Name' not in df.columns:
            df = pd.DataFrame(columns=['Roll_Number', 'Name', 'Email'])
            df.to_csv('students.csv', index=False)
        return df
    except Exception:
        df = pd.DataFrame(columns=['Roll_Number', 'Name', 'Email'])
        df.to_csv('students.csv', index=False)
        return df

def get_attendance():
    if not os.path.exists('attendance_log.csv'):
        df = pd.DataFrame(columns=['Roll_Number', 'Name', 'Timestamp', 'Status'])
        df.to_csv('attendance_log.csv', index=False)
        return df
    try:
        df = pd.read_csv('attendance_log.csv')
        df.columns = df.columns.str.strip().str.title().str.replace(' ', '_')
        if 'Roll_Number' not in df.columns:
            df = pd.DataFrame(columns=['Roll_Number', 'Name', 'Timestamp', 'Status'])
            df.to_csv('attendance_log.csv', index=False)
        return df
    except Exception:
        df = pd.DataFrame(columns=['Roll_Number', 'Name', 'Timestamp', 'Status'])
        df.to_csv('attendance_log.csv', index=False)
        return df

def send_email_alert(student_email, student_name, roll_no):
    try:
        sender_email = st.secrets.get("SMTP_EMAIL", "")
        sender_password = st.secrets.get("SMTP_PASSWORD", "")
        if not sender_email or not sender_password:
            return False
            
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = student_email
        msg['Subject'] = f"Attendance Marked - {student_name}"
        
        body = f"Hello {student_name} (Roll No: {roll_no}),\n\nYour attendance has been recorded successfully on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n\nThank you!"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception:
        return False

# --- MAIN LAYOUT ---
col1, col2 = st.columns([1, 1])

# LEFT COLUMN: Attendance System
with col1:
    st.header("📷 Face Scan / Attendance Portal")
    df_students = get_students()
    
    if not df_students.empty and 'Roll_Number' in df_students.columns and 'Name' in df_students.columns:
        student_options = [f"{row['Roll_Number']} - {row['Name']}" for _, row in df_students.iterrows()]
        selected_student = st.selectbox("Select Student to Mark Attendance", student_options)
        
        cam_photo = st.camera_input("Take Photo")
        
        if cam_photo:
            roll_no = selected_student.split(" - ")[0]
            s_name = selected_student.split(" - ")[1]
            
            email_val = df_students[df_students['Roll_Number'].astype(str) == str(roll_no)]['Email'].values
            s_email = email_val[0] if len(email_val) > 0 and pd.notna(email_val[0]) else ""
            
            if st.button("Submit Attendance", type="primary"):
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                new_log = pd.DataFrame([[roll_no, s_name, now, "Present"]], columns=['Roll_Number', 'Name', 'Timestamp', 'Status'])
                
                df_log = get_attendance()
                df_log = pd.concat([df_log, new_log], ignore_index=True)
                df_log.to_csv('attendance_log.csv', index=False)
                
                st.success(f"Attendance Marked: {s_name} ({roll_no})")
                
                if s_email and send_email_alert(s_email, s_name, roll_no):
                    st.info(f"Email sent to {s_email}")
    else:
        st.warning("No students added yet! Add students using the Admin Panel on the right side.")

# RIGHT COLUMN: Admin Panel on Home Screen
with col2:
    st.header("⚙️ Admin Control Panel")
    st.write("Add new student details directly into the database.")
    
    admin_pass = st.text_input("Enter Admin Password", type="password")
    
    if admin_pass == st.secrets.get("ADMIN_PASSWORD", "admin123"):
        st.success("Admin Access Granted")
        
        with st.form("register_form"):
            st.subheader("Register New Student")
            new_roll = st.text_input("Roll Number")
            new_name = st.text_input("Student Name")
            new_email = st.text_input("Email Address")
            save_btn = st.form_submit_button("Add Student")
            
            if save_btn:
                if new_roll and new_name and new_email:
                    df_s = get_students()
                    
                    # Safe Column Checking
                    exists = False
                    if not df_s.empty and 'Roll_Number' in df_s.columns:
                        exists = str(new_roll) in df_s['Roll_Number'].astype(str).values
                    
                    if exists:
                        st.error("Roll number already exists!")
                    else:
                        new_row = pd.DataFrame([[new_roll, new_name, new_email]], columns=['Roll_Number', 'Name', 'Email'])
                        df_s = pd.concat([df_s, new_row], ignore_index=True)
                        df_s.to_csv('students.csv', index=False)
                        st.success(f"Successfully registered {new_name}!")
                        st.rerun()
                else:
                    st.error("Please fill all fields.")
        
        st.subheader("Current Registered Students")
        st.dataframe(get_students(), use_container_width=True)
    elif admin_pass != "":
        st.error("Incorrect Password")

# --- BOTTOM SECTION: Logs History ---
st.markdown("---")
st.header("📊 Attendance Log History")
df_attendance = get_attendance()
st.dataframe(df_attendance, use_container_width=True)
