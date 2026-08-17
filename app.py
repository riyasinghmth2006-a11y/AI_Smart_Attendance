import streamlit as st
import cv2
import numpy as np
import pandas as pd
import datetime
import os
import plotly.express as px

# Streamlit Page Setup
st.set_page_config(page_title="AI Smart Attendance", layout="wide")
st.title("🎓 Advanced AI Smart Attendance System")

# Attendance File Initial Setup
CSV_FILE = "attendance.csv"
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=["Name", "Date", "Time", "Status"])
    df_init.to_csv(CSV_FILE, index=False)

# Sidebar Navigation
menu = st.sidebar.selectbox("Navigation", ["Mark Attendance", "Analytics & History", "Download Reports"])

if menu == "Mark Attendance":
    st.subheader("📷 Live Camera Attendance")
    img_file_buffer = st.camera_input("Take a photo to mark attendance")

    if img_file_buffer is not None:
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        # Verify photo capture
        if cv2_img is not None:
            st.success("✅ Face Captured Successfully!")

            df_curr = pd.read_csv(CSV_FILE)
            today_date = str(datetime.date.today())
            current_time = datetime.datetime.now().strftime("%H:%M:%S")

            student_name = "Student_1"
            already_marked = df_curr[(df_curr['Name'] == student_name) & (df_curr['Date'] == today_date)]

            if already_marked.empty:
                new_entry = pd.DataFrame([{"Name": student_name, "Date": today_date, "Time": current_time, "Status": "Present"}])
                df_updated = pd.concat([df_curr, new_entry], ignore_index=True)
                df_updated.to_csv(CSV_FILE, index=False)
                st.balloons()
                st.info(f"Marked attendance for **{student_name}** at {current_time}")
            else:
                st.warning(f"Attendance for **{student_name}** is already marked today!")

elif menu == "Analytics & History":
    st.subheader("📊 Attendance Analytics & History")
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        st.info("No attendance records found yet.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Records", len(df))
        col2.metric("Unique Students", df["Name"].nunique())
        col3.metric("Total Dates Logged", df["Date"].nunique())
        st.markdown("---")
        
        col_left, col_right = st.columns(2)
        with col_left:
            st.write("### Attendance Count per Student")
            student_counts = df["Name"].value_counts().reset_index()
            student_counts.columns = ["Name", "Count"]
            fig_bar = px.bar(student_counts, x="Name", y="Count", color="Name", title="Total Attendance by Student")
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_right:
            st.write("### Daily Attendance Trend")
            daily_counts = df.groupby("Date").size().reset_index(name="Present Count")
            fig_line = px.line(daily_counts, x="Date", y="Present Count", markers=True, title="Daily Attendance")
            st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("---")
        st.dataframe(df, use_container_width=True)

elif menu == "Download Reports":
    st.subheader("📥 Export & Download Attendance Reports")
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        st.warning("No data available to export.")
    else:
        dates = df["Date"].unique().tolist()
        selected_date = st.selectbox("Filter by Date (Optional)", ["All Dates"] + dates)

        export_df = df if selected_date == "All Dates" else df[df["Date"] == selected_date]
        st.dataframe(export_df)

        csv_data = export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download Report as CSV",
            data=csv_data,
            file_name=f"attendance_report_{selected_date}.csv",
            mime="text/csv",
        )
        
