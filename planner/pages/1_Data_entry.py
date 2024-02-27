from contextlib import ExitStack
from functools import partial

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from planner.lib.loan import Currency, Loan, TermsType
from planner.lib.person import Person

st.set_page_config(
    page_title="loan Calculator",
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


def change_widget_font_size(label, font_size="12px"):
    js_code = f"""
        <script>
        var elements = window.parent.document.querySelectorAll('*');
        for (var i = 0; i < elements.length; ++i) {{
            if (String(elements[i].innerText).startsWith('{label}')) {{
                elements[i].style.fontSize = '{font_size}';
            }}
        }}
        </script>
    """
    components.html(f"{js_code}", height=0, width=0)


# Load some custom javascript
LABELS = {
    "+loan": {
        "full": "__+loan__ :money_with_wings:",
        "size": "20px",
    },
    "+people": {
        "full": "__+people__ :person_frowning:",
        "size": "20px",
    },
}
for et, spec in LABELS.items():
    change_widget_font_size(et, spec["size"])


# -------------------#
# On click handlers #
# -------------------#
def handler_new_loan():
    with ExitStack() as stack:
        stack.enter_context(st.expander(label=LABELS["+loan"]["full"]))
        stack.enter_context(st.form("new_loan_form", border=False))

        name = st.text_input(label="Name", placeholder="Mortgage")
        interest_rate = st.number_input("Interest Rate (%)", value=5.0, step=0.01)
        col1, col2 = st.columns(2)

        principal = col1.number_input("Initial Loan Amount", value=300000, step=10000)
        currency = col2.selectbox("Currency", options=[c.name for c in Currency])

        terms = col1.number_input("Loan term", value=25, step=1)
        terms_type = col2.selectbox(
            label="Term Type",
            label_visibility="hidden",
            options=[tt.name for tt in TermsType],
        )

        col1.multiselect(
            label="Stakeholders",
            options=st.session_state.get("people", {}).keys(),
            help="Add stakeholders to loan. Requires people.",
        )

        loan = Loan(
            name=name,
            principal=principal,
            currency=currency,
            interest_rate=interest_rate,
            terms=terms,
            terms_type=terms_type,
        )
        if primary_submit("Create"):
            st.session_state.loans[name] = loan


def handler_new_person():
    with ExitStack() as stack:
        stack.enter_context(st.expander(LABELS["+people"]["full"]))
        stack.enter_context(st.form("my_form", border=False))
        name = st.text_input("Name", placeholder="Jabba Bibaba")
        col1, col2 = st.columns(2)
        salary = col1.text_input("Salary (yearly)", placeholder="100")
        currency = col2.selectbox("Currency", options=[c.name for c in Currency])
        assets = col1.text_input("Assets", help="Disposable assets.")

        person = Person(name=name, salary=salary, currency=currency, assets=assets)

        if primary_submit("Create"):
            st.session_state.people[name] = person


# ------------------------------#
# Main page data input widgets #
# ------------------------------#
handler_new_person()
handler_new_loan()
# TODO handle expense?

st.divider()

# ---------------#
# Data display  #
# ---------------#
if people := st.session_state.get("people"):
    # st.markdown("# Foo bar")
    st.write(people)
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

if calculate and st.session_state["loans"]:
    loan = next(iter(st.session_state.loans.values()))
    payment_schedule = loan.payment_schedule()

    st.subheader("Payment Schedule")
    df = pd.DataFrame(payment_schedule).round(2)
    st.write(df)

    total_interest_paid = df["Interest"].sum()
    st.write(
        "Total Interest Paid: " f"{total_interest_paid:,.2f} {loan.currency}",
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
