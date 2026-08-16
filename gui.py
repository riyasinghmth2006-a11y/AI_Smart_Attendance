import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import csv
import os


# ==========================================
# COLORS
# ==========================================

BG_COLOR = "#f4f6f8"
CARD_COLOR = "#ffffff"
TEXT_COLOR = "#1f2937"


# ==========================================
# START ATTENDANCE
# ==========================================

def start_attendance():

    subject = subject_var.get()

    if subject == "Select Subject":

        messagebox.showwarning(
            "Subject Required",
            "Please select a subject first."
        )

        return

    subject_numbers = {
        "Python": "1",
        "Data Structures": "2",
        "Mathematics": "3",
        "DBMS": "4"
    }

    choice = subject_numbers[subject]

    try:

        subprocess.Popen(
            [sys.executable, "recognize_face.py"],
            stdin=subprocess.PIPE,
            text=True
        ).stdin.write(choice + "\n")

        status_label.config(
            text=f"Attendance started for {subject}"
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"Could not start attendance.\n\n{error}"
        )


# ==========================================
# VIEW REPORT
# ==========================================

def view_report():

    report_window = tk.Toplevel(root)

    report_window.title(
        "Attendance Report"
    )

    report_window.geometry(
        "1000x600"
    )

    report_window.configure(
        bg=BG_COLOR
    )

    title = tk.Label(
        report_window,
        text="ATTENDANCE REPORT",
        font=("Arial", 20, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )

    title.pack(pady=20)

    columns = (
        "Name",
        "Roll No",
        "Subject",
        "Status",
        "Date & Time",
        "Percentage"
    )

    table = ttk.Treeview(
        report_window,
        columns=columns,
        show="headings"
    )

    for column in columns:

        table.heading(
            column,
            text=column
        )

    table.column(
        "Name",
        width=150
    )

    table.column(
        "Roll No",
        width=100
    )

    table.column(
        "Subject",
        width=150
    )

    table.column(
        "Status",
        width=100
    )

    table.column(
        "Date & Time",
        width=180
    )

    table.column(
        "Percentage",
        width=120
    )

    scrollbar = ttk.Scrollbar(
        report_window,
        orient="vertical",
        command=table.yview
    )

    table.configure(
        yscrollcommand=scrollbar.set
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    table.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    if not os.path.exists(
        "attendance.csv"
    ):

        messagebox.showinfo(
            "No Records",
            "No attendance records found."
        )

        return

    try:

        with open(
            "attendance.csv",
            "r",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            records = list(reader)

    except Exception as error:

        messagebox.showerror(
            "Error",
            str(error)
        )

        return

    for row in records:

        name = row["Name"]
        roll_no = row["Roll_No"]
        subject = row["Subject"]
        status = row["Status"]
        date_time = row["Date_Time"]

        total_classes = 0
        present_classes = 0

        for record in records:

            if (
                record["Roll_No"] == roll_no
                and
                record["Subject"] == subject
            ):

                total_classes += 1

                if (
                    record["Status"].lower()
                    == "present"
                ):

                    present_classes += 1

        if total_classes > 0:

            percentage = (
                present_classes /
                total_classes
            ) * 100

        else:

            percentage = 0

        table.insert(
            "",
            "end",
            values=(
                name,
                roll_no,
                subject,
                status,
                date_time,
                f"{percentage:.2f}%"
            )
        )


# ==========================================
# STUDENT LIST
# ==========================================

def student_list():

    student_window = tk.Toplevel(root)

    student_window.title(
        "Student List"
    )

    student_window.geometry(
        "500x450"
    )

    student_window.configure(
        bg=BG_COLOR
    )

    title = tk.Label(
        student_window,
        text="REGISTERED STUDENTS",
        font=("Arial", 18, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )

    title.pack(pady=20)

    columns = (
        "Name",
        "Roll No"
    )

    table = ttk.Treeview(
        student_window,
        columns=columns,
        show="headings"
    )

    table.heading(
        "Name",
        text="Student Name"
    )

    table.heading(
        "Roll No",
        text="Roll Number"
    )

    table.column(
        "Name",
        width=250
    )

    table.column(
        "Roll No",
        width=150
    )

    table.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=20
    )

    try:

        with open(
            "students.csv",
            "r",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                table.insert(
                    "",
                    "end",
                    values=(
                        row["Name"],
                        row["Roll_No"]
                    )
                )

    except FileNotFoundError:

        messagebox.showerror(
            "Error",
            "students.csv not found."
        )


# ==========================================
# EXIT
# ==========================================

def exit_program():

    root.destroy()


# ==========================================
# MAIN WINDOW
# ==========================================

root = tk.Tk()

root.title(
    "AI Smart Attendance Monitoring System"
)

root.geometry(
    "750x650"
)

root.resizable(
    False,
    False
)

root.configure(
    bg=BG_COLOR
)


# ==========================================
# HEADER
# ==========================================

header = tk.Frame(
    root,
    bg=TEXT_COLOR,
    height=100
)

header.pack(
    fill="x"
)

title = tk.Label(
    header,
    text="AI SMART ATTENDANCE",
    font=("Arial", 25, "bold"),
    bg=TEXT_COLOR,
    fg="white"
)

title.pack(
    pady=(20, 2)
)

subtitle = tk.Label(
    header,
    text="Face Recognition Monitoring System",
    font=("Arial", 11),
    bg=TEXT_COLOR,
    fg="white"
)

subtitle.pack()


# ==========================================
# MAIN CARD
# ==========================================

card = tk.Frame(
    root,
    bg=CARD_COLOR
)

card.pack(
    padx=70,
    pady=35,
    fill="both",
    expand=True
)


# ==========================================
# SUBJECT
# ==========================================

subject_label = tk.Label(
    card,
    text="Select Subject",
    font=("Arial", 13, "bold"),
    bg=CARD_COLOR,
    fg=TEXT_COLOR
)

subject_label.pack(
    pady=(25, 10)
)

subject_var = tk.StringVar()

subject_var.set(
    "Select Subject"
)

subject_dropdown = ttk.Combobox(
    card,
    textvariable=subject_var,
    values=[
        "Python",
        "Data Structures",
        "Mathematics",
        "DBMS"
    ],
    state="readonly",
    width=30
)

subject_dropdown.pack(
    ipady=6
)


# ==========================================
# BUTTONS
# ==========================================

start_button = tk.Button(
    card,
    text="START ATTENDANCE",
    command=start_attendance,
    font=("Arial", 12, "bold"),
    width=28,
    height=2
)

start_button.pack(
    pady=(30, 10)
)


report_button = tk.Button(
    card,
    text="VIEW ATTENDANCE REPORT",
    command=view_report,
    font=("Arial", 12, "bold"),
    width=28,
    height=2
)

report_button.pack(
    pady=10
)


students_button = tk.Button(
    card,
    text="VIEW STUDENT LIST",
    command=student_list,
    font=("Arial", 12, "bold"),
    width=28,
    height=2
)

students_button.pack(
    pady=10
)


exit_button = tk.Button(
    card,
    text="EXIT",
    command=exit_program,
    font=("Arial", 11),
    width=15
)

exit_button.pack(
    pady=20
)


# ==========================================
# STATUS
# ==========================================

status_label = tk.Label(
    root,
    text="System Ready",
    font=("Arial", 10),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)

status_label.pack(
    pady=(0, 15)
)


# ==========================================
# RUN
# ==========================================

root.mainloop()