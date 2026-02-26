import streamlit as st
import pandas as pd
import numpy as np

st.title("8-Week Course Workload Planner")

st.markdown(
"""
Estimate student workload and generate a weekly workload view.
Designed for all disciplines.
"""
)

# ------------------------------
# Global Assumptions
# ------------------------------
st.sidebar.header("Global Assumptions")

reading_pages_per_hour = st.sidebar.slider("Reading speed (pages/hour)", 5, 40, 15)
article_hours = st.sidebar.slider("Hours per academic article", 1.0, 6.0, 3.0)

# Discussion
st.sidebar.subheader("Discussion Hours")
discussion_standard = st.sidebar.slider("Standard written discussion", 0.5, 4.0, 2.0)
discussion_reflective = st.sidebar.slider("Reflective discussion", 0.5, 4.0, 1.5)
discussion_video = st.sidebar.slider("Video discussion", 1.0, 5.0, 2.5)
discussion_peer = st.sidebar.slider("Peer review", 1.5, 6.0, 3.5)

# Writing
st.sidebar.subheader("Writing Hours Per Page")
w_reflection = st.sidebar.slider("Personal reflection", 0.25, 3.0, 0.75)
w_academic_nosrc = st.sidebar.slider("Academic (no sources)", 0.5, 4.0, 1.25)
w_academic_sources = st.sidebar.slider("Academic (sources)", 0.75, 5.0, 1.75)
w_academic_journals = st.sidebar.slider("Academic (journal sources)", 1.0, 6.0, 2.25)

# ------------------------------
# Weekly Input
# ------------------------------
st.header("Enter Weekly Activities")

weeks = [f"Week {i}" for i in range(1, 9)]

data = {
    "Textbook Pages": [0]*8,
    "Literature Pages": [0]*8,
    "Academic Articles": [0]*8,
    "Writing Pages": [0]*8,
    "Writing Type": ["None"]*8,
    "Discussion Type": ["None"]*8,
    "Quiz/Exam Hours": [0]*8
}

df = pd.DataFrame(data, index=weeks)

df = st.data_editor(
    df,
    column_config={
        "Discussion Type": st.column_config.SelectboxColumn(
            options=["None","Standard Written","Reflective","Video","Peer Review"]
        ),
        "Writing Type": st.column_config.SelectboxColumn(
            options=[
                "None",
                "Personal reflection",
                "Academic (no sources)",
                "Academic (sources)",
                "Academic (journal sources)"
            ]
        )
    },
    use_container_width=True
)

# ------------------------------
# Calculations
# ------------------------------
reading_hours = (df["Textbook Pages"] + df["Literature Pages"]) / reading_pages_per_hour
research_hours = df["Academic Articles"] * article_hours

writing_hours = []
for wt, pages in zip(df["Writing Type"], df["Writing Pages"]):
    if wt == "Personal reflection":
        writing_hours.append(pages * w_reflection)
    elif wt == "Academic (no sources)":
        writing_hours.append(pages * w_academic_nosrc)
    elif wt == "Academic (sources)":
        writing_hours.append(pages * w_academic_sources)
    elif wt == "Academic (journal sources)":
        writing_hours.append(pages * w_academic_journals)
    else:
        writing_hours.append(0)
writing_hours = np.array(writing_hours)

discussion_hours = []
for d in df["Discussion Type"]:
    if d == "Standard Written":
        discussion_hours.append(discussion_standard)
    elif d == "Reflective":
        discussion_hours.append(discussion_reflective)
    elif d == "Video":
        discussion_hours.append(discussion_video)
    elif d == "Peer Review":
        discussion_hours.append(discussion_peer)
    else:
        discussion_hours.append(0)
discussion_hours = np.array(discussion_hours)

assessment_hours = df["Quiz/Exam Hours"]

total_hours = reading_hours + research_hours + writing_hours + discussion_hours + assessment_hours

results_df = pd.DataFrame({
    "Reading": reading_hours,
    "Research": research_hours,
    "Writing": writing_hours,
    "Discussion": discussion_hours,
    "Assessments": assessment_hours,
    "Total Hours": total_hours
}, index=weeks)

# ------------------------------
# Results
# ------------------------------
st.header("Results")

st.dataframe(results_df.round(2), use_container_width=True)

peak_week = results_df["Total Hours"].idxmax()
peak_value = results_df["Total Hours"].max()

st.metric("Peak Week", f"{peak_week} ({round(peak_value,1)} hrs)")

# Heat-style view
st.subheader("Weekly Workload (Heat View)")
st.bar_chart(results_df["Total Hours"])

# Category breakdown
st.subheader("Category Breakdown")
st.bar_chart(results_df[["Reading","Research","Writing","Discussion","Assessments"]])

# Interpretation
if peak_value > 20:
    st.warning("Very heavy peak week detected.")
elif peak_value > 18:
    st.info("Peak aligns with accelerated 8-week expectations.")
else:
    st.success("Workload appears balanced.")