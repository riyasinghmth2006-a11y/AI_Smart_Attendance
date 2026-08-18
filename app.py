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

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Smart Attendance System",
    page_icon="🤖",
    layout="wide"
)

# --- Clean Light Theme CSS ---
st.markdown("""
<style>
    /* Full Page Background */
    .stApp {
        background-color: #FFFFFF;
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
    
    /* Responsive & Mobile Friendly Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        background-color: #F1F5F9;
        border-radius: 8px;
        color: #334155;
        font-weight: 600;
        padding: 0px 14px;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284C7 !important;
        color: white !important;
    }

    /* Force Light Styling on Dataframes */
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1 style='margin:0; font-size: 2.2rem;'>🤖 AI Smart Attendance Portal</h1>
    <p style='margin:5px 0 0 0; opacity: 0.9;'>Automated Attendance Tracking & Real-Time Analytics</p>
</div>
""", unsafe_allow_html=True)

# --- CSV Helper Functions ---
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
        df.columns = df.columns.str.strip().str.replace(' ', '_')
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
        msg['Subject'] = f"Attendance Confirmation - {student_name}"
        
        body = f"Hello {student_name} (Roll No: {roll_no}),\n\nYour attendance has been recorded on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n\nThank you,\nAI Attendance System"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception:
        return False

# --- HOME SCREEN TABS ---
tab1, tab2, tab3 = st.tabs(["📷 Attendance", "⚙️ Admin Panel", "📊 Analytics"])

# --- TAB 1: TAKE ATTENDANCE ---
with tab1:
    st.subheader("Face Scan & Attendance Portal")
    col1, col2 = st.columns([1, 1])
    
    df_st = get_students()
    
    with col1:
        st.write("### Student Verification")
        if not df_st.empty and 'Roll_Number' in df_st.columns and 'Name' in df_st.columns:
            student_list = [f"{row['Roll_Number']} - {row['Name']}" for _, row in df_st.iterrows()]
            selected_student = st.selectbox("Select Registered Student", student_list)
            
            camera_image = st.camera_input("Capture Face Photo")
            
            if camera_image:
                roll_no = selected_student.split(" - ")[0]
                s_name = selected_student.split(" - ")[1]
                
                email_matches = df_st[df_st['Roll_Number'].astype(str) == str(roll_no)]['Email'].values
                s_email = email_matches[0] if len(email_matches) > 0 else ""
                
                if st.button("Mark Attendance", type="primary"):
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    new_log = pd.DataFrame([[roll_no, s_name, now, "Present"]], columns=['Roll_Number', 'Name', 'Timestamp', 'Status'])
                    
                    df_log = get_attendance()
                    df_log = pd.concat([df_log, new_log], ignore_index=True)
                    df_log.to_csv('attendance_log.csv', index=False)
                    
                    st.success(f"✅ Attendance Marked for {s_name} ({roll_no})!")
                    
                    if s_email and send_email_alert(s_email, s_name, roll_no):
                        st.info(f"📧 Email notification sent to {s_email}")
        else:
            st.info("ℹ️ No registered students found. Please add students in the **⚙️ Admin Panel** tab above.")

    with col2:
        st.write("### Today's Quick Summary")
        df_log = get_attendance()
        st.metric("Total Attendance Logged Today", len(df_log))
        st.dataframe(df_log.tail(5), use_container_width=True)

# --- TAB 2: ADMIN PANEL ---
with tab2:
    st.subheader("🔑 Admin Control Dashboard")
    st.info("Manage student registrations directly from the main interface.")
    
    admin_pass = st.text_input("Enter Admin Password", type="password")
    
    if admin_pass == st.secrets.get("ADMIN_PASSWORD", "admin123"):
        st.success("🔓 Admin Controls Active")
        col_a, col_b = st.columns([1, 1])
        
        with col_a:
            st.write("#### Register New Student")
            with st.form("add_student_form"):
                new_roll = st.text_input("Roll Number")
                new_name = st.text_input("Student Name")
                new_email = st.text_input("Email Address")
                submit_btn = st.form_submit_button("Save Student")
                
                if submit_btn:
                    if new_roll and new_name and new_email:
                        df_s = get_students()
                        if not df_s.empty and str(new_roll) in df_s['Roll_Number'].astype(str).values:
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
            df_curr = get_students()
            st.dataframe(df_curr, use_container_width=True)
            st.caption(f"Total Registered Students: {len(df_curr)}")
    elif admin_pass != "":
        st.error("❌ Incorrect Admin Password")

# --- TAB 3: ANALYTICS & REPORTS ---
with tab3:
    st.subheader("📊 Analytics & Data Export")
    df_log = get_attendance()
    
    if not df_log.empty and 'Timestamp' in df_log.columns:
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
            
            if st.button("Generate & Download PDF Summary"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt="AI Smart Attendance Report", ln=True, align='C')
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
                pdf.ln(10)
                
                for _, row in df_log.iterrows():
                    pdf.cell(200, 8, txt=f"Roll: {row.get('Roll_Number', '')} | Name: {row.get('Name', '')} | Time: {row.get('Timestamp', '')}", ln=True)
                    
                pdf.output("attendance_report.pdf")
                with open("attendance_report.pdf", "rb") as file:
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=file,
                        file_name="attendance_report.pdf",
                        mime="application/pdf"
                    )
    else:
        st.info("No attendance records logged yet.")
        
