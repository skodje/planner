import streamlit as st

from planner.pages.common import Page


class Page2(Page):
    def __init__(self, state) -> None:
        self.state = state

    def write(self) -> None:
        st.title("Page 2")

        st.write(self.state.client_config["slider_value"])
