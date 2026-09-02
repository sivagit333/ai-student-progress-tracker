import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Student Progress Tracker",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# SUPABASE CONNECTION
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase credentials are missing. Please check your .env file.")
    st.stop()

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ============================================================
# LOAD STUDENTS
# ============================================================

def load_students():

    response = (
        supabase
        .table("students")
        .select(
            "student_id, name, grade, python, sql, projects"
        )
        .execute()
    )

    return pd.DataFrame(response.data)


# ============================================================
# LOAD PROGRESS HISTORY
# ============================================================

def load_progress_history(student_id):

    response = (
        supabase
        .table("progress_history")
        .select(
            "student_id, recorded_date, python, sql, projects"
        )
        .eq(
            "student_id",
            student_id
        )
        .order(
            "recorded_date"
        )
        .execute()
    )

    # Always return the expected columns
    # even when there are no records.
    columns = [
        "student_id",
        "recorded_date",
        "python",
        "sql",
        "projects"
    ]

    return pd.DataFrame(
        response.data,
        columns=columns
    )


# ============================================================
# CALCULATE PERFORMANCE
# ============================================================

def calculate_performance(students):

    if students.empty:
        return students

    score_columns = [
        "python",
        "sql",
        "projects"
    ]

    students["Average Score"] = (
        students[score_columns]
        .mean(axis=1)
    )

    def get_performance(score):

        if score >= 85:
            return "Excellent"

        elif score >= 70:
            return "Good"

        return "Needs Improvement"

    students["Performance"] = (
        students["Average Score"]
        .apply(get_performance)
    )

    return students


# ============================================================
# LOAD DATA
# ============================================================

students = load_students()

students = calculate_performance(
    students
)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("📊 AI Student Progress Tracker")

st.write(
    "Track and analyze student learning progress."
)


# ============================================================
# ADD STUDENT
# ============================================================

st.sidebar.header("➕ Add Student")

with st.sidebar.form("student_form"):

    student_id = st.text_input(
        "Student ID"
    )

    name = st.text_input(
        "Student Name"
    )

    grade = st.number_input(
        "Grade",
        min_value=1,
        max_value=12,
        value=5
    )

    python_score = st.number_input(
        "Python Score",
        min_value=0,
        max_value=100,
        value=0
    )

    sql_score = st.number_input(
        "SQL Score",
        min_value=0,
        max_value=100,
        value=0
    )

    project_score = st.number_input(
        "Project Score",
        min_value=0,
        max_value=100,
        value=0
    )

    submitted = st.form_submit_button(
        "Add Student"
    )

    if submitted:

        if not student_id or not name:

            st.sidebar.error(
                "Student ID and Name are required."
            )

        elif (
            not students.empty
            and student_id in students["student_id"].values
        ):

            st.sidebar.error(
                "Student ID already exists."
            )

        else:

            try:

                supabase.table("students").insert({

                    "student_id": student_id,
                    "name": name,
                    "grade": grade,
                    "python": python_score,
                    "sql": sql_score,
                    "projects": project_score

                }).execute()

                st.sidebar.success(
                    f"{name} added successfully!"
                )

                st.rerun()

            except Exception as e:

                st.sidebar.error(
                    f"Error adding student: {e}"
                )


# ============================================================
# DASHBOARD METRICS
# ============================================================

if students.empty:

    total_students = 0
    overall_average = 0
    excellent_students = 0
    needs_improvement = 0

else:

    total_students = len(students)

    overall_average = (
        students["Average Score"].mean()
    )

    excellent_students = (
        students["Performance"] == "Excellent"
    ).sum()

    needs_improvement = (
        students["Performance"] == "Needs Improvement"
    ).sum()


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "👨‍🎓 Total Students",
    total_students
)

col2.metric(
    "📊 Average Score",
    f"{overall_average:.2f}"
)

col3.metric(
    "🏆 Excellent",
    excellent_students
)

col4.metric(
    "⚠️ Needs Improvement",
    needs_improvement
)


# ============================================================
# STUDENT PERFORMANCE
# ============================================================

st.subheader(
    "📈 Student Performance"
)

if students.empty:

    st.info(
        "No students found. Add a student using the sidebar."
    )

else:

    st.dataframe(
        students,
        use_container_width=True
    )


# ============================================================
# STUDENT MANAGEMENT
# ============================================================

st.subheader(
    "🛠️ Student Management"
)

if not students.empty:

    management_student = st.selectbox(

        "Select a student to manage",

        students["student_id"],

        format_func=lambda x:
            students.loc[
                students["student_id"] == x,
                "name"
            ].iloc[0],

        key="management_student"
    )

    selected_data = students[
        students["student_id"] == management_student
    ].iloc[0]


    # ========================================================
    # EDIT STUDENT
    # ========================================================

    with st.expander(
        "✏️ Edit Student"
    ):

        with st.form(
            "edit_student_form"
        ):

            edit_name = st.text_input(
                "Student Name",
                value=selected_data["name"]
            )

            edit_grade = st.number_input(
                "Grade",
                min_value=1,
                max_value=12,
                value=int(
                    selected_data["grade"]
                )
            )

            edit_python = st.number_input(
                "Python Score",
                min_value=0,
                max_value=100,
                value=int(
                    selected_data["python"]
                )
            )

            edit_sql = st.number_input(
                "SQL Score",
                min_value=0,
                max_value=100,
                value=int(
                    selected_data["sql"]
                )
            )

            edit_projects = st.number_input(
                "Project Score",
                min_value=0,
                max_value=100,
                value=int(
                    selected_data["projects"]
                )
            )

            update_button = st.form_submit_button(
                "💾 Update Student"
            )

            if update_button:

                try:

                    supabase.table(
                        "students"
                    ).update({

                        "name": edit_name,

                        "grade": edit_grade,

                        "python": edit_python,

                        "sql": edit_sql,

                        "projects": edit_projects

                    }).eq(
                        "student_id",
                        management_student
                    ).execute()

                    st.success(
                        f"{edit_name} updated successfully!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Error updating student: {e}"
                    )


    # ========================================================
    # DELETE STUDENT
    # ========================================================

    with st.expander(
        "🗑️ Delete Student"
    ):

        st.warning(
            f"You are about to delete "
            f"{selected_data['name']}."
        )

        delete_button = st.button(
            "🗑️ Delete Student",
            key="delete_student"
        )

        if delete_button:

            try:

                supabase.table(
                    "students"
                ).delete().eq(
                    "student_id",
                    management_student
                ).execute()

                st.success(
                    "Student deleted successfully!"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Error deleting student: {e}"
                )


# ============================================================
# INDIVIDUAL STUDENT ANALYSIS
# ============================================================

st.subheader(
    "👤 Individual Student Analysis"
)

if not students.empty:

    selected_student = st.selectbox(

        "Select a student",

        students["name"],

        key="analysis_student"
    )

    student = students[
        students["name"] == selected_student
    ].iloc[0]


    # ========================================================
    # LOAD PROGRESS HISTORY
    # ========================================================

    progress_history = load_progress_history(
        student["student_id"]
    )


    # ========================================================
    # CURRENT PERFORMANCE METRICS
    # ========================================================

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🐍 Python",
        student["python"]
    )

    col2.metric(
        "🗄️ SQL",
        student["sql"]
    )

    col3.metric(
        "📁 Projects",
        student["projects"]
    )

    st.metric(
        "📊 Average Score",
        f"{student['Average Score']:.2f}"
    )

    st.write(
        f"**Performance Level:** "
        f"{student['Performance']}"
    )


    # ========================================================
    # RECORD PROGRESS
    # ========================================================

    st.subheader(
        "📅 Record Progress"
    )

    if st.button(
        "💾 Record Current Progress",
        key="record_progress"
    ):

        try:

            supabase.table(
                "progress_history"
            ).insert({

                "student_id": student["student_id"],

                "python": int(student["python"]),

                "sql": int(student["sql"]),

                "projects": int(student["projects"])

            }).execute()

            st.success(
                f"Progress recorded successfully for "
                f"{student['name']}!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Error recording progress: {e}"
            )


    # ========================================================
    # PROGRESS HISTORY
    # ========================================================

    st.subheader(
        "📚 Progress History"
    )

    if progress_history.empty:

        st.info(
            "No progress history recorded yet. "
            "Click 'Record Current Progress' to create a record."
        )

    else:

        history_display = progress_history.copy()

        history_display["recorded_date"] = pd.to_datetime(
            history_display["recorded_date"]
        ).dt.strftime("%Y-%m-%d")

        history_display = history_display.rename(
            columns={
                "student_id": "Student ID",
                "recorded_date": "Date",
                "python": "Python",
                "sql": "SQL",
                "projects": "Projects"
            }
        )

        st.dataframe(
            history_display,
            use_container_width=True
        )


    # ========================================================
    # PROGRESS TREND ANALYSIS
    # ========================================================

    if not progress_history.empty:

        st.subheader(
            "📈 Progress Trend Analysis"
        )

        history_analysis = progress_history.copy()

        history_analysis["recorded_date"] = pd.to_datetime(
            history_analysis["recorded_date"]
        )

        # Calculate average score for each record
        history_analysis["average"] = (
            history_analysis[
                ["python", "sql", "projects"]
            ].mean(axis=1)
        )

        # Sort oldest to newest
        history_analysis = history_analysis.sort_values(
            "recorded_date"
        )

        # First and latest averages
        first_average = (
            history_analysis["average"].iloc[0]
        )

        latest_average = (
            history_analysis["average"].iloc[-1]
        )

        # Overall change
        improvement = (
            latest_average - first_average
        )


        # ====================================================
        # OVERALL PROGRESS METRICS
        # ====================================================

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "📌 First Average",
            f"{first_average:.2f}"
        )

        col2.metric(
            "📊 Latest Average",
            f"{latest_average:.2f}"
        )

        col3.metric(
            "🚀 Overall Change",
            f"{improvement:+.2f}"
        )


        # ====================================================
        # OVERALL PROGRESS STATUS
        # ====================================================

        if improvement > 2:

            st.success(
                f"🟢 {student['name']} is improving! "
                f"Overall performance increased by "
                f"{improvement:.2f} points."
            )

        elif improvement < -2:

            st.error(
                f"🔴 {student['name']}'s performance has "
                f"declined by {abs(improvement):.2f} points."
            )

        else:

            st.info(
                f"🟡 {student['name']}'s overall performance "
                f"is stable."
            )


        # ====================================================
        # SUBJECT-WISE PROGRESS
        # ====================================================

        st.subheader(
            "📚 Subject-wise Progress"
        )

        first_record = history_analysis.iloc[0]

        latest_record = history_analysis.iloc[-1]

        subject_progress = pd.DataFrame({

            "Subject": [
                "Python",
                "SQL",
                "Projects"
            ],

            "First Score": [
                first_record["python"],
                first_record["sql"],
                first_record["projects"]
            ],

            "Latest Score": [
                latest_record["python"],
                latest_record["sql"],
                latest_record["projects"]
            ]
        })


        subject_progress["Change"] = (
            subject_progress["Latest Score"]
            - subject_progress["First Score"]
        )


        # Subject progress status
        def get_subject_status(change):

            if change > 2:
                return "📈 Improving"

            elif change < -2:
                return "📉 Declining"

            return "➡️ Stable"


        subject_progress["Status"] = (
            subject_progress["Change"]
            .apply(get_subject_status)
        )


        st.dataframe(
            subject_progress,
            use_container_width=True,
            hide_index=True
        )


        # ====================================================
        # PROGRESS OVER TIME CHART
        # ====================================================

        st.subheader(
            "📈 Progress Over Time"
        )

        history_chart = progress_history.copy()

        history_chart["recorded_date"] = pd.to_datetime(
            history_chart["recorded_date"]
        )

        history_chart = history_chart.sort_values(
            "recorded_date"
        )

        history_chart = history_chart.set_index(
            "recorded_date"
        )[
            [
                "python",
                "sql",
                "projects"
            ]
        ]

        history_chart.columns = [
            "Python",
            "SQL",
            "Projects"
        ]

        st.line_chart(
            history_chart
        )


    # ========================================================
    # PERFORMANCE CHART
    # ========================================================

    st.subheader(
        "📊 Subject Performance"
    )

    chart_data = pd.DataFrame({

        "Subject": [
            "Python",
            "SQL",
            "Projects"
        ],

        "Score": [

            student["python"],

            student["sql"],

            student["projects"]

        ]

    })

    st.bar_chart(
        chart_data.set_index(
            "Subject"
        )
    )


    # ========================================================
    # LEARNING RECOMMENDATION
    # ========================================================

    st.subheader(
        "🤖 Learning Recommendation"
    )

    scores = {

        "Python": student["python"],

        "SQL": student["sql"],

        "Projects": student["projects"]

    }

    weakest_subject = min(
        scores,
        key=scores.get
    )

    weakest_score = scores[
        weakest_subject
    ]


    if weakest_score < 70:

        recommendation = (

            f"{student['name']} needs additional "
            f"practice in {weakest_subject}. "
            f"Consider assigning beginner-level "
            f"exercises and reviewing the fundamentals."

        )

    elif weakest_score < 85:

        recommendation = (

            f"{student['name']} is making good "
            f"progress in {weakest_subject}. "
            f"More practice could help improve "
            f"their confidence and performance."

        )

    else:

        recommendation = (

            f"{student['name']} is performing well "
            f"across all subjects. Consider giving "
            f"advanced {weakest_subject} challenges."

        )

    st.info(
        recommendation
    )


else:

    st.info(
        "Add a student to view individual analysis."
    )