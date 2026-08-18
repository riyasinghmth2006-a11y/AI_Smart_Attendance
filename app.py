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

# --- Page Configuration & Light Theme ---
st.set_page_config(
    page_title="AI Smart Attendance System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# --- Title Header ---
st.title("🤖 AI Smart Attendance Portal")
st.subheader("Automated Tracking, Subject Management & Real-Time Analytics")
st.markdown("---")

# --- Safe Database Helpers ---
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
        df = pd.DataFrame(columns=['Roll_Number', 'Name', 'Subject', 'Timestamp', 'Status'])
        df.to_csv('attendance_log.csv', index=False)
        return df
    try:
        df = pd.read_csv('attendance_log.csv')
        df.columns = df.columns.str.strip().str.title().str.replace(' ', '_')
        if 'Roll_Number' not in df.columns or 'Subject' not in df.columns:
            df = pd.DataFrame(columns=['Roll_Number', 'Name', 'Subject', 'Timestamp', 'Status'])
            df.to_csv('attendance_log.csv', index=False)
        return df
    except Exception:
        df = pd.DataFrame(columns=['Roll_Number', 'Name', 'Subject', 'Timestamp', 'Status'])
        df.to_csv('attendance_log.csv', index=False)
        return df

def send_email_alert(student_email, student_name, roll_no, subject_name):
    try:
        sender_email = st.secrets.get("SMTP_EMAIL", "")
        sender_password = st.secrets.get("SMTP_PASSWORD", "")
        if not sender_email or not sender_password:
            return False
            
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = student_email
        msg['Subject'] = f"Attendance Marked - {subject_name}"
        
        body = f"Hello {student_name} (Roll No: {roll_no}),\n\nYour attendance for '{subject_name}' has been successfully recorded on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n\nThank you,\nAI Attendance System"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception:
        return False

# Session State for preventing duplicate submissions on single click
if "last_processed_photo" not in st.session_state:
    st.session_state["last_processed_photo"] = None

# --- MAIN LAYOUT (2 COLUMNS) ---
col1, col2 = st.columns([1, 1])

# LEFT COLUMN: Auto-Submit Attendance Marking
with col1:
    st.header("📷 Face Scan / Attendance Portal")
    df_students = get_students()
    
    if not df_students.empty and 'Roll_Number' in df_students.columns:
        student_options = [f"{row['Roll_Number']} - {row['Name']}" for _, row in df_students.iterrows()]
        selected_student = st.selectbox("Select Student", student_options)
        
        # Subject Selection
        subject = st.selectbox("Select Subject", ["Mathematics", "Computer Science", "Physics", "Chemistry", "English"])
        
        cam_photo = st.camera_input("Take Photo")
        
        # Automatic Trigger when Photo is Captured
        if cam_photo is not None:
            photo_id = f"{cam_photo.name}_{cam_photo.size}_{selected_student}_{subject}"
            
            if st.session_state["last_processed_photo"] != photo_id:
                roll_no = selected_student.split(" - ")[0]
                s_name = selected_student.split(" - ")[1]
                
                email_val = df_students[df_students['Roll_Number'].astype(str) == str(roll_no)]['Email'].values
                s_email = email_val[0] if len(email_val) > 0 and pd.notna(email_val[0]) else ""
                
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                new_log = pd.DataFrame([[roll_no, s_name, subject, now, "Present"]], columns=['Roll_Number', 'Name', 'Subject', 'Timestamp', 'Status'])
                
                df_log = get_attendance()
                df_log = pd.concat([df_log, new_log], ignore_index=True)
                df_log.to_csv('attendance_log.csv', index=False)
                
                st.session_state["last_processed_photo"] = photo_id
                
                st.success(f"✅ Auto-Logged: Attendance Marked for {s_name} ({subject})")
                
                if s_email:
                    if send_email_alert(s_email, s_name, roll_no, subject):
                        st.info(f"📧 Confirmation email sent to {s_email}")
            else:
                st.success(f"✅ Attendance already recorded!")
    else:
        st.warning("No students registered yet! Add students using the Admin Panel on the right.")

# RIGHT COLUMN: Admin Panel
with col2:
    st.header("⚙️ Admin Control Panel")
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
                    exists = str(new_roll) in df_s['Roll_Number'].astype(str).values if not df_s.empty else False
                    
                    if exists:
                        st.error("Roll number already exists!")
                    else:
                        new_row = pd.DataFrame([[new_roll, new_name, new_email]], columns=['Roll_Number', 'Name', 'Email'])
                        df_s = pd.concat([df_s, new_row], ignore_index=True)
                        df_s.to_csv('students.csv', index=False)
                        st.success(f"Registered {new_name} successfully!")
                        st.rerun()
                else:
                    st.error("Please fill all fields.")
        
        st.subheader("Current Registered Directory")
        st.dataframe(get_students(), use_container_width=True)
    elif admin_pass != "":
        st.error("Incorrect Password")

# --- BOTTOM SECTION: Analytics & Reports ---
st.markdown("---")
st.header("📊 Attendance Analytics & Percentage Reports")

df_att = get_attendance()

if not df_att.empty:
    m1, m2, m3 = st.columns(3)
    
    total_logs = len(df_att)
    total_students = len(get_students())
    
    m1.metric("Total Attendance Recorded", total_logs)
    m2.metric("Total Registered Students", total_students)
    
    if total_students > 0:
        unique_present = df_att['Roll_Number'].nunique()
        pct = (unique_present / total_students) * 100
        m3.metric("Overall Student Coverage", f"{pct:.1f}%")
    
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.subheader("Subject-wise Attendance Breakdown")
        if 'Subject' in df_att.columns:
            subj_counts = df_att['Subject'].value_counts().reset_index()
            subj_counts.columns = ['Subject', 'Count']
            fig = px.bar(subj_counts, x='Subject', y='Count', color='Subject', title="Attendance per Subject")
            st.plotly_chart(fig, use_container_width=True)
            
    with c_right:
        st.subheader("PDF Report Export")
        st.dataframe(df_att.tail(5), use_container_width=True)
        
        if st.button("Generate & Download PDF Report"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="AI Smart Attendance Summary Report", ln=True, align='C')
            pdf.set_font("Arial", size=10)
            pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
            pdf.ln(10)
            
            for _, r in df_att.iterrows():
                row_str = f"Roll: {r.get('Roll_Number','')} | Name: {r.get('Name','')} | Subj: {r.get('Subject','')} | Time: {r.get('Timestamp','')}"
                pdf.cell(200, 8, txt=row_str, ln=True)
                
            pdf.output("attendance_report.pdf")
            with open("attendance_report.pdf", "rb") as file:
                st.download_button(
                    label="📥 Click Here to Download PDF",
                    data=file,
                    file_name="attendance_report.pdf",
                    mime="application/pdf"
                )
else:
    st.info("No attendance logged yet.")
    
