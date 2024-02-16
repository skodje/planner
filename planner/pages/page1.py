import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from planner.mortgage import Mortgage
from planner.pages.common import Page


class Page1(Page):
    def __init__(self, state):
        self.state = state

    def write(self):
        st.title("Mortgage Calculator")  # TODO make class name?

        # slider_value = st.slider(
        #    "Set Value from here See it on Page 2",
        #    value=self.state.client_config["slider_value"],
        # )
        # self.state.client_config["slider_value"] = slider_value

        # Input fields
        # interest_rate = st.number_input("Interest Rate (%)", value=4.0, step=0.1)
        # principal = st.number_input("Initial Loan Amount", value=300000)
        # years = st.number_input("Years", value=30, step=1)
        # extra_payment = st.number_input("Additional Monthly Payment", value=0)

        mortgage = Mortgage(
            principal=st.number_input("Initial Loan Amount", value=300000, step=10000),
            interest_rate=st.number_input("Interest Rate (%)", value=5.0, step=0.01),
            years=st.number_input("Years", value=25, step=1),
        )
        calculate = st.button("Calculate")

        if calculate:
            payment_schedule = mortgage.payment_schedule()

            st.subheader("Payment Schedule")
            df = pd.DataFrame(payment_schedule).round(2)
            st.write(df)

            total_interest_paid = df["Interest"].sum()
            st.write(
                "Total Interest Paid: "
                f"{total_interest_paid:,.2f} {mortgage.currency.name}",
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
