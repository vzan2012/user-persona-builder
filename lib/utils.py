import streamlit as st


def load_css():
    try:
        with open("./css/styles.css", "r") as f:
            st.markdown(
                f"<style type='text/css'>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Styles CSS File Not Found in the Project Folder !!!")


def persona_preview(persona_form_data):
    pass
