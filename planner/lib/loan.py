from __future__ import annotations

import dataclasses
from enum import Enum, auto


class Currency(Enum):
    USD = auto()
    EUR = auto()
    GBP = auto()
    JPY = auto()
    CAD = auto()
    NOK = auto()


class TermsType(Enum):
    years = auto()
    months = auto()


@dataclasses.dataclass
class Loan:
    name: str = ""
    principal: float = 0.0  # original amount borrowed.
    interest_rate: float = 0.0  # Tunable
    terms: int = 25  # Tunable
    terms_type: str = TermsType.years  # Tunable
    extra_payment: int | float = 0.0  # Tunable
    currency: Currency = Currency.NOK

    def payment_schedule(self):
        balance = self.principal
        monthly_payment = self.monthly_payment
        for month in range(1, self.total_months + 1):
            interest_payment = balance * self.monthly_interest_rate
            principal_payment = monthly_payment - interest_payment
            balance = round(balance - principal_payment, 2)
            yield {
                "Month": month,
                "Principal": round(principal_payment, 2),
                "Interest": round(interest_payment, 2),
                "Remaining Balance": balance,
            }

    def monthly_payment_alloc(self) -> tuple[float, float]:
        """Calculate ."""
        interest_payment = self.principal * self.monthly_interest_rate
        principal_payment = self.monthly_payment - interest_payment
        return round(interest_payment, 2), round(principal_payment, 2)

    @property
    def monthly_interest_rate(self) -> float:
        return self.interest_rate / 12 / 100

    @property
    def total_months(self) -> int:
        match self.terms_type:
            case TermsType.years.name:
                return self.terms * 12
            case TermsType.months.name:
                return self.terms
            case _:
                raise RuntimeError(f"Unexpected {self.terms_type}")

    @property
    def monthly_payment(self) -> float:
        # TODO consider caching?
        # Calculate the monthly payment using the formula for a fixed-rate loan
        print(f"{self.total_months=}")
        print(f"{self.monthly_interest_rate=}")
        return (
            self.principal
            * (
                self.monthly_interest_rate
                * (1 + self.monthly_interest_rate) ** self.total_months
            )
            / ((1 + self.monthly_interest_rate) ** self.total_months - 1)
        )
