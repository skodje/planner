import inspect
from contextlib import ExitStack
from functools import partial

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from planner.lib.loan import Loan, TermsType
from planner.lib.person import Person
from planner.lib.utils import change_widget_font_size

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


def dataclass_to_markdown(cls) -> str:
    """
    Convert a dataclass to Markdown format.

    Args:
        cls (Any): The dataclass to be converted.

    Returns:
        str: Markdown representation of the dataclass.
    """
    # Header
    markdown = f"## {cls.__name__}\n\n"

    # Attributes
    markdown += "| Attribute | Type | Description |\n"
    markdown += "| --- | --- | --- |\n"
    for field in fields(cls):
        markdown += f"| {field.name} | {field.type.__name__} |  |\n"

    # Methods
    markdown += "\n### Methods:\n\n"
    for name, method in inspect.getmembers(cls, inspect.isfunction):
        if not name.startswith("__"):
            params = inspect.signature(method).parameters
            param_str = ", ".join(
                [
                    f"{param}: {param_info.annotation.__name__}"
                    for param, param_info in params.items()
                ]
            )
            return_type = inspect.signature(method).return_annotation.__name__
            markdown += f"- `{name}({param_str}) -> {return_type}`: \n\n"

    return markdown


### FOR TESTING ###
st.session_state.people["Ida"] = Person(
    name="Ida",
    salary=1_050_000,
    assets=100,
)
st.session_state.people["Lars"] = Person(
    name="Lars",
    salary=954_000,
    assets=100,
)
st.session_state.people["August"] = Person(
    name="August",
    salary=100,
    assets=100,
)
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
# for et, spec in LABELS.items():
#    change_widget_font_size(et, spec["size"])


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
                ]
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
if people := st.session_state.get("people"):
    # st.markdown("# Foo bar")
    st.write(dataclass_to_markdown(people["Ida"]))
    # st.write(people)
if loans := st.session_state.get("loans"):
    # st.markdown("# Foo bar")
    st.write(loans)

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
        "Total Interest Paid: " f"{total_interest_paid:,.2f} \u00A4",
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
