import streamlit as st

from planner.utils import add_custom_css

st.set_page_config(
    page_title="Home",
)

add_custom_css()

st.title("Home")
