import streamlit as st

from planner.lib import mortgage


st.set_page_config(
    page_title="Create people",
)


with st.form("my_form"):
    st.write("New Person")
    st.text_input(label="Name", placeholder="Jabba Bibaba")
    col1, col2 = st.columns(2)
    col1.text_input(label="Salaray", placeholder="100")
    col2.selectbox(label="Currency", options=[c.name for c in mortgage.Currency])

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        print("Submitted")
