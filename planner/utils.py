import streamlit as st


def add_custom_css() -> None:
    st.markdown(
        """
        <style>
        </style>
        """,
        unsafe_allow_html=True,
    )
