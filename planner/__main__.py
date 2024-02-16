import streamlit as st

from planner import mortgage
from planner.pages import PAGE_MAP
from planner.state import provide_state
from planner.utils import add_custom_css

add_custom_css()


def create_person() -> None:
    with st.sidebar.form("my_form"):
        st.write("New Person")
        st.text_input(label="Name", placeholder="Jabba Bibaba")
        col1, col2 = st.columns(2)
        col1.text_input(label="Salaray", placeholder="100")
        col2.selectbox(label="Currency", options=[c.name for c in mortgage.Currency])

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            return


@provide_state()
def main(state=None) -> None:
    current_page = st.sidebar.radio("Go To", list(PAGE_MAP))
    with st.sidebar.container(border=True):
        st.button(
            label="Create person",
            help="Add a new person",
            on_click=create_person,
        )
    PAGE_MAP[current_page](state=state).write()


if __name__ == "__main__":
    main()
