# utils.py
import pandas as pd
import streamlit as st

def read_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    return df

def manual_entry_tabular(subject):
    st.markdown(f"### ✍️ Manual Entry for **{subject}**")
    if f"manual_df_{subject}" not in st.session_state:
        st.session_state[f"manual_df_{subject}"] = pd.DataFrame({"Name": [""], "Marks": [0]})

    df = st.session_state[f"manual_df_{subject}"]

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(f"➕ Add Row ({subject})"):
            df.loc[len(df)] = ["", 0]
    with col2:
        if st.button(f"➖ Remove Last Row ({subject})") and len(df) > 1:
            df.drop(df.tail(1).index, inplace=True)

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        key=f"editor_{subject}",
        column_config={
            "Name": st.column_config.TextColumn("Student Name"),
            "Marks": st.column_config.NumberColumn("Marks", min_value=0, max_value=100, step=1)
        }
    )

    st.session_state[f"manual_df_{subject}"] = edited_df
    return edited_df[edited_df["Name"] != ""]

def collect_subject_data():
    subject_count = st.number_input("How many subjects do you want to enter?", min_value=1, step=1)
    data_dict = {}

    for i in range(int(subject_count)):
        subject = st.text_input(f"Enter name of Subject {i+1}", key=f"subject_name_{i}")
        if subject.strip() == "":
            continue

        st.subheader(f"📘 Subject: {subject}")
        input_mode = st.radio(f"How do you want to enter data for {subject}?", ["Upload CSV", "Manual Entry"], key=f"input_mode_{subject}")

        if input_mode == "Upload CSV":
            uploaded_file = st.file_uploader(f"Upload CSV file for {subject}", type=["csv"], key=f"csv_upload_{subject}")
            if uploaded_file:
                df = read_csv(uploaded_file)
                data_dict[subject] = df

        elif input_mode == "Manual Entry":
            df = manual_entry_tabular(subject)
            data_dict[subject] = df

    return data_dict
