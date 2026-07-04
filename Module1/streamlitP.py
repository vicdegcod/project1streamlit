import streamlit as st
import sqlite3
import pandas as pd

# ----------------------------
# Database Connection
# ----------------------------
conn = sqlite3.connect(
    "rehabilitation.db",
    check_same_thread=False
)
cursor = conn.cursor()

st.set_page_config(
    page_title="Rehabilitation Management System",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Rehabilitation Management System")

menu = st.sidebar.selectbox(
    "Select Menu",
    (
        "Dashboard",
        "Patients",
        "Therapists",
        "Appointments",
        "Therapy Sessions",
        "Progress Reports"
    )
)

# ==========================
# Dashboard
# ==========================
if menu == "Dashboard":

    st.header("System Dashboard")

    patient_count = cursor.execute(
        "SELECT COUNT(*) FROM patients"
    ).fetchone()[0]

    therapist_count = cursor.execute(
        "SELECT COUNT(*) FROM therapists"
    ).fetchone()[0]

    appointment_count = cursor.execute(
        "SELECT COUNT(*) FROM appointments"
    ).fetchone()[0]

    c1, c2, c3 = st.columns(3)

    c1.metric("Patients", patient_count)
    c2.metric("Therapists", therapist_count)
    c3.metric("Appointments", appointment_count)

# ==========================
# Patients
# ==========================
elif menu == "Patients":

    st.header("Patient Management")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Add",
        "View",
        "Update",
        "Delete"
    ])

    # -------------------
    # Add
    # -------------------
    with tab1:

        fname = st.text_input("First Name")
        lname = st.text_input("Last Name")
        gender = st.selectbox(
            "Gender",
            ["Male", "Female", "Other"]
        )
        age = st.number_input(
            "Age",
            1,
            120
        )

        phone = st.text_input("Phone")
        email = st.text_input("Email")
        address = st.text_area("Address")
        addiction = st.text_input("Addiction")
        admission = st.date_input("Admission Date")

        if st.button("Register Patient"):

            cursor.execute("""
            INSERT INTO patients(
            first_name,
            last_name,
            gender,
            age,
            phone,
            email,
            address,
            addiction,
            admission_date)
            VALUES(?,?,?,?,?,?,?,?,?)
            """, (
                fname,
                lname,
                gender,
                age,
                phone,
                email,
                address,
                addiction,
                str(admission)
            ))

            conn.commit()
            st.success("Patient Registered Successfully")

    # -------------------
    # View
    # -------------------
    with tab2:

        df = pd.read_sql_query(
            "SELECT * FROM patients",
            conn
        )

        st.dataframe(df)

    # -------------------
    # Update
    # -------------------
    with tab3:

        pid = st.number_input(
            "Patient ID",
            1,
            step=1
        )

        new_phone = st.text_input("New Phone")
        new_email = st.text_input("New Email")

        if st.button("Update Patient"):

            cursor.execute("""
            UPDATE patients
            SET phone=?,
            email=?
            WHERE patient_id=?
            """, (
                new_phone,
                new_email,
                pid
            ))

            conn.commit()

            st.success("Patient Updated")

    # -------------------
    # Delete
    # -------------------
    with tab4:

        delete_id = st.number_input(
            "Delete Patient ID",
            1,
            step=1
        )

        if st.button("Delete Patient"):

            cursor.execute("""
            DELETE FROM patients
            WHERE patient_id=?
            """, (
                delete_id,
            ))

            conn.commit()

            st.success("Patient Deleted")

# ==========================
# Therapists
# ==========================
elif menu == "Therapists":

    st.header("Therapist Management")

    therapists = pd.read_sql_query(
        "SELECT * FROM therapists",
        conn
    )

    st.dataframe(therapists)

# ==========================
# Appointments
# ==========================
elif menu == "Appointments":

    st.header("Appointments")

    appointments = pd.read_sql_query("""
    SELECT

    appointments.appointment_id,

    patients.first_name ||

    ' ' ||

    patients.last_name

    AS Patient,

    therapists.first_name ||

    ' ' ||

    therapists.last_name

    AS Therapist,

    appointment_date,

    appointment_time,

    status

    FROM appointments

    JOIN patients
    ON appointments.patient_id=patients.patient_id

    JOIN therapists
    ON appointments.therapist_id=therapists.therapist_id
    """, conn)

    st.dataframe(appointments)

# ==========================
# Therapy Sessions
# ==========================
elif menu == "Therapy Sessions":

    st.header("Therapy Sessions")

    sessions = pd.read_sql_query(
        "SELECT * FROM therapy_sessions",
        conn
    )

    st.dataframe(sessions)

# ==========================
# Progress Reports
# ==========================
elif menu == "Progress Reports":

    st.header("Patient Progress")

    report = pd.read_sql_query("""

    SELECT

    patient_id,

    first_name,

    last_name,

    completed_sessions,

    total_sessions

    FROM patients

    """, conn)

    report["Progress %"] = (
        report["completed_sessions"] /
        report["total_sessions"] * 100
    ).round(1)

    st.dataframe(report)

    st.bar_chart(
        report.set_index("first_name")["Progress %"]
    )