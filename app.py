import streamlit as st

st.title("AI Smart Attendance System")

# Streamlit Browser Camera Widget
img_file_buffer = st.camera_input("Take Attendance Picture")

if img_file_buffer is not None:
    st.success("Photo captured successfully!")
    st.image(img_file_buffer)
