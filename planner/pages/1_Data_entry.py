import inspect
from contextlib import ExitStack
from functools import partial

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from planner.lib.loan import Loan, TermsType
from planner.lib.person import Person

st.set_page_config(
    page_title="Data entry",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Planner")

st.session_state.setdefault("people", {})
st.session_state.setdefault("loans", {})

primary_submit = partial(
    st.form_submit_button,
    use_container_width=True,
    type="primary",
)


### FOR TESTING ###
# st.session_state.people["Rizzy"] = Person(
#    name="Rizzy",
#    salary=800_000,
#    assets=300_000,
# )
# st.session_state.people["Izy"] = Person(
#    name="Izy",
#    salary=900_000,
#    assets=500_000,
# )
# st.session_state.people["Lizzy"] = Person(
#    name="Lizzy",
#    salary=10_000,
#    assets=100,
# )
### END FOR TESTING ###


# Load some custom javascript
LABELS = {
    "+loan": {
        "full": "__+loan__ :bank:",
        "size": "20px",
    },
    "+people": {
        "full": "__+people__ :person_frowning:",
        "size": "20px",
    },
    "+expense": {
        "full": "__+expense__ :money_with_wings:",
        "size": "20px",
    },
}


def update_sidebar(session_state_key: str) -> None:
    """Function to display session state items in the sidebar, with the ability to delete items.

    Args:
        session_state_key (str): Key in st.session_state to manage (e.g., 'people').

    """
    if not (items := st.session_state.get(session_state_key)):
        return

    st.sidebar.markdown(f"## {session_state_key.capitalize()}")

    for name in list(items):
        info = items[name]
        st.sidebar.write(str(info))

        if st.sidebar.button("Delete", key=f"{session_state_key}_{name}_delete"):
            del items[name]
            st.session_state[session_state_key] = items
            break

    st.sidebar.divider()


# -------------------#
# On click handlers #
# -------------------#
def handler_new_loan():
    with st.expander(label=LABELS["+loan"]["full"]):
        name = st.text_input(label="Name", placeholder="Mortgage")
        principal = st.number_input("Initial Loan Amount", value=300000, step=10000)
        interest_rate = st.number_input("Interest Rate (%)", value=5.0, step=0.01)

        col1, col2 = st.columns(2)
        terms = col1.number_input("Loan term", value=25, step=1)
        terms_type = col2.selectbox(
            label="Term Type",
            label_visibility="hidden",
            options=[tt.name for tt in TermsType],
        )

        percentages = stakeholder_context(col1, col2)

        if st.button("Add loan"):
            if percentages and round(sum(percentages.values())) != 100:
                st.error("Percentages must add up to 100")
            else:
                st.session_state.loans[name] = Loan(
                    name=name,
                    principal=principal,
                    interest_rate=interest_rate,
                    terms=terms,
                    terms_type=terms_type,
                )


def handler_new_person():
    with ExitStack() as stack:
        stack.enter_context(st.expander(LABELS["+people"]["full"]))
        stack.enter_context(st.form("my_form", border=False))
        name = st.text_input("Name", placeholder="Jabba Bibaba")
        col1, col2 = st.columns(2)
        salary = col1.text_input("Salary (yearly)", placeholder="100")
        assets = col1.text_input("Assets", help="Disposable assets.")

        person = Person(
            name=name,
            salary=salary,
            assets=assets,
        )

        if primary_submit("Create"):
            st.session_state.people[name] = person


def calculate_percentage_distribution(numbers):
    total_sum = sum(numbers)
    percentage_distribution = [(num / total_sum) * 100 for num in numbers]
    return percentage_distribution


def stakeholder_context(col1, col2):
    # Need to ensure unique keys
    basekey = inspect.currentframe().f_back.f_code.co_name

    stakeholders = col1.multiselect(
        label="Stakeholders",
        options=st.session_state.people,
        key=f"{basekey}_select",
        help="Add stakeholders to loan. Requires people.",
    )

    distribute = (
        st.checkbox(
            "Distribute by salary",
            key=f"{basekey}_distribute",
        )
        if len(stakeholders) > 1
        else False
    )

    percentages = {}
    if stakeholders:
        cols = st.columns(len(stakeholders))

        if distribute:
            distribution = calculate_percentage_distribution(
                [
                    st.session_state.people[stakeholder].salary
                    for stakeholder in stakeholders
                ],
            )
        else:
            distribution = [100 / len(stakeholders)] * len(stakeholders)

        for user, col, share in zip(stakeholders, cols, distribution):
            remaining_percentage = 100.0

            percentage = col.number_input(
                f"{user} (%):",
                min_value=0.0,
                max_value=remaining_percentage,
                value=share,
                key=f"{basekey}_{user}_percentage",
            )
            percentages[user] = percentage
            remaining_percentage -= percentage
        return percentages


def handler_expense():
    with st.expander(LABELS["+expense"]["full"]):
        name = st.text_input("Name", placeholder="Netflix")
        col1, col2 = st.columns(2)

        amount = col1.number_input("Amount")
        terms_type = col2.selectbox(
            label="Frequency",
            options=["monthly", "yearly", "quarterly", "daily"],
        )

        stakeholder_context(col1, col2)

        submit = st.button("Create expense")
        if submit:
            print("here")


# ------------------------------#
# Main page data input widgets #
# ------------------------------#
handler_new_person()
handler_new_loan()
handler_expense()

st.divider()

# ---------------#
# Data display  #
# ---------------#
update_sidebar("people")
update_sidebar("loans")

st.divider()

# ------------#
# Calculator #
# ------------#

calculate = st.button(
    label="Calculate",
    type="primary",
)

if calculate and st.session_state.loans:
    loan = next(iter(st.session_state.loans.values()))
    payment_schedule = loan.payment_schedule()

    st.subheader("Payment Schedule")
    df = pd.DataFrame(payment_schedule).round(2)
    st.write(df)

    total_interest_paid = df["Interest"].sum()
    st.write(
        "Total Interest Paid: " f"{total_interest_paid:,.2f} \u00a4",
    )

    st.subheader("Visualization")
    fig, ax = plt.subplots()
    ax.plot(df["Month"], df["Remaining Balance"])
    ax.set(
        xlabel="Month",
        ylabel="Remaining Balance",
        title="Mortgage Remaining Balance Over Time",
    )
    st.pyplot(fig)
