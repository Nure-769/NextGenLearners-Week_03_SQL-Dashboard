import streamlit as st
import pandas as pd
import sqlite3

# Page Configuration
st.set_page_config(page_title="NextGenLearners Dashboard", layout="wide")
st.title("📊 NextGenLearners Program Performance Dashboard")
st.markdown("Interactive performance tracker for applications, completions, and hackathon scores.")

# Connect to Database
conn = sqlite3.connect('nextgen.db')

applicants = pd.read_sql("SELECT * FROM applicants;", conn)
interns = pd.read_sql("SELECT * FROM interns;", conn)
scores = pd.read_sql("SELECT * FROM hackathon_scores;", conn)

# Interactive Filter (Domain Dropdown)
domain_list = ['All'] + sorted([str(d) for d in applicants['domain'].dropna().unique().tolist()])
selected_domain = st.selectbox('Select Domain Filter', domain_list)

# Filter Data Based on Selection
if selected_domain != 'All':
    app_filtered = applicants[applicants['domain'] == selected_domain]
    int_filtered = interns[interns['domain'] == selected_domain]
    scores_filtered = scores[scores['domain'] == selected_domain]
else:
    app_filtered = applicants
    int_filtered = interns
    scores_filtered = scores

# 1. Funnel Summary Metrics
st.subheader("1. Applicant & Intern Funnel")
col1, col2, col3 = st.columns(3)
col1.metric("Total Applicants", len(app_filtered))
col2.metric("Total Interns Enrolled", len(int_filtered))
completed_count = len(int_filtered[int_filtered['completion_status'] == 'Completed'])
col3.metric("Completed Interns", completed_count)

st.divider()

# 2. Charts
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("2. Completion Count by Domain")
    q_completion = """
    SELECT domain, COUNT(*) AS completed_count
    FROM interns
    WHERE completion_status = 'Completed'
    GROUP BY domain;
    """
    df_comp = pd.read_sql(q_completion, conn)
    if selected_domain != 'All':
        df_comp = df_comp[df_comp['domain'] == selected_domain]
    st.bar_chart(df_comp.set_index('domain'))

with col_b:
    st.subheader("3. Average Hackathon Score")
    q_avg = """
    SELECT domain, ROUND(AVG(score), 2) AS avg_score
    FROM hackathon_scores
    GROUP BY domain;
    """
    df_avg = pd.read_sql(q_avg, conn)
    if selected_domain != 'All':
        df_avg = df_avg[df_avg['domain'] == selected_domain]
    st.bar_chart(df_avg.set_index('domain'))

st.divider()

# 3. Leaderboard
st.subheader("🏆 Top Performers Leaderboard")
q_leaderboard = """
SELECT i.intern_id, i.domain, h.score
FROM interns i
JOIN hackathon_scores h ON i.intern_id = h.intern_id
ORDER BY h.score DESC
LIMIT 10;
"""
df_leaderboard = pd.read_sql(q_leaderboard, conn)
if selected_domain != 'All':
    df_leaderboard = df_leaderboard[df_leaderboard['domain'] == selected_domain]

st.dataframe(df_leaderboard, use_container_width=True)

conn.close()