import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("CSV Data Visualizer for EV Telemetry")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, delimiter=';')

    # Show raw data with filter/search
    st.subheader("📋 Filterable Data Table")
    st.dataframe(df)

    # Custom Graph Section
    st.subheader("📊 Custom Graphs")
    col1, col2, col3 = st.columns(3)
    with col1:
        x_axis = st.selectbox("Select X-axis", df.columns)
    with col2:
        y1_axis = st.selectbox("Select Primary Y-axis", df.columns)
    with col3:
        y2_axis = st.selectbox("Select Secondary Y-axis (optional)", ["None"] + list(df.columns))

    fig, ax1 = plt.subplots()
    ax1.set_xlabel(x_axis)
    ax1.set_ylabel(y1_axis, color="blue")
    ax1.plot(df[x_axis], df[y1_axis], color="blue", label=y1_axis)

    if y2_axis != "None":
        ax2 = ax1.twinx()
        ax2.set_ylabel(y2_axis, color="red")
        ax2.plot(df[x_axis], df[y2_axis], color="red", label=y2_axis)

    st.pyplot(fig)

    # Distribution Analysis for `current_in`
    st.subheader("📈 Distribution of `current_in`")
    if "current_in" in df.columns:
        # Define bins with 10-unit intervals up to 130, then 130+
        bins = list(range(0, 140, 10)) + [float("inf")]
        labels = [f"{i}-{i+10}" for i in range(0, 130, 10)] + ["130+"]

        # Assign bin labels
        df["current_in_class"] = pd.cut(df["current_in"], bins=bins, labels=labels, right=False)

        # Distribution percentage
        distribution = df["current_in_class"].value_counts(normalize=True).sort_index() * 100

        fig2, ax2 = plt.subplots()
        ax2.bar(distribution.index.astype(str), distribution.values, color="skyblue")
        ax2.set_ylabel("Percentage (%)")
        ax2.set_xlabel("Current_in Range (A)")
        ax2.set_title("Current_in Distribution by Class (10A Intervals)")
        plt.xticks(rotation=45)
        st.pyplot(fig2)

        # Runtime Summary Table
        st.subheader("⏱️ Runtime Summary by Current Range")
        sample_interval_sec = 1 / 22  # each row = 1/22 sec
        runtime_stats = df["current_in_class"].value_counts().sort_index().reset_index()
        runtime_stats.columns = ["Current Range (A)", "Row Count"]
        runtime_stats["Total Time (sec)"] = runtime_stats["Row Count"] * sample_interval_sec
        st.table(runtime_stats)
    else:
        st.warning("`current_in` column not found.")
