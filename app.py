import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="AI Student Progress Tracker",
    page_icon="📊",
    layout="wide"
)

DATA_FILE = Path("data/students.csv")


def load_students():
    return pd.read_csv(DATA_FILE)


def calculate_performance(students):
    score_columns = ["python", "sql", "projects"]

    students["Average Score"] = students[score_columns].mean(axis=1)

    def get_performance(score):
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        return "Needs Improvement"

    students["Performance"] = students["Average Score"].apply(
        get_performance
    )

    return students


# Load data
students = load_students()
students = calculate_performance(students)


# -----------------------------
# Page Header
# -----------------------------

st.title("📊 AI Student Progress Tracker")
st.write("Track and analyze student learning progress.")


# -----------------------------
# Add Student
# -----------------------------

st.sidebar.header("➕ Add Student")

with st.sidebar.form("student_form"):

    student_id = st.text_input("Student ID")
    name = st.text_input("Student Name")
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

    submitted = st.form_submit_button("Add Student")

    if submitted:

        if not student_id or not name:
            st.sidebar.error("Student ID and Name are required.")

        elif student_id in students["student_id"].values:
            st.sidebar.error("Student ID already exists.")

        else:
            new_student = pd.DataFrame({
                "student_id": [student_id],
                "name": [name],
                "grade": [grade],
                "python": [python_score],
                "sql": [sql_score],
                "projects": [project_score]
            })

            new_student.to_csv(
                DATA_FILE,
                mode="a",
                header=False,
                index=False
            )

            st.sidebar.success(
                f"{name} added successfully!"
            )

            st.rerun()


# -----------------------------
# Dashboard Metrics
# -----------------------------

total_students = len(students)
overall_average = students["Average Score"].mean()
excellent_students = (
    students["Performance"] == "Excellent"
).sum()
needs_improvement = (
    students["Performance"] == "Needs Improvement"
).sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("👨‍🎓 Total Students", total_students)
col2.metric("📊 Average Score", f"{overall_average:.2f}")
col3.metric("🏆 Excellent", excellent_students)
col4.metric("⚠️ Needs Improvement", needs_improvement)


# -----------------------------
# Student Performance
# -----------------------------

st.subheader("📈 Student Performance")

st.dataframe(
    students,
    use_container_width=True
)

# -----------------------------
# Student Management
# -----------------------------

st.subheader("🛠️ Student Management")

management_student = st.selectbox(
    "Select a student to manage",
    students["student_id"],
    format_func=lambda x: students.loc[
        students["student_id"] == x, "name"
    ].iloc[0],
    key="management_student"
)

selected_data = students[
    students["student_id"] == management_student
].iloc[0]

with st.expander("✏️ Edit Student"):

    with st.form("edit_student_form"):

        edit_name = st.text_input(
            "Student Name",
            value=selected_data["name"]
        )

        edit_grade = st.number_input(
            "Grade",
            min_value=1,
            max_value=12,
            value=int(selected_data["grade"])
        )

        edit_python = st.number_input(
            "Python Score",
            min_value=0,
            max_value=100,
            value=int(selected_data["python"])
        )

        edit_sql = st.number_input(
            "SQL Score",
            min_value=0,
            max_value=100,
            value=int(selected_data["sql"])
        )

        edit_projects = st.number_input(
            "Project Score",
            min_value=0,
            max_value=100,
            value=int(selected_data["projects"])
        )

        update_button = st.form_submit_button(
            "💾 Update Student"
        )

        if update_button:

            students.loc[
                students["student_id"] == management_student,
                "name"
            ] = edit_name

            students.loc[
                students["student_id"] == management_student,
                "grade"
            ] = edit_grade

            students.loc[
                students["student_id"] == management_student,
                "python"
            ] = edit_python

            students.loc[
                students["student_id"] == management_student,
                "sql"
            ] = edit_sql

            students.loc[
                students["student_id"] == management_student,
                "projects"
            ] = edit_projects

            # Save only the original columns
            students[
                [
                    "student_id",
                    "name",
                    "grade",
                    "python",
                    "sql",
                    "projects"
                ]
            ].to_csv(
                DATA_FILE,
                index=False
            )

            st.success(
                f"{edit_name} updated successfully!"
            )

            st.rerun()


# -----------------------------
# Delete Student
# -----------------------------

with st.expander("🗑️ Delete Student"):

    st.warning(
        f"You are about to delete "
        f"{selected_data['name']}."
    )

    delete_button = st.button(
        "🗑️ Delete Student",
        key="delete_student"
    )

    if delete_button:

        students = students[
            students["student_id"] != management_student
        ]

        students[
            [
                "student_id",
                "name",
                "grade",
                "python",
                "sql",
                "projects"
            ]
        ].to_csv(
            DATA_FILE,
            index=False
        )

        st.success("Student deleted successfully!")

        st.rerun()


# -----------------------------
# Individual Student Analysis
# -----------------------------

st.subheader("👤 Individual Student Analysis")

selected_student = st.selectbox(
    "Select a student",
    students["name"]
)

student = students[
    students["name"] == selected_student
].iloc[0]

col1, col2, col3 = st.columns(3)

col1.metric("🐍 Python", student["python"])
col2.metric("🗄️ SQL", student["sql"])
col3.metric("📁 Projects", student["projects"])

st.metric(
    "📊 Average Score",
    f"{student['Average Score']:.2f}"
)

st.write(
    f"**Performance Level:** {student['Performance']}"
)


# -----------------------------
# Performance Chart
# -----------------------------

st.subheader("📊 Subject Performance")

chart_data = pd.DataFrame({
    "Subject": ["Python", "SQL", "Projects"],
    "Score": [
        student["python"],
        student["sql"],
        student["projects"]
    ]
})

st.bar_chart(
    chart_data.set_index("Subject")
)


# -----------------------------
# Learning Recommendation
# -----------------------------

st.subheader("🤖 Learning Recommendation")

scores = {
    "Python": student["python"],
    "SQL": student["sql"],
    "Projects": student["projects"]
}

weakest_subject = min(scores, key=scores.get)
weakest_score = scores[weakest_subject]

if weakest_score < 70:
    recommendation = (
        f"{student['name']} needs additional practice in "
        f"{weakest_subject}. Consider assigning beginner-level "
        f"exercises and reviewing the fundamentals."
    )
elif weakest_score < 85:
    recommendation = (
        f"{student['name']} is making good progress in "
        f"{weakest_subject}. More practice could help improve "
        f"their confidence and performance."
    )
else:
    recommendation = (
        f"{student['name']} is performing well across all subjects. "
        f"Consider giving advanced {weakest_subject} challenges."
    )

st.info(recommendation)