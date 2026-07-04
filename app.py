import sqlite3


class Database:
    def __init__(self, db_name="rehabilitation.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    # -----------------------------
    # CREATE TABLES
    # -----------------------------
    def create_tables(self):

        # Patients
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients(
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            phone TEXT,
            email TEXT,
            addiction TEXT,
            admission_date TEXT,
            completed_sessions INTEGER DEFAULT 0,
            total_sessions INTEGER DEFAULT 10
        )
        """)

        # Therapists
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS therapists(
            therapist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            specialization TEXT,
            phone TEXT,
            email TEXT
        )
        """)

        # Assignments
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments(
            assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            therapist_id INTEGER,
            assignment_date TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY(therapist_id) REFERENCES therapists(therapist_id)
        )
        """)

        # Appointments
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments(
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            therapist_id INTEGER,
            appointment_date TEXT,
            appointment_time TEXT,
            status TEXT DEFAULT 'Booked',
            FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY(therapist_id) REFERENCES therapists(therapist_id)
        )
        """)

        # Therapy Sessions
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS therapy_sessions(
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            therapist_id INTEGER,
            session_date TEXT,
            notes TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY(therapist_id) REFERENCES therapists(therapist_id)
        )
        """)

        self.conn.commit()

    # -----------------------------
    # PATIENT CRUD
    # -----------------------------
    def add_patient(self, full_name, age, gender,
                    phone, email,
                    addiction,
                    admission_date):

        self.cursor.execute("""
        INSERT INTO patients(
        full_name,
        age,
        gender,
        phone,
        email,
        addiction,
        admission_date
        )
        VALUES(?,?,?,?,?,?,?)
        """,
        (
            full_name,
            age,
            gender,
            phone,
            email,
            addiction,
            admission_date
        ))

        self.conn.commit()

    def get_patients(self):
        self.cursor.execute("""
        SELECT * FROM patients
        ORDER BY full_name
        """)
        return self.cursor.fetchall()

    def search_patient(self, keyword):

        self.cursor.execute("""
        SELECT *
        FROM patients
        WHERE patient_id LIKE ?
        OR full_name LIKE ?
        """,
        (f"%{keyword}%", f"%{keyword}%"))

        return self.cursor.fetchall()

    def update_patient(
            self,
            patient_id,
            full_name,
            age,
            gender,
            phone,
            email,
            addiction):

        self.cursor.execute("""
        UPDATE patients
        SET
        full_name=?,
        age=?,
        gender=?,
        phone=?,
        email=?,
        addiction=?
        WHERE patient_id=?
        """,
        (
            full_name,
            age,
            gender,
            phone,
            email,
            addiction,
            patient_id
        ))

        self.conn.commit()

    def delete_patient(self, patient_id):

        self.cursor.execute("""
        DELETE FROM patients
        WHERE patient_id=?
        """, (patient_id,))

        self.conn.commit()

    # -----------------------------
    # THERAPIST CRUD
    # -----------------------------
    def add_therapist(
            self,
            full_name,
            specialization,
            phone,
            email):

        self.cursor.execute("""
        INSERT INTO therapists(
        full_name,
        specialization,
        phone,
        email
        )
        VALUES(?,?,?,?)
        """,
        (
            full_name,
            specialization,
            phone,
            email
        ))

        self.conn.commit()

    def get_therapists(self):

        self.cursor.execute("""
        SELECT *
        FROM therapists
        ORDER BY full_name
        """)

        return self.cursor.fetchall()

    def delete_therapist(self, therapist_id):

        self.cursor.execute("""
        DELETE FROM therapists
        WHERE therapist_id=?
        """, (therapist_id,))

        self.conn.commit()

    # -----------------------------
    # ASSIGN PATIENT
    # -----------------------------
    def assign_patient(
            self,
            patient_id,
            therapist_id,
            assignment_date):

        self.cursor.execute("""
        INSERT INTO assignments(
        patient_id,
        therapist_id,
        assignment_date
        )
        VALUES(?,?,?)
        """,
        (
            patient_id,
            therapist_id,
            assignment_date
        ))

        self.conn.commit()

    # -----------------------------
    # APPOINTMENTS
    # -----------------------------
    def book_appointment(
            self,
            patient_id,
            therapist_id,
            appointment_date,
            appointment_time):

        self.cursor.execute("""
        INSERT INTO appointments(
        patient_id,
        therapist_id,
        appointment_date,
        appointment_time
        )
        VALUES(?,?,?,?)
        """,
        (
            patient_id,
            therapist_id,
            appointment_date,
            appointment_time
        ))

        self.conn.commit()

    def cancel_appointment(self, appointment_id):

        self.cursor.execute("""
        UPDATE appointments
        SET status='Cancelled'
        WHERE appointment_id=?
        """, (appointment_id,))

        self.conn.commit()

    def upcoming_appointments(self):

        self.cursor.execute("""
        SELECT *
        FROM appointments
        WHERE status='Booked'
        ORDER BY appointment_date
        """)

        return self.cursor.fetchall()

    # -----------------------------
    # THERAPY SESSIONS
    # -----------------------------
    def record_session(
            self,
            patient_id,
            therapist_id,
            session_date,
            notes):

        self.cursor.execute("""
        INSERT INTO therapy_sessions(
        patient_id,
        therapist_id,
        session_date,
        notes
        )
        VALUES(?,?,?,?)
        """,
        (
            patient_id,
            therapist_id,
            session_date,
            notes
        ))

        self.cursor.execute("""
        UPDATE patients
        SET completed_sessions =
        completed_sessions + 1
        WHERE patient_id=?
        """, (patient_id,))

        self.conn.commit()

    # -----------------------------
    # PROGRESS
    # -----------------------------
    def patient_progress(self, patient_id):

        self.cursor.execute("""
        SELECT
        completed_sessions,
        total_sessions
        FROM patients
        WHERE patient_id=?
        """, (patient_id,))

        row = self.cursor.fetchone()

        if row:

            completed = row[0]
            total = row[1]

            if total == 0:
                return 0

            return round((completed / total) * 100, 2)

        return 0

    # -----------------------------
    # DASHBOARD COUNTS
    # -----------------------------
    def total_patients(self):
        self.cursor.execute("SELECT COUNT(*) FROM patients")
        return self.cursor.fetchone()[0]

    def total_therapists(self):
        self.cursor.execute("SELECT COUNT(*) FROM therapists")
        return self.cursor.fetchone()[0]

    def total_appointments(self):
        self.cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE status='Booked'
        """)
        return self.cursor.fetchone()[0]

    def total_sessions(self):
        self.cursor.execute("""
        SELECT COUNT(*)
        FROM therapy_sessions
        """)
        return self.cursor.fetchone()[0]

    def close(self):
        self.conn.close()




import streamlit as st
import pandas as pd
from database import Database

# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------
st.set_page_config(
    page_title="Rehabilitation Management System",
    page_icon="🏥",
    layout="wide"
)

db = Database()

# -----------------------------------
# HEADER
# -----------------------------------
st.title("🏥 Rehabilitation Management System")
st.markdown("### Dashboard")

st.divider()

# -----------------------------------
# DASHBOARD METRICS
# -----------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Patients",
        value=db.total_patients()
    )

with col2:
    st.metric(
        label="Therapists",
        value=db.total_therapists()
    )

with col3:
    st.metric(
        label="Appointments",
        value=db.total_appointments()
    )

with col4:
    st.metric(
        label="Therapy Sessions",
        value=db.total_sessions()
    )

st.divider()

# -----------------------------------
# PATIENTS TABLE
# -----------------------------------
st.subheader("Registered Patients")

patients = db.get_patients()

if patients:

    patient_df = pd.DataFrame(
        patients,
        columns=[
            "Patient ID",
            "Full Name",
            "Age",
            "Gender",
            "Phone",
            "Email",
            "Addiction",
            "Admission Date",
            "Completed Sessions",
            "Total Sessions"
        ]
    )

    st.dataframe(
        patient_df,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No patients registered.")

st.divider()

# -----------------------------------
# UPCOMING APPOINTMENTS
# -----------------------------------
st.subheader("Upcoming Appointments")

appointments = db.upcoming_appointments()

if appointments:

    appointment_df = pd.DataFrame(
        appointments,
        columns=[
            "Appointment ID",
            "Patient ID",
            "Therapist ID",
            "Date",
            "Time",
            "Status"
        ]
    )

    st.dataframe(
        appointment_df,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No appointments booked.")

st.divider()

# -----------------------------------
# QUICK SEARCH
# -----------------------------------
st.subheader("Search Patient")

search = st.text_input(
    "Search by Patient ID or Name"
)

if search:

    results = db.search_patient(search)

    if results:

        result_df = pd.DataFrame(
            results,
            columns=[
                "Patient ID",
                "Full Name",
                "Age",
                "Gender",
                "Phone",
                "Email",
                "Addiction",
                "Admission Date",
                "Completed Sessions",
                "Total Sessions"
            ]
        )

        st.success(f"{len(results)} patient(s) found.")

        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.warning("No matching patient found.")

st.divider()

# -----------------------------------
# SIDEBAR
# -----------------------------------
st.sidebar.title("Navigation")

st.sidebar.success("Select a page from the sidebar.")

st.sidebar.markdown("""
### Available Pages

- Patients
- Therapists
- Appointments
- Therapy Sessions
- Treatment Progress
- Reports
""")

st.sidebar.info(
    "The pages folder will automatically appear "
    "here once created."
)

# -----------------------------------
# FOOTER
# -----------------------------------
st.markdown("---")
st.caption("Rehabilitation Management System | Streamlit + SQLite")


def get_patient_by_id(self, patient_id):
    self.cursor.execute(
        "SELECT * FROM patients WHERE patient_id=?",
        (patient_id,)
    )
    return self.cursor.fetchone()

import streamlit as st
import pandas as pd
from database import Database

db = Database()

st.set_page_config(
    page_title="Patients",
    page_icon="🧑‍⚕️",
    layout="wide"
)

st.title("🧑‍⚕️ Patient Management")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Add Patient",
        "View Patients",
        "Update Patient",
        "Delete Patient"
    ]
)

# ------------------------------------------------
# ADD PATIENT
# ------------------------------------------------
with tab1:

    st.subheader("Register New Patient")

    with st.form("add_patient_form"):

        name = st.text_input("Full Name")

        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120
        )

        gender = st.selectbox(
            "Gender",
            ["Male", "Female", "Other"]
        )

        phone = st.text_input("Phone")

        email = st.text_input("Email")

        addiction = st.text_input("Condition / Addiction")

        admission_date = st.date_input("Admission Date")

        submitted = st.form_submit_button("Add Patient")

        if submitted:

            if name.strip() == "":
                st.error("Patient name is required.")

            else:

                db.add_patient(
                    name,
                    age,
                    gender,
                    phone,
                    email,
                    addiction,
                    str(admission_date)
                )

                st.success("Patient added successfully.")

# ------------------------------------------------
# VIEW PATIENTS
# ------------------------------------------------
with tab2:

    st.subheader("Patient List")

    search = st.text_input("Search by ID or Name")

    if search:
        patients = db.search_patient(search)
    else:
        patients = db.get_patients()

    if patients:

        df = pd.DataFrame(
            patients,
            columns=[
                "ID",
                "Name",
                "Age",
                "Gender",
                "Phone",
                "Email",
                "Condition",
                "Admission Date",
                "Completed",
                "Total"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No patients found.")

# ------------------------------------------------
# UPDATE PATIENT
# ------------------------------------------------
with tab3:

    st.subheader("Update Patient")

    patient_id = st.number_input(
        "Patient ID",
        min_value=1,
        step=1
    )

    if st.button("Load Patient"):

        patient = db.get_patient_by_id(patient_id)

        if patient:

            st.session_state["patient"] = patient

        else:
            st.error("Patient not found.")

    if "patient" in st.session_state:

        patient = st.session_state["patient"]

        with st.form("update_form"):

            name = st.text_input(
                "Full Name",
                value=patient[1]
            )

            age = st.number_input(
                "Age",
                value=int(patient[2])
            )

            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"],
                index=["Male", "Female", "Other"].index(patient[3])
                if patient[3] in ["Male", "Female", "Other"] else 0
            )

            phone = st.text_input(
                "Phone",
                value=patient[4]
            )

            email = st.text_input(
                "Email",
                value=patient[5]
            )

            addiction = st.text_input(
                "Condition",
                value=patient[6]
            )

            update = st.form_submit_button("Update Patient")

            if update:

                db.update_patient(
                    patient_id,
                    name,
                    age,
                    gender,
                    phone,
                    email,
                    addiction
                )

                st.success("Patient updated successfully.")

                del st.session_state["patient"]

# ------------------------------------------------
# DELETE PATIENT
# ------------------------------------------------
with tab4:

    st.subheader("Delete Patient")

    delete_id = st.number_input(
        "Patient ID to Delete",
        min_value=1,
        step=1,
        key="delete_patient"
    )

    if st.button("Delete Patient"):

        patient = db.get_patient_by_id(delete_id)

        if patient:

            db.delete_patient(delete_id)

            st.success("Patient deleted successfully.")

        else:

            st.error("Patient not found.")


# -----------------------------
# GET THERAPIST BY ID
# -----------------------------
def get_therapist_by_id(self, therapist_id):

    self.cursor.execute(
        "SELECT * FROM therapists WHERE therapist_id=?",
        (therapist_id,)
    )

    return self.cursor.fetchone()


# -----------------------------
# UPDATE THERAPIST
# -----------------------------
def update_therapist(
        self,
        therapist_id,
        full_name,
        specialization,
        phone,
        email):

    self.cursor.execute("""
    UPDATE therapists
    SET
        full_name=?,
        specialization=?,
        phone=?,
        email=?
    WHERE therapist_id=?
    """,
    (
        full_name,
        specialization,
        phone,
        email,
        therapist_id
    ))

    self.conn.commit()


    import streamlit as st
import pandas as pd
from database import Database
from datetime import date

db = Database()

st.set_page_config(
    page_title="Therapists",
    page_icon="👨‍⚕️",
    layout="wide"
)

st.title("👨‍⚕️ Therapist Management")

tabs = st.tabs([
    "Add Therapist",
    "View Therapists",
    "Update Therapist",
    "Delete Therapist",
    "Assign Patient"
])

# ---------------------------------------------------
# ADD THERAPIST
# ---------------------------------------------------
with tabs[0]:

    st.subheader("Register Therapist")

    with st.form("add_therapist"):

        name = st.text_input("Full Name")

        specialization = st.text_input("Specialization")

        phone = st.text_input("Phone")

        email = st.text_input("Email")

        submit = st.form_submit_button("Save")

        if submit:

            if name.strip() == "":
                st.error("Therapist name is required.")

            else:

                db.add_therapist(
                    name,
                    specialization,
                    phone,
                    email
                )

                st.success("Therapist added successfully.")

# ---------------------------------------------------
# VIEW THERAPISTS
# ---------------------------------------------------
with tabs[1]:

    st.subheader("Therapist List")

    therapists = db.get_therapists()

    if therapists:

        df = pd.DataFrame(
            therapists,
            columns=[
                "ID",
                "Name",
                "Specialization",
                "Phone",
                "Email"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No therapists available.")

# ---------------------------------------------------
# UPDATE THERAPIST
# ---------------------------------------------------
with tabs[2]:

    therapist_id = st.number_input(
        "Therapist ID",
        min_value=1,
        step=1
    )

    if st.button("Load Therapist"):

        therapist = db.get_therapist_by_id(therapist_id)

        if therapist:

            st.session_state["therapist"] = therapist

        else:
            st.error("Therapist not found.")

    if "therapist" in st.session_state:

        therapist = st.session_state["therapist"]

        with st.form("update_therapist"):

            name = st.text_input(
                "Name",
                therapist[1]
            )

            specialization = st.text_input(
                "Specialization",
                therapist[2]
            )

            phone = st.text_input(
                "Phone",
                therapist[3]
            )

            email = st.text_input(
                "Email",
                therapist[4]
            )

            update = st.form_submit_button("Update")

            if update:

                db.update_therapist(
                    therapist_id,
                    name,
                    specialization,
                    phone,
                    email
                )

                st.success("Therapist updated.")

                del st.session_state["therapist"]

# ---------------------------------------------------
# DELETE THERAPIST
# ---------------------------------------------------
with tabs[3]:

    therapist_id = st.number_input(
        "Therapist ID to Delete",
        min_value=1,
        step=1,
        key="delete"
    )

    if st.button("Delete Therapist"):

        therapist = db.get_therapist_by_id(
            therapist_id
        )

        if therapist:

            db.delete_therapist(therapist_id)

            st.success("Therapist deleted.")

        else:

            st.error("Therapist not found.")

# ---------------------------------------------------
# ASSIGN PATIENT
# ---------------------------------------------------
with tabs[4]:

    st.subheader("Assign Patient")

    patients = db.get_patients()
    therapists = db.get_therapists()

    if not patients:

        st.warning("No patients registered.")

    elif not therapists:

        st.warning("No therapists registered.")

    else:

        patient_dict = {
            f"{p[0]} - {p[1]}": p[0]
            for p in patients
        }

        therapist_dict = {
            f"{t[0]} - {t[1]}": t[0]
            for t in therapists
        }

        patient = st.selectbox(
            "Patient",
            list(patient_dict.keys())
        )

        therapist = st.selectbox(
            "Therapist",
            list(therapist_dict.keys())
        )

        if st.button("Assign"):

            db.assign_patient(
                patient_dict[patient],
                therapist_dict[therapist],
                str(date.today())
            )

            st.success("Patient assigned successfully.")


            # -----------------------------
# GET ALL APPOINTMENTS
# -----------------------------
def get_appointments(self):

    self.cursor.execute("""
    SELECT
        a.appointment_id,
        p.full_name,
        t.full_name,
        a.appointment_date,
        a.appointment_time,
        a.status
    FROM appointments a
    JOIN patients p
        ON a.patient_id = p.patient_id
    JOIN therapists t
        ON a.therapist_id = t.therapist_id
    ORDER BY a.appointment_date, a.appointment_time
    """)

    return self.cursor.fetchall()


# -----------------------------
# GET APPOINTMENT BY ID
# -----------------------------
def get_appointment(self, appointment_id):

    self.cursor.execute("""
    SELECT *
    FROM appointments
    WHERE appointment_id=?
    """, (appointment_id,))

    return self.cursor.fetchone()


# -----------------------------
# APPOINTMENT HISTORY
# -----------------------------
def appointment_history(self):

    self.cursor.execute("""
    SELECT
        a.appointment_id,
        p.full_name,
        t.full_name,
        a.appointment_date,
        a.appointment_time,
        a.status
    FROM appointments a
    JOIN patients p
        ON a.patient_id=p.patient_id
    JOIN therapists t
        ON a.therapist_id=t.therapist_id
    ORDER BY a.appointment_date DESC
    """)

    return self.cursor.fetchall()

import streamlit as st
import pandas as pd
from database import Database

db = Database()

st.set_page_config(
    page_title="Appointments",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Therapy Appointments")

tab1, tab2, tab3 = st.tabs(
    [
        "Book Appointment",
        "Upcoming Appointments",
        "Appointment History"
    ]
)

# ------------------------------------------------
# BOOK APPOINTMENT
# ------------------------------------------------
with tab1:

    st.subheader("Book Therapy Appointment")

    patients = db.get_patients()
    therapists = db.get_therapists()

    if not patients:
        st.warning("Please register patients first.")

    elif not therapists:
        st.warning("Please register therapists first.")

    else:

        patient_dict = {
            f"{p[0]} - {p[1]}": p[0]
            for p in patients
        }

        therapist_dict = {
            f"{t[0]} - {t[1]}": t[0]
            for t in therapists
        }

        with st.form("appointment_form"):

            patient = st.selectbox(
                "Patient",
                list(patient_dict.keys())
            )

            therapist = st.selectbox(
                "Therapist",
                list(therapist_dict.keys())
            )

            appointment_date = st.date_input(
                "Appointment Date"
            )

            appointment_time = st.time_input(
                "Appointment Time"
            )

            submit = st.form_submit_button(
                "Book Appointment"
            )

            if submit:

                db.book_appointment(
                    patient_dict[patient],
                    therapist_dict[therapist],
                    str(appointment_date),
                    appointment_time.strftime("%H:%M")
                )

                st.success(
                    "Appointment booked successfully."
                )

# ------------------------------------------------
# UPCOMING APPOINTMENTS
# ------------------------------------------------
with tab2:

    st.subheader("Upcoming Appointments")

    appointments = db.get_appointments()

    if appointments:

        df = pd.DataFrame(
            appointments,
            columns=[
                "Appointment ID",
                "Patient",
                "Therapist",
                "Date",
                "Time",
                "Status"
            ]
        )

        status = st.selectbox(
            "Filter by Status",
            ["All", "Booked", "Cancelled"]
        )

        if status != "All":
            df = df[df["Status"] == status]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Cancel Appointment")

        appointment_id = st.number_input(
            "Appointment ID",
            min_value=1,
            step=1
        )

        if st.button("Cancel Appointment"):

            appointment = db.get_appointment(
                appointment_id
            )

            if appointment:

                db.cancel_appointment(
                    appointment_id
                )

                st.success(
                    "Appointment cancelled."
                )

            else:

                st.error(
                    "Appointment not found."
                )

    else:
        st.info("No appointments available.")

# ------------------------------------------------
# APPOINTMENT HISTORY
# ------------------------------------------------
with tab3:

    st.subheader("Appointment History")

    history = db.appointment_history()

    if history:

        history_df = pd.DataFrame(
            history,
            columns=[
                "Appointment ID",
                "Patient",
                "Therapist",
                "Date",
                "Time",
                "Status"
            ]
        )

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No appointment history available."
        )

        # -----------------------------
# GET ALL THERAPY SESSIONS
# -----------------------------
def get_sessions(self):

    self.cursor.execute("""
    SELECT
        s.session_id,
        p.full_name,
        t.full_name,
        s.session_date,
        s.notes
    FROM therapy_sessions s
    JOIN patients p
        ON s.patient_id = p.patient_id
    JOIN therapists t
        ON s.therapist_id = t.therapist_id
    ORDER BY s.session_date DESC
    """)

    return self.cursor.fetchall()


# -----------------------------
# SEARCH SESSIONS
# -----------------------------
def search_sessions(self, keyword):

    self.cursor.execute("""
    SELECT
        s.session_id,
        p.full_name,
        t.full_name,
        s.session_date,
        s.notes
    FROM therapy_sessions s
    JOIN patients p
        ON s.patient_id = p.patient_id
    JOIN therapists t
        ON s.therapist_id = t.therapist_id
    WHERE p.full_name LIKE ?
    ORDER BY s.session_date DESC
    """, (f"%{keyword}%",))

    return self.cursor.fetchall()

import streamlit as st
import pandas as pd
from database import Database
from datetime import date

db = Database()

st.set_page_config(
    page_title="Therapy Sessions",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Therapy Sessions")

tab1, tab2, tab3 = st.tabs([
    "Record Session",
    "Session History",
    "Treatment Progress"
])

# --------------------------------------------------
# RECORD SESSION
# --------------------------------------------------
with tab1:

    patients = db.get_patients()
    therapists = db.get_therapists()

    if not patients:

        st.warning("No patients registered.")

    elif not therapists:

        st.warning("No therapists registered.")

    else:

        patient_dict = {
            f"{p[0]} - {p[1]}": p[0]
            for p in patients
        }

        therapist_dict = {
            f"{t[0]} - {t[1]}": t[0]
            for t in therapists
        }

        with st.form("session_form"):

            patient = st.selectbox(
                "Patient",
                list(patient_dict.keys())
            )

            therapist = st.selectbox(
                "Therapist",
                list(therapist_dict.keys())
            )

            session_date = st.date_input(
                "Session Date",
                value=date.today()
            )

            notes = st.text_area(
                "Session Notes"
            )

            submit = st.form_submit_button(
                "Record Session"
            )

            if submit:

                db.record_session(
                    patient_dict[patient],
                    therapist_dict[therapist],
                    str(session_date),
                    notes
                )

                st.success(
                    "Therapy session recorded successfully."
                )

# --------------------------------------------------
# SESSION HISTORY
# --------------------------------------------------
with tab2:

    st.subheader("Session History")

    keyword = st.text_input(
        "Search by Patient Name"
    )

    if keyword:

        sessions = db.search_sessions(keyword)

    else:

        sessions = db.get_sessions()

    if sessions:

        df = pd.DataFrame(
            sessions,
            columns=[
                "Session ID",
                "Patient",
                "Therapist",
                "Date",
                "Notes"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No therapy sessions found.")

# --------------------------------------------------
# TREATMENT PROGRESS
# --------------------------------------------------
with tab3:

    st.subheader("Treatment Progress")

    patients = db.get_patients()

    if patients:

        for patient in patients:

            patient_id = patient[0]
            patient_name = patient[1]

            progress = db.patient_progress(
                patient_id
            )

            st.markdown(f"### {patient_name}")

            st.progress(progress / 100)

            st.write(
                f"Progress: **{progress:.2f}%**"
            )

            st.divider()

    else:

        st.info(
            "No patients available."
        )

        import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import Database

db = Database()

st.set_page_config(
    page_title="Reports",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Rehabilitation Reports")

# ----------------------------------------
# LOAD DATA
# ----------------------------------------

patients = db.get_patients()
therapists = db.get_therapists()
appointments = db.get_appointments()
sessions = db.get_sessions()

# ----------------------------------------
# SUMMARY METRICS
# ----------------------------------------

st.subheader("System Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Patients", len(patients))

with col2:
    st.metric("Therapists", len(therapists))

with col3:
    st.metric("Appointments", len(appointments))

with col4:
    st.metric("Therapy Sessions", len(sessions))

st.divider()

# ----------------------------------------
# PATIENT REPORT
# ----------------------------------------

st.subheader("Patient Report")

if patients:

    patient_df = pd.DataFrame(
        patients,
        columns=[
            "Patient ID",
            "Name",
            "Age",
            "Gender",
            "Phone",
            "Email",
            "Condition",
            "Admission Date",
            "Completed Sessions",
            "Total Sessions"
        ]
    )

    st.dataframe(
        patient_df,
        use_container_width=True
    )

    csv = patient_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download Patient Report (CSV)",
        csv,
        "patients_report.csv",
        "text/csv"
    )

else:

    st.info("No patient records available.")

st.divider()

# ----------------------------------------
# GENDER DISTRIBUTION
# ----------------------------------------

if patients:

    st.subheader("Gender Distribution")

    gender_counts = patient_df["Gender"].value_counts()

    fig, ax = plt.subplots()

    ax.pie(
        gender_counts,
        labels=gender_counts.index,
        autopct="%1.1f%%"
    )

    ax.set_title("Patients by Gender")

    st.pyplot(fig)

st.divider()

# ----------------------------------------
# PATIENT PROGRESS
# ----------------------------------------

st.subheader("Treatment Progress")

if patients:

    names = []
    progress = []

    for patient in patients:

        names.append(patient[1])
        progress.append(
            db.patient_progress(patient[0])
        )

    fig, ax = plt.subplots(figsize=(10,5))

    ax.bar(names, progress)

    ax.set_ylabel("Progress (%)")
    ax.set_xlabel("Patients")
    ax.set_title("Treatment Progress")

    plt.xticks(rotation=45)

    st.pyplot(fig)

st.divider()

# ----------------------------------------
# APPOINTMENT STATUS
# ----------------------------------------

st.subheader("Appointment Status")

if appointments:

    appointment_df = pd.DataFrame(
        appointments,
        columns=[
            "Appointment ID",
            "Patient",
            "Therapist",
            "Date",
            "Time",
            "Status"
        ]
    )

    status = appointment_df["Status"].value_counts()

    fig, ax = plt.subplots()

    ax.bar(
        status.index,
        status.values
    )

    ax.set_title("Appointments")

    ax.set_ylabel("Number")

    st.pyplot(fig)

st.divider()

# ----------------------------------------
# THERAPIST LIST
# ----------------------------------------

st.subheader("Therapists")

if therapists:

    therapist_df = pd.DataFrame(
        therapists,
        columns=[
            "ID",
            "Name",
            "Specialization",
            "Phone",
            "Email"
        ]
    )

    st.dataframe(
        therapist_df,
        use_container_width=True
    )

else:

    st.info("No therapists found.")