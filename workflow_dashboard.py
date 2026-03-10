import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------
# Page Config
# -----------------------
st.set_page_config(
    page_title="DocuWare Workflow Dashboard",
    layout="wide"
)
st.title("DocuWare Workflow Analytics Dashboard")
st.markdown("Analyze workflow bottlenecks and workflow performance")

# -----------------------
# Background
# -----------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #87CEEB;  /* Sky Blue */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------
# Load Dataset
# -----------------------
df = pd.read_csv("workflow_completed_steps.csv", sep=";")
df.columns = df.columns.str.strip()  # Remove spaces
df['completion_time'] = pd.to_datetime(df['completion_time'])

# Sort and calculate durations
df = df.sort_values(['workflow_ID','step_order'])
df['prev_time'] = df.groupby('workflow_ID')['completion_time'].shift(1)
df['duration_minutes'] = (df['completion_time'] - df['prev_time']).dt.total_seconds() / 60

# -----------------------
# Sidebar Filters
# -----------------------
st.sidebar.header("Filters")
workflow_filter = st.sidebar.selectbox("Select Workflow", ["All"] + list(df['workflow_ID'].unique()))
step_type_filter = st.sidebar.selectbox("Select Step Type", ["All"] + list(df['step_type'].unique()))

filtered_df = df.copy()
if workflow_filter != "All":
    filtered_df = filtered_df[filtered_df['workflow_ID'] == workflow_filter]
if step_type_filter != "All":
    filtered_df = filtered_df[filtered_df['step_type'] == step_type_filter]

# -----------------------
# KPI Cards
# -----------------------
total_workflows = filtered_df['workflow_ID'].nunique()
avg_duration = round(filtered_df['duration_minutes'].mean(), 2)
longest_step = round(filtered_df['duration_minutes'].max(), 2)

st.subheader("Key Metrics")
st.markdown(
    f"""
    <div style="display:flex; gap:20px; margin-bottom:20px;">
        <div style="background-color:white; padding:20px; border-radius:10px; flex:1; text-align:center; box-shadow:2px 2px 10px rgba(0,0,0,0.1);">
            <h3>Total Workflows</h3>
            <h2>{total_workflows}</h2>
        </div>
        <div style="background-color:white; padding:20px; border-radius:10px; flex:1; text-align:center; box-shadow:2px 2px 10px rgba(0,0,0,0.1);">
            <h3>Average Step Duration (min)</h3>
            <h2>{avg_duration}</h2>
        </div>
        <div style="background-color:white; padding:20px; border-radius:10px; flex:1; text-align:center; box-shadow:2px 2px 10px rgba(0,0,0,0.1);">
            <h3>Longest Step Duration (min)</h3>
            <h2>{longest_step}</h2>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------
# Top Bottleneck Steps
# -----------------------
st.subheader("Top 10 Bottleneck Steps")
bottlenecks = (
    filtered_df.groupby('step_name')['duration_minutes']
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

# Color gradient: green = fast, red = slow
max_duration = bottlenecks.max()
min_duration = bottlenecks.min()
colors = [( (d - min_duration) / (max_duration - min_duration), 1-(d - min_duration) / (max_duration - min_duration), 0) for d in bottlenecks]

fig, ax = plt.subplots(figsize=(8,5))
bottlenecks.sort_values().plot(kind='barh', ax=ax, color=colors)
ax.set_xlabel("Average Duration (min)")
ax.set_ylabel("Step Name")
ax.set_title("Top Workflow Bottlenecks", color='black')
st.pyplot(fig)

# -----------------------
# Step Type Analysis
# -----------------------
st.subheader("Step Type Distribution")
step_counts = filtered_df['step_type'].value_counts()
fig2, ax2 = plt.subplots(figsize=(6,4))
color_palette = plt.cm.tab10.colors
colors2 = [color_palette[i % 10] for i in range(len(step_counts))]
step_counts.plot(kind='bar', color=colors2, ax=ax2)
ax2.set_ylabel("Count")
ax2.set_xlabel("Step Type")
st.pyplot(fig2)

# -----------------------
# Workflow Trend Over Time
# -----------------------
st.subheader("Workflow Activity Over Time")
filtered_df['date'] = filtered_df['completion_time'].dt.date
trend = filtered_df.groupby('date')['workflow_ID'].nunique()
fig3, ax3 = plt.subplots(figsize=(10,4))
trend.plot(kind='line', marker='o', color='mediumblue', linewidth=2, ax=ax3)
ax3.set_ylabel("Number of Workflows")
ax3.set_xlabel("Date")
st.pyplot(fig3)

# -----------------------
# Raw Data Table
# -----------------------
st.subheader("Workflow Details")

st.dataframe(filtered_df)
