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

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Smart Attendance",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PREMIUM LOOK ---
st.markdown("""
<style>
    /* Dark Theme Custom Styling */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    
    /* Custom Card Styling */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        text-align: center;
    }
    .metric-card h3 {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 8px;
    }
    .metric-card h1 {
        color: #38bdf8;
        font-size: 2.2rem;
        margin: 0;
    }

    /* Primary Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b1329;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

ATTENDANCE_CSV = "attendance.csv"
STUDENTS_CSV = "students.csv"

# --- HELPER FUNCTIONS ---
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
    if not sender_email or not sender_password or to_email == "N/A": return False, "Missing credentials"
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = f"Attendance Confirmation - {subject_name}"
        msg.attach(MIMEText(f"Hello,\n\nAttendance marked for {student_name} ({subject_name}) at {time_str}.\n\nRegards,\nAI System", 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=5)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True, "Success"
    except Exception as e:
        return False, str(e)

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

# --- HEADER SECTION ---
st.title("🎓 AI Smart Attendance Portal")
st.caption("Automated Face-Verification & Real-time Analytics System")

# KPI METRICS CARDS
st_df = load_students()
att_df = load_attendance()
today_str = str(datetime.date.today())
today_count = len(att_df[att_df['Date'] == today_str]) if not att_df.empty else 0

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f'<div class="metric-card"><h3>TOTAL REGISTERED</h3><h1>{len(st_df)}</h1></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card"><h3>PRESENT TODAY</h3><h1>{today_count}</h1></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><h3>TOTAL LOGS</h3><h1>{len(att_df)}</h1></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- NAVIGATION ---
menu = st.sidebar.radio("📌 Navigation Menu", ["📸 Mark Attendance", "📊 Analytics & Insights", "📥 Download Reports", "🔑 Admin Panel"])

if menu == "📸 Mark Attendance":
    st.subheader("📷 Face Verification Scan")
    students_df = load_students()
    
    if students_df.empty:
        st.warning("No students registered! Please add students via Admin Panel.")
    else:
        c1, c2 = st.columns(2)
        selected_roll = c1.selectbox("Select Roll Number", students_df['Roll_No'].astype(str).unique())
        matched_student = students_df[students_df['Roll_No'].astype(str) == str(selected_roll)]
        
        if not matched_student.empty:
            student_info = matched_student.iloc[0]
            student_name = student_info.get("Name", "Unknown")
            student_email = student_info.get("Email", "N/A")
            
            c2.selectbox("Select Subject", ["Python Programming", "AI & Machine Learning", "Data Science", "Web Development"], key="subj")
            selected_subject = st.session_state.subj
            
            st.info(f"👤 *Student Name:* {student_name} | 📧 *Email:* {student_email}")
            
            img_file = st.camera_input("Scan Face via Camera")
            if img_file is not None:
                with st.spinner("🔍 Validating Face Clarity..."):
                    is_valid, _ = verify_face_image(img_file)
                
                if not is_valid:
                    st.error("❌ Scan Failed: Please face the camera properly with good lighting.")
                else:
                    df = load_attendance()
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    already_marked = df[(df['Roll_No'].astype(str) == str(selected_roll)) & 
                                        (df['Date'] == today_str) & 
                                        (df['Subject'] == selected_subject)]
                    
                    if not already_marked.empty:
                        st.warning(f"⚠️ *{student_name}* is already marked Present for *{selected_subject}* today!")
                    else:
                        new_entry = pd.DataFrame([{
                            "Name": student_name, "Roll_No": selected_roll, "Email": student_email,
                            "Subject": selected_subject, "Date": today_str, "Time": current_time, "Status": "Present"
                        }])
                        save_attendance(pd.concat([df, new_entry], ignore_index=True))
                        st.balloons()
                        st.success(f"✅ Marked Present: *{student_name}* ({selected_subject})")
                        
                        if student_email != "N/A":
                            status, msg = send_email_alert(student_email, student_name, selected_subject, current_time)
                            if status: st.info(f"📧 Confirmation email sent to *{student_email}*!")

elif menu == "📊 Analytics & Insights":
    st.subheader("📊 Class Attendance Dashboard")
    df = load_attendance()
    if df.empty:
        st.info("No attendance data logged yet.")
    else:
        filter_subj = st.selectbox("Filter Subject", ["All"] + list(df['Subject'].unique()))
        filtered_df = df if filter_subj == "All" else df[df['Subject'] == filter_subj]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        fig = px.bar(filtered_df, x="Subject", color="Status", title="Subject-wise Breakdown", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

elif menu == "📥 Download Reports":
    st.subheader("📥 Export Attendance Files")
    df = load_attendance()
    if df.empty:
        st.warning("No records to export.")
    else:
        col1, col2 = st.columns(2)
        pdf_bytes = create_pdf(df)
        col1.download_button("📄 Download PDF Report", data=pdf_bytes, file_name="attendance_report.pdf", mime="application/pdf")
        csv_data = df.to_csv(index=False).encode('utf-8')
        col2.download_button("📊 Download CSV File", data=csv_data, file_name="attendance_report.csv", mime="text/csv")

elif menu == "🔑 Admin Panel":
    st.subheader("🔑 Admin Settings")
    pwd_input = st.text_input("Enter Admin Password", type="password")
    if pwd_input == st.secrets.get("ADMIN_PASSWORD", "admin123"):
        st.success("✅ Authenticated")
        tab1, tab2 = st.tabs(["➕ Manage Student Directory", "📋 View Attendance Logs"])
        
        with tab1:
            st.write("### Add New Student")
            with st.form("add_student", clear_on_submit=True):
                r = st.text_input("Roll Number")
                n = st.text_input("Student Name")
                e = st.text_input("Email Address")
                if st.form_submit_button("Add Student"):
                    if r and n:
                        st_df = load_students()
                        new_row = pd.DataFrame([{"Roll_No": str(r), "Name": str(n), "Email": str(e) if e else "N/A"}])
                        save_students(pd.concat([st_df, new_row], ignore_index=True))
                        st.success(f"Added: {n} (Roll No: {r})")
                        st.rerun()
                    else: st.error("Please enter Roll No and Name!")
            
            st.write("### Registered Students")
            st.dataframe(load_students(), use_container_width=True)
            
        with tab2:
            st.dataframe(load_attendance(), use_container_width=True)
