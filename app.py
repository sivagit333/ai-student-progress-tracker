import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AI Student Progress Tracker",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Student Progress Tracker")
st.write("Track and analyze student learning progress.")

# Load student data
students = pd.read_csv("data/students.csv")

# Calculate average score
score_columns = ["python", "sql", "projects"]
students["Average Score"] = students[score_columns].mean(axis=1)

# Determine performance level
def get_performance(score):
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    else:
        return "Needs Improvement"

students["Performance"] = students["Average Score"].apply(get_performance)

# -----------------------------
# Dashboard Metrics
# -----------------------------

total_students = len(students)
overall_average = students["Average Score"].mean()
excellent_students = (students["Performance"] == "Excellent").sum()
needs_improvement = (students["Performance"] == "Needs Improvement").sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("👨‍🎓 Total Students", total_students)
col2.metric("📊 Average Score", f"{overall_average:.2f}")
col3.metric("🏆 Excellent", excellent_students)
col4.metric("⚠️ Needs Improvement", needs_improvement)

# -----------------------------
# Student Performance Table
# -----------------------------

st.subheader("📈 Student Performance")

st.dataframe(
    students,
    use_container_width=True
)

# -----------------------------
# Individual Student Analysis
# -----------------------------

st.subheader("👤 Individual Student Analysis")

selected_student = st.selectbox(
    "Select a student",
    students["name"]
)

student = students[students["name"] == selected_student].iloc[0]

st.write(f"### 📋 {student['name']}'s Performance")

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