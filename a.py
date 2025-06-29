import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from grading_logic import load_grading_rules, absolute_grade_from_file, relative_grades
from utils import collect_subject_data
import json
from PIL import Image
import base64
import plotly.express as px

# --- UTILS ---
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

def img_to_bytes(img_path):
    try:
        with open(img_path, "rb") as img_file:
            img_bytes = img_file.read()
        return base64.b64encode(img_bytes).decode()
    except FileNotFoundError:
        st.error(f"Error: Image file not found: {img_path}")
        return ""
    except Exception as e:
        st.error(f"Error encoding image: {e}")
        return ""

# --- BACKGROUND IMAGE FOR HOME PAGE ---
try:
    background_image_path = "__pycache__/maxresdefault.jpg"
    background_image = Image.open(background_image_path)
except FileNotFoundError:
    st.error("Error: Background image not found.")
    background_image = None
except Exception as e:
    st.error(f"Error loading background image: {e}")
    background_image = None

# --- GENERAL SETTINGS ---
PAGE_TITLE = "Grading Dashboard"
PAGE_ICON = "🎓"
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuration")
    menu = st.selectbox("📂 Navigation", [
        "🏠 Home",
        "🔧 Class Setup",
        "📘 Subject-wise Results",
        "📊 Overall Class Performance",
        "📈 Visualizations"
    ])
    grading_type = st.selectbox("Grading System", ["Absolute", "Relative"])

    # Session state init
    if "data_dict" not in st.session_state:
        st.session_state.data_dict = {}
        st.session_state.all_results = {}
        st.session_state.rules = load_grading_rules() if grading_type == "Absolute" else None

    if "subject_names" not in st.session_state:
        st.session_state.subject_names = []

# --- DARK GRADIENT THEME FOR OTHER PAGES ---
if menu != "🏠 Home":
    gradient_css = """
    <style>
    .stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #42275a, #734b6d, #3a1c71, #d76d77, #ffafbd);
    background-size: 400% 400%;
    animation: gradientMove 15s ease infinite !important;
    }

    @keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
    }

    /* Set default text to white */
    html, body, [class*="css"] {
    color: white;
    }

    /* Make widgets readable on dark background */
    .stMarkdown, .stDataFrame, .stPlotlyChart, .stTextInput, .stSelectbox, .stNumberInput {
    background-color: rgba(0, 0, 0, 0.5) !important;
    color: white !important;
    border-radius: 10px;
    padding: 1em;
    font-weight: 500;
    border: 1px solid rgba(255, 255, 255, 0.2);
    }
    </style>
    """

    st.markdown(gradient_css, unsafe_allow_html=True)

# --- MAIN CONTENT ROUTES ---
if menu == "🏠 Home":
    if background_image:
        st.markdown(
            f"""
            <style>
                .stApp {{
                    background-image: url("data:image/jpeg;base64,{img_to_bytes(background_image_path)}");
                    background-size: cover;
                    background-position: center;
                }}
                .home-text {{
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    text-align: right;
                    color: black;
                }}
            </style>
            """,
            unsafe_allow_html=True
        )

    with st.container():
        st.markdown(
            f"""
            <div class='home-text'>
                <h1 style='color: black; font-weight: bold;'>🎓 Student Grading System Dashboard</h1>
                <h2 style='color: black; font-weight: bold;'>Interactive tool for teachers to manage and visualize student grades.</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

elif menu == "🔧 Class Setup":
    with st.container():
        st.markdown("### ✍️ Class Data Entry")
        st.session_state.data_dict = collect_subject_data()

        # Remove the duplicate "Subject Information" section
        # st.markdown("#### Subject Information")
        # num_subjects = st.number_input("How many subjects do you want?", min_value=1, max_value=10, value=1)

        # subject_names = []
        # for i in range(num_subjects):
        #     subject_name = st.text_input(f"Enter name of Subject {i+1}", key=f"subject_{i}") # Added key
        #     subject_names.append(subject_name)

        # st.session_state.subject_names = subject_names

elif menu == "📘 Subject-wise Results":
    with st.container():
        st.markdown("### 📘 Subject Results View")
        data_dict = st.session_state.data_dict
        rules = st.session_state.rules

        if not data_dict:
            st.warning("⚠️ Please enter data in 'Class Setup' first.")
        else:
            subject_list = list(data_dict.keys())
            subject = st.selectbox("Choose Subject", subject_list)
            df = data_dict[subject].copy()

            if grading_type == "Absolute":
                df['Grade'] = df['Marks'].apply(lambda x: absolute_grade_from_file(int(x), rules))
            else:
                df['Grade'] = relative_grades(df['Marks'].tolist())

            grade_icons = {
                "A+": "⭐",
                "A": "🥇",
                "B": "🥈",
                "C": "🥉",
                "D": "🙁",
                "F": "😞",
            }

            def add_grade_icon(grade):
                return f"{grade} {grade_icons.get(grade, '')}"

            df['Grade'] = df['Grade'].apply(add_grade_icon)

            st.dataframe(df)
            st.session_state.all_results[subject] = df[['Name', 'Marks', 'Grade']].rename(columns={
                "Marks": f"{subject}_Marks",
                "Grade": f"{subject}_Grade"
            })

elif menu == "📊 Overall Class Performance":
    with st.container():
        st.markdown("### 🧾 Overall Class Summary")
        all_results = st.session_state.all_results
        if not all_results:
            st.warning("⚠️ Grade the subjects first in 'Subject-wise Results'.")
        else:
            merged_df = None
            for subject_df in all_results.values():
                if merged_df is None:
                    merged_df = subject_df
                else:
                    merged_df = pd.merge(merged_df, subject_df, on="Name", how="outer")

            merged_df = merged_df.fillna("-")

            def color_grades(val):
                color = 'green' if "A" in val or "B" in val else 'red' if "F" in val or "D" in val else ''
                return f'background-color: {color}'

            grades_cols = [col for col in merged_df.columns if "_Grade" in col]
            styled_df = merged_df.style.applymap(color_grades, subset=grades_cols)

            st.dataframe(styled_df)

            st.markdown("#### 🔥 Heatmap of Marks")
            marks_cols = [col for col in merged_df.columns if "_Marks" in col]
            heat_df = merged_df[["Name"] + marks_cols].set_index("Name").replace("-", 0)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                fig, ax = plt.subplots(figsize=(7, 3))
                sns.heatmap(heat_df.astype(float), annot=True, cmap="YlGnBu", linewidths=.5, ax=ax, cbar=False)
                st.pyplot(fig)

elif menu == "📈 Visualizations":
    with st.container():
        st.markdown("### 📈 Visualizations")
        data_dict = st.session_state.data_dict
        all_results = st.session_state.all_results

        if not all_results:
            st.warning("⚠️ First grade a subject in 'Subject-wise Results'.")
        else:
            subject = st.selectbox("Choose Subject for Visualization", list(all_results.keys()))
            df = all_results[subject].copy()

            marks_col = [col for col in df.columns if col.endswith("_Marks")][0]
            grade_col = [col for col in df.columns if col.endswith("_Grade")][0]

            df = df.rename(columns={marks_col: "Marks", grade_col: "Grade"})

            graph_type = st.selectbox("Select Graph Type", ["Bar Chart", "Pie Chart", "Line Curve", "Interactive Bar Chart"])

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if graph_type == "Bar Chart":
                    fig, ax = plt.subplots(figsize=(5, 3))
                    df['Grade'].value_counts().sort_index().plot(kind='bar', ax=ax, color='skyblue')
                    ax.set_title(f"{subject} Grade Distribution", fontsize=12)
                    ax.set_xlabel("Grades")
                    ax.set_ylabel("Number of Students")
                    st.pyplot(fig)

                elif graph_type == "Pie Chart":
                    fig2, ax2 = plt.subplots(figsize=(5, 3))
                    grade_counts = df['Grade'].value_counts().sort_index()
                    ax2.pie(grade_counts, labels=grade_counts.index, autopct='%1.1f%%', startangle=140,
                            colors=plt.cm.Paired.colors, textprops={'fontsize': 10})
                    ax2.axis('equal')
                    st.pyplot(fig2)

                elif graph_type == "Line Curve":
                    fig3, ax3 = plt.subplots(figsize=(5, 3))
                    df.sort_values('Marks').reset_index(drop=True)['Marks'].plot(kind='line', marker='o', ax=ax3, color='teal')
                    ax3.set_title(f"{subject} Grade Curve", fontsize=12)
                    ax3.set_xlabel("Student Index")
                    ax3.set_ylabel("Marks")
                    st.pyplot(fig3)

                elif graph_type == "Interactive Bar Chart":
                    fig4 = px.bar(df['Grade'].value_counts().sort_index(),
                                 x=df['Grade'].value_counts().sort_index().index,
                                 y=df['Grade'].value_counts().sort_index().values,
                                 labels={'x': 'Grade', 'y': 'Number of Students'},
                                 title=f"{subject} Grade Distribution (Interactive)",
                                 color=df['Grade'].value_counts().sort_index().index,
                                 color_discrete_sequence=px.colors.qualitative.Prism)
                    st.plotly_chart(fig4)