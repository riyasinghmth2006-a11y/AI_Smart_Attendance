import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fpdf import FPDF

# --- Page Configuration (Light Theme & Wide Layout) ---
st.set_page_config(
    page_title="AI Smart Attendance System",
    page_icon="🤖",
    layout="wide"
)

# --- Custom Light Theme CSS ---
st.markdown("""
<style>
    /* Main Background & Text Color */
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }
    
    /* Header Container */
    .main-header {
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    
    /* Light Cards */
    .light-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    
    /* Streamlit Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #E2E8F0;
        border-radius: 8px;
        color: #334155;
        font-weight: 600;
        padding: 0px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284C7 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.markdown("""
<div class="main-header">
    <h1 style='margin:0; font-size: 2.2rem;'>🤖 AI Smart Attendance Portal</h1>
    <p style='margin:5px 0 0 0; opacity: 0.9;'>Automated Attendance Tracking & Real-Time Analytics</p>
</div>
""", unsafe_allow_html=True)

# --- CSV Data Initialization ---
if not os.path.exists('students.csv'):
    df_students = pd.DataFrame(columns=['Roll_Number', 'Name', 'Email'])
    df_students.to_csv('students.csv', index=False)

if not os.path.exists('attendance_log.csv'):
    df_log = pd.DataFrame(columns=['Roll_Number', 'Name', 'Timestamp', 'Status'])
    df_log.to_csv('attendance_log.csv', index=False)

# --- Helper Functions ---
def get_students():
    return pd.read_csv('students.csv')

def get_attendance():
    return pd.read_csv('attendance_log.csv')

def send_email_alert(student_email, student_name, roll_no):
    try:
        sender_email = st.secrets["SMTP_EMAIL"]
        sender_password = st.secrets["SMTP_PASSWORD"]
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = student_email
        msg['Subject'] = f"Attendance Confirmation - {student_name}"
        
        body = f"Hello {student_name} (Roll No: {roll_no}),\n\nYour attendance has been successfully recorded on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}.\n\nThank you,\nAI Attendance System"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return False

# --- HOME SCREEN TABS (Admin Panel Included on Main Screen) ---
tab1, tab2, tab3 = st.tabs(["📷 Take Attendance", "⚙️ Admin Panel (Home Screen)", "📊 Analytics & Reports"])

# --- TAB 1: TAKE ATTENDANCE ---
with tab1:
    st.subheader("Face Scan & Attendance Portal")
    col1, col2 = st.columns([1, 1])
    
    df_st = get_students()
    
    with col1:
        st.write("### Student Verification")
        if not df_st.empty:
            student_list = [f"{row['Roll_Number']} - {row['Name']}" for _, row in df_st.iterrows()]
            selected_student = st.selectbox("Select Registered Student", student_list)
            
            camera_image = st.camera_input("Capture Face Photo")
            
            if camera_image:
                roll_no = selected_student.split(" - ")[0]
                s_name = selected_student.split(" - ")[1]
                s_email = df_st[df_st['Roll_Number'].astype(str) == str(roll_no)]['Email'].values[0]
                
                if st.button("Mark Attendance", type="primary"):
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    new_log = pd.DataFrame([[roll_no, s_name, now, "Present"]], columns=['Roll_Number', 'Name', 'Timestamp', 'Status'])
                    
                    df_log = get_attendance()
                    df_log = pd.concat([df_log, new_log], ignore_index=True)
                    df_log.to_csv('attendance_log.csv', index=False)
                    
                    st.success(f"✅ Attendance Marked for {s_name} ({roll_no})!")
                    
                    # Send Email Alert
                    if send_email_alert(s_email, s_name, roll_no):
                        st.info(f"📧 Confirmation Email sent to {s_email}")
                    else:
                        st.warning("⚠️ Attendance marked, but Email Alert failed (check Streamlit Secrets).")
        else:
            st.warning("⚠️ No students registered yet! Please add students using the Admin Panel tab on top.")

    with col2:
        st.write("### Today's Quick Summary")
        df_log = get_attendance()
        st.metric("Total Attendance Logged Today", len(df_log))
        st.dataframe(df_log.tail(5), use_container_width=True)

# --- TAB 2: ADMIN PANEL ON HOME SCREEN ---
with tab2:
    st.subheader("🔑 Admin Control Dashboard")
    st.info("Manage student registrations and database directly from the main home interface.")
    
    admin_pass = st.text_input("Enter Admin Password to Unlock Controls", type="password")
    
    if admin_pass == st.secrets.get("ADMIN_PASSWORD", "admin123"):
        st.success("🔓 Admin Controls Active")
        
        col_a, col_b = st.columns([1, 1])
        
        with col_a:
            st.write("#### Register New Student")
            with st.form("add_student_form"):
                new_roll = st.text_input("Roll Number")
                new_name = st.text_input("Student Name")
                new_email = st.text_input("Email Address")
                submit_btn = st.form_submit_button("Save Student to Database")
                
                if submit_btn:
                    if new_roll and new_name and new_email:
                        df_s = get_students()
                        if str(new_roll) in df_s['Roll_Number'].astype(str).values:
                            st.error("Roll Number already exists!")
                        else:
                            new_entry = pd.DataFrame([[new_roll, new_name, new_email]], columns=['Roll_Number', 'Name', 'Email'])
                            df_s = pd.concat([df_s, new_entry], ignore_index=True)
                            df_s.to_csv('students.csv', index=False)
                            st.success(f"Added {new_name} successfully!")
                            st.rerun()
                    else:
                        st.error("Please fill all fields!")
                        
        with col_b:
            st.write("#### Registered Student Directory")
            df_curr_students = get_students()
            st.dataframe(df_curr_students, use_container_width=True)
            st.caption(f"Total Registered Students: {len(df_curr_students)}")
    elif admin_pass != "":
        st.error("❌ Incorrect Admin Password")

# --- TAB 3: ANALYTICS & REPORTS ---
with tab3:
    st.subheader("📊 Analytics & Data Export")
    df_log = get_attendance()
    
    if not df_log.empty:
        col_x, col_y = st.columns([2, 1])
        with col_x:
            st.write("#### Attendance Trends")
            df_log['Date'] = pd.to_datetime(df_log['Timestamp']).dt.date
            daily_counts = df_log.groupby('Date').size().reset_index(name='Count')
            fig = px.bar(daily_counts, x='Date', y='Count', title="Daily Attendance Count", color_discrete_sequence=['#0284C7'])
            st.plotly_chart(fig, use_container_width=True)
            
        with col_y:
            st.write("#### Export Data")
            st.dataframe(df_log, use_container_width=True)
            
            # PDF Generation
            if st.button("Generate & Download PDF Summary"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt="AI Smart Attendance Report", ln=True, align='C')
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
                pdf.ln(10)
                
                for _, row in df_log.iterrows():
                    pdf.cell(200, 8, txt=f"Roll: {row['Roll_Number']} | Name: {row['Name']} | Time: {row['Timestamp']}", ln=True)
                    
                pdf.output("attendance_report.pdf")
                with open("attendance_report.pdf", "rb") as file:
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=file,
                        file_name="attendance_report.pdf",
                        mime="application/pdf"
                    )
    else:
        st.info("No attendance data available yet to display analytics.")
        
