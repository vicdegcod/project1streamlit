import streamlit as st
import sqlite3

# ==============================
# DATABASE
# ==============================

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("rehabilitation.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            addiction TEXT,
            admission_date TEXT,
            completed_sessions INTEGER DEFAULT 0,
            total_sessions INTEGER
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS therapists(
            therapist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            specialization TEXT,
            phone TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments(
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            therapist_id INTEGER,
            visit_date TEXT,
            visit_time TEXT,
            status TEXT,
            FOREIGN KEY(client_id) REFERENCES clients(client_id),
            FOREIGN KEY(therapist_id) REFERENCES therapists(therapist_id)
        )
        """)

        self.conn.commit()

db = Database()

# ==============================
# STREAMLIT PAGE
# ==============================

st.set_page_config(page_title="Rehabilitation Management System", layout="wide")

st.title("🏥 Rehabilitation Management System")

menu = st.sidebar.selectbox(
    "Select Module",
    [
        "Add Client",
        "Delete Client",
        "View Clients",
        "Add Therapist",
        "View Therapists",
        "Book Therapy Visit",
        "Cancel Therapy Visit",
        "View Therapy Visits",
        "Update Treatment Progress",
        "Calculate Progress"
    ]
)

# ===================================================
# ADD CLIENT
# ===================================================

if menu == "Add Client":

    st.header("Add Client")

    name = st.text_input("Client Name")
    age = st.number_input("Age", 1, 120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    addiction = st.text_input("Addiction Type")
    admission = st.date_input("Admission Date")
    sessions = st.number_input("Total Therapy Sessions", 1)

    if st.button("Add Client"):

        db.cursor.execute("""
        INSERT INTO clients(name,age,gender,addiction,admission_date,total_sessions)
        VALUES(?,?,?,?,?,?)
        """,
        (
            name,
            age,
            gender,
            addiction,
            str(admission),
            sessions
        ))

        db.conn.commit()

        st.success("Client Added Successfully")

# ===================================================
# DELETE CLIENT
# ===================================================

elif menu == "Delete Client":

    st.header("Delete Client")

    cid = st.number_input("Client ID", 1)

    if st.button("Delete"):

        db.cursor.execute(
            "DELETE FROM appointments WHERE client_id=?",
            (cid,)
        )

        db.cursor.execute(
            "DELETE FROM clients WHERE client_id=?",
            (cid,)
        )

        db.conn.commit()

        st.success("Client Deleted")

# ===================================================
# VIEW CLIENTS
# ===================================================

elif menu == "View Clients":

    st.header("Client List")

    db.cursor.execute("SELECT * FROM clients")

    rows = db.cursor.fetchall()

    st.dataframe(
        rows,
        use_container_width=True
    )

# ===================================================
# ADD THERAPIST
# ===================================================

elif menu == "Add Therapist":

    st.header("Add Therapist")

    name = st.text_input("Therapist Name")
    specialization = st.text_input("Specialization")
    phone = st.text_input("Phone")

    if st.button("Add Therapist"):

        db.cursor.execute("""
        INSERT INTO therapists(name,specialization,phone)
        VALUES(?,?,?)
        """,(name,specialization,phone))

        db.conn.commit()

        st.success("Therapist Added")

# ===================================================
# VIEW THERAPISTS
# ===================================================

elif menu == "View Therapists":

    st.header("Therapists")

    db.cursor.execute("SELECT * FROM therapists")

    rows = db.cursor.fetchall()

    st.dataframe(rows, use_container_width=True)

# ===================================================
# BOOK VISIT
# ===================================================

elif menu == "Book Therapy Visit":

    st.header("Book Therapy Visit")

    client = st.number_input("Client ID", 1)
    therapist = st.number_input("Therapist ID", 1)
    visit_date = st.date_input("Visit Date")
    visit_time = st.time_input("Visit Time")

    if st.button("Book Visit"):

        db.cursor.execute("""
        INSERT INTO appointments
        (client_id,therapist_id,visit_date,visit_time,status)
        VALUES(?,?,?,?,?)
        """,
        (
            client,
            therapist,
            str(visit_date),
            str(visit_time),
            "Booked"
        ))

        db.conn.commit()

        st.success("Therapy Visit Booked")

# ===================================================
# CANCEL VISIT
# ===================================================

elif menu == "Cancel Therapy Visit":

    st.header("Cancel Therapy Visit")

    appointment = st.number_input("Appointment ID", 1)

    if st.button("Cancel Visit"):

        db.cursor.execute("""
        UPDATE appointments
        SET status='Cancelled'
        WHERE appointment_id=?
        """,(appointment,))

        db.conn.commit()

        st.success("Appointment Cancelled")

# ===================================================
# VIEW APPOINTMENTS
# ===================================================

elif menu == "View Therapy Visits":

    st.header("Appointments")

    db.cursor.execute("""
    SELECT
    appointment_id,
    client_id,
    therapist_id,
    visit_date,
    visit_time,
    status
    FROM appointments
    """)

    rows = db.cursor.fetchall()

    st.dataframe(rows, use_container_width=True)

# ===================================================
# UPDATE PROGRESS
# ===================================================

elif menu == "Update Treatment Progress":

    st.header("Update Progress")

    cid = st.number_input("Client ID", 1)

    completed = st.number_input(
        "Completed Sessions",
        0
    )

    if st.button("Update"):

        db.cursor.execute("""
        UPDATE clients
        SET completed_sessions=?
        WHERE client_id=?
        """,
        (
            completed,
            cid
        ))

        db.conn.commit()

        st.success("Progress Updated")

# ===================================================
# CALCULATE PROGRESS
# ===================================================

elif menu == "Calculate Progress":

    st.header("Treatment Progress")

    cid = st.number_input("Client ID", 1)

    if st.button("Calculate"):

        db.cursor.execute("""
        SELECT
        name,
        completed_sessions,
        total_sessions
        FROM clients
        WHERE client_id=?
        """,(cid,))

        row = db.cursor.fetchone()

        if row:

            name = row[0]
            completed = row[1]
            total = row[2]

            progress = 0

            if total > 0:
                progress = (completed / total) * 100

            st.subheader(name)

            st.write(f"Completed Sessions: **{completed}**")
            st.write(f"Total Sessions: **{total}**")

            st.progress(progress / 100)

            st.success(f"Treatment Progress: {progress:.2f}%")

        else:
            st.error("Client Not Found")