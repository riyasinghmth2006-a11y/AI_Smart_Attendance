import streamlit as st
import cv2
import numpy as np
import pandas as pd
import datetime
import os
import plotly.express as px
import face_recognition

# Streamlit Page Setup
st.set_page_config(page_title="AI Smart Attendance", layout="wide")
st.title("🎓 Advanced AI Smart Attendance System")

CSV_FILE = "attendance.csv"
FACES_DIR = "registered_faces"

# Ensure directories exist
if not os.path.exists(FACES_DIR):
    os.makedirs(FACES_DIR)

def load_data():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            if not all(col in df.columns for col in ["Name", "Roll_No", "Date", "Time", "Status"]):
                df = pd.DataFrame(columns=["Name", "Roll_No", "Date", "Time", "Status"])
        except Exception:
            df = pd.DataFrame(columns=["Name", "Roll_No", "Date", "Time", "Status"])
    else:
        df = pd.DataFrame(columns=["Name", "Roll_No", "Date", "Time", "Status"])
    return df

# Function to load registered face encodings
def load_registered_faces():
    known_encodings = []
    known_names = []
    known_rolls = []
    
    for file_name in os.listdir(FACES_DIR):
        if file_name.endswith(".npy"):
            parts = file_name.replace(".npy", "").split("_")
            if len(parts) >= 2:
                name, roll = parts[0], parts[1]
                encoding = np.load(os.path.join(FACES_DIR, file_name))
                known_encodings.append(encoding)
                known_names.append(name)
                known_rolls.append(roll)
    return known_encodings, known_names, known_rolls

# Sidebar Navigation
menu = st.sidebar.selectbox("Navigation", [
    "Mark Attendance", 
    "Register New Student", 
    "Analytics & History", 
    "Download Reports"
])

# ----------------- OPTION 1: MARK ATTENDANCE -----------------
if menu == "Mark Attendance":
    st.subheader("📷 Live Camera Attendance (Face Recognition)")
    img_file_buffer = st.camera_input("Take a photo to mark attendance")

    if img_file_buffer is not None:
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

        # Detect faces in live photo
        face_locations = face_recognition.face_locations(rgb_img)
        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)

        if not face_encodings:
            st.warning("⚠️ No face detected. Please position clearly in front of the camera.")
        else:
            known_encodings, known_names, known_rolls = load_registered_faces()

            if not known_encodings:
                st.error("⚠️ No students registered in system! Please register students first from 'Register New Student' tab.")
            else:
                df_curr = load_data()
                today_date = str(datetime.date.today())
                current_time = datetime.datetime.now().strftime("%H:%M:%S")

                for live_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_encodings, live_encoding, tolerance=0.5)
                    face_distances = face_recognition.face_distance(known_encodings, live_encoding)

                    if True in matches:
                        best_match_index = np.argmin(face_distances)
                        matched_name = known_names[best_match_index]
                        matched_roll = known_rolls[best_match_index]

                        # Check duplicate
                        already_marked = df_curr[(df_curr['Roll_No'] == str(matched_roll)) & (df_curr['Date'] == today_date)]

                        if already_marked.empty:
                            new_entry = pd.DataFrame([{
                                "Name": matched_name,
                                "Roll_No": matched_roll,
                                "Date": today_date,
                                "Time": current_time,
                                "Status": "Present"
                            }])
                            df_updated = pd.concat([df_curr, new_entry], ignore_index=True)
                            df_updated.to_csv(CSV_FILE, index=False)
                            st.balloons()
                            st.success(f"✅ Recognized: **{matched_name}** (Roll: {matched_roll})")
                            st.info(f"Attendance marked at {current_time}")
                        else:
                            st.warning(f"⚠️ **{matched_name}** (Roll: {matched_roll}) is already marked Present today!")
                    else:
                        st.error("❌ Unregistered Face Detected! Attendance not marked.")

# ----------------- OPTION 2: REGISTER STUDENT -----------------
elif menu == "Register New Student":
    st.subheader("📝 Register New Student Profile")

    with st.form("register_form"):
        student_name = st.text_input("Student Name")
        roll_no = st.text_input("Roll Number")
        uploaded_photo = st.camera_input("Capture Student Face Photo")
        submit_btn = st.form_submit_button("Register Student")

        if submit_btn:
            if not student_name or not roll_no:
                st.error("Please fill Student Name and Roll Number!")
            elif uploaded_photo is None:
                st.error("Please capture a photo to register!")
            else:
                bytes_data = uploaded_photo.getvalue()
                cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

                encodings = face_recognition.face_encodings(rgb_img)

                if not encodings:
                    st.error("No face detected in photo! Please take a clearer picture.")
                else:
                    encoding_to_save = encodings[0]
                    file_path = os.path.join(FACES_DIR, f"{student_name}_{roll_no}.npy")
                    np.save(file_path, encoding_to_save)
                    st.success(f"🎉 Student **{student_name}** (Roll: {roll_no}) Registered Successfully!")

# ----------------- OPTION 3: ANALYTICS & HISTORY -----------------
elif menu == "Analytics & History":
    st.subheader("📊 Attendance Analytics & History")
    df = load_data()
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

# ----------------- OPTION 4: DOWNLOAD REPORTS -----------------
elif menu == "Download Reports":
    st.subheader("📥 Export & Download Attendance Reports")
    df = load_data()
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
        
