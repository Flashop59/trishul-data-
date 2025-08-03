import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Data Visualizer for EV Telemetry (CSV / Excel)")

# ---- File Upload ----
uploaded_file = st.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Detect file type
    file_name = uploaded_file.name.lower()

    # --- CSV Handling ---
    if file_name.endswith(".csv"):
        delimiter = st.selectbox("Select CSV Delimiter", [",", ";", "\t"], index=1)
        df = pd.read_csv(uploaded_file, delimiter=delimiter)

    # --- Excel Handling ---
    elif file_name.endswith(".xlsx"):
        try:
            xls = pd.ExcelFile(uploaded_file)
            sheet_name = st.selectbox("Select Sheet", xls.sheet_names)
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        except ImportError:
            st.error("Excel support requires `openpyxl`. Please install it using:\n\n`pip install openpyxl`")
            st.stop()

    # ---- Display Data ----
    st.subheader("📋 Filterable Data Table")
    st.dataframe(df)

    # ---- Column Selection ----
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    all_cols = df.columns.tolist()

    # ---- Custom Graph Section ----
    st.subheader("📊 Custom Graphs")
    col1, col2, col3 = st.columns(3)

    with col1:
        x_axis = st.selectbox("Select X-axis (Any Column)", all_cols)
    with col2:
        y1_axis = st.selectbox("Select Primary Y-axis (Numeric)", numeric_cols)
    with col3:
        y2_axis = st.selectbox("Select Secondary Y-axis (optional)", ["None"] + numeric_cols)

    # Plot line graph
    fig, ax1 = plt.subplots()
    ax1.set_xlabel(x_axis)
    ax1.set_ylabel(y1_axis, color="blue")
    ax1.plot(df[x_axis], df[y1_axis], color="blue", label=y1_axis)

    if y2_axis != "None":
        ax2 = ax1.twinx()
        ax2.set_ylabel(y2_axis, color="red")
        ax2.plot(df[x_axis], df[y2_axis], color="red", label=y2_axis)

    st.pyplot(fig)

    # ---- Customizable Distribution Section ----
    st.subheader("📈 Distribution Analysis")
    if numeric_cols:
        dist_col = st.selectbox("Select Column for Distribution (Numeric)", numeric_cols, index=0)

        # Binning (10-unit intervals + last bin)
        bins = list(range(0, 140, 10)) + [float("inf")]
        labels = [f"{i}-{i+10}" for i in range(0, 130, 10)] + ["130+"]

        # Assign bin labels
        df[f"{dist_col}_class"] = pd.cut(df[dist_col], bins=bins, labels=labels, right=False)

        # Percentage distribution
        distribution = df[f"{dist_col}_class"].value_counts(normalize=True).sort_index() * 100

        # Plot distribution
        fig2, ax2 = plt.subplots()
        ax2.bar(distribution.index.astype(str), distribution.values, color="skyblue")
        ax2.set_ylabel("Percentage (%)")
        ax2.set_xlabel(f"{dist_col} Range")
        ax2.set_title(f"{dist_col} Distribution by Class (10-unit Intervals)")
        plt.xticks(rotation=45)
        st.pyplot(fig2)

        # Runtime summary
        st.subheader("⏱️ Runtime Summary by Range")
        sample_interval_sec = 1 / 22  # each row = 1/22 sec
        runtime_stats = df[f"{dist_col}_class"].value_counts().sort_index().reset_index()
        runtime_stats.columns = [f"{dist_col} Range", "Row Count"]
        runtime_stats["Total Time (sec)"] = runtime_stats["Row Count"] * sample_interval_sec
        st.table(runtime_stats)
    else:
        st.warning("No numeric columns found for distribution analysis.")
