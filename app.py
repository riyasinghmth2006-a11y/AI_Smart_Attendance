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

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Attendance Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Generated on: {datetime.date.today()}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(35, 10, "Name", border=1)
    pdf.cell(25, 10, "Roll", border=1)
    pdf.cell(35, 10, "Date", border=1)
    pdf.cell(30, 10, "Time", border=1)
    pdf.cell(30, 10, "Status", border=1)
    pdf.ln()
    
    pdf.set_font("Arial", size=12)
    for _, row in df.iterrows():
        pdf.cell(35, 10, str(row['Name']), border=1)
        pdf.cell(25, 10, str(row['Roll_No']), border=1)
        pdf.cell(35, 10, str(row['Date']), border=1)
        pdf.cell(30, 10, str(row['Time']), border=1)
        pdf.cell(30, 10, str(row['Status']), border=1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# Sidebar Navigation
menu = st.sidebar.selectbox("Navigation", [
    "Mark Attendance", 
    "Analytics & History", 
    "Download Reports", 
    "🔑 Admin Panel (Overrides)"
])

# ----------------- MARK ATTENDANCE -----------------
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
            new_entry = pd.DataFrame([{
                "Name": student_name, 
                "Roll_No": roll_no, 
                "Email": user_email,
                "Date": today, 
                "Time": current_time, 
                "Status": "Present"
            }])
            df_updated = pd.concat([df, new_entry], ignore_index=True)
            save_data(df_updated)
            st.balloons()
            st.success(f"✅ Marked attendance for *{student_name}* (Roll: {roll_no})!")

            if user_email:
                with st.spinner("Sending Email Alert..."):
                    status, msg = send_email_alert(user_email, student_name, current_time)
                if status:
                    st.info(f"📧 Confirmation email sent to *{user_email}*!")
                else:
                    st.warning(f"⚠️ Attendance marked, but email failed: {msg}")

# ----------------- ANALYTICS & HISTORY -----------------
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

# ----------------- DOWNLOAD REPORTS -----------------
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

# ----------------- ADMIN PANEL -----------------
elif menu == "🔑 Admin Panel (Overrides)":
    st.subheader("🔒 Teacher / Admin Control Panel")
    
    # Password Protection
    admin_password = st.secrets.get("ADMIN_PASSWORD", "admin123")
    pwd_input = st.text_input("Enter Admin Password", type="password")
    
    if pwd_input == admin_password:
        st.success("✅ Admin Authenticated")
        df = load_data()

        tab1, tab2, tab3 = st.tabs(["📝 Edit / Delete Records", "➕ Manual Attendance Entry", "📋 Full Attendance Log"])

        # Tab 1: Edit / Delete Records
        with tab1:
            st.write("### Edit or Delete Records")
            if df.empty:
                st.info("No records to edit.")
            else:
                # Add index column for easy selection
                df_reset = df.reset_index()
                selected_index = st.number_input("Select Record Index to Edit/Delete", min_value=0, max_value=len(df)-1, step=1, value=0)
                
                selected_row = df.iloc[selected_index]
                st.write("*Selected Entry:*")
                st.json(selected_row.to_dict())

                col_e1, col_e2 = st.columns(2)
                
                # Edit Form
                with col_e1:
                    st.write("#### ✏️ Edit Record")
                    new_name = st.text_input("Edit Name", value=str(selected_row["Name"]))
                    new_roll = st.text_input("Edit Roll No", value=str(selected_row["Roll_No"]))
                    new_email = st.text_input("Edit Email", value=str(selected_row["Email"]))
                    new_status = st.selectbox("Edit Status", ["Present", "Absent", "Late"], index=["Present", "Absent", "Late"].index(selected_row["Status"]) if selected_row["Status"] in ["Present", "Absent", "Late"] else 0)

                    if st.button("Update Record"):
                        df.at[selected_index, "Name"] = new_name
                        df.at[selected_index, "Roll_No"] = new_roll
                        df.at[selected_index, "Email"] = new_email
                        df.at[selected_index, "Status"] = new_status
                        save_data(df)
                        st.success("Record updated successfully!")
                        st.rerun()

                # Delete Button
                with col_e2:
                    st.write("#### 🗑️ Delete Record")
                    st.write("Warning: This action cannot be undone.")
                    if st.button("Delete Selected Record", type="primary"):
                        df = df.drop(selected_index).reset_index(drop=True)
                        save_data(df)
                        st.warning("Record deleted successfully!")
                        st.rerun()

        # Tab 2: Manual Attendance Entry
        with tab2:
            st.write("### ➕ Manual Attendance Override")
            col_m1, col_m2 = st.columns(2)
            m_name = col_m1.text_input("Student Name ", value="")
            m_roll = col_m2.text_input("Roll Number ", value="")
            m_email = col_m1.text_input("Email ID ", value="")
            m_date = col_m2.date_input("Date", value=datetime.date.today())
            m_status = col_m1.selectbox("Status", ["Present", "Absent", "Late"])

            if st.button("Add Manual Attendance"):
                if m_name and m_roll:
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    new_entry = pd.DataFrame([{
                        "Name": m_name,
                        "Roll_No": m_roll,
                        "Email": m_email,
                        "Date": str(m_date),
                        "Time": current_time,
                        "Status": m_status
                    }])
                    df_updated = pd.concat([df, new_entry], ignore_index=True)
                    save_data(df_updated)
                    st.success(f"Manually added attendance for {m_name} ({m_status})!")
                    st.rerun()
                else:
                    st.error("Please fill Name and Roll Number!")

        # Tab 3: Full Log
        with tab3:
            st.write("### 📋 All Attendance Log")
            st.dataframe(df, use_container_width=True)

    elif pwd_input != "":
        st.error("❌ Incorrect Password. Please try again.")
    else:
        st.info("Enter the admin password above to unlock admin tools.")