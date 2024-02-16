import dataclasses
from enum import Enum, auto


class Currency(Enum):
    USD = auto()
    EUR = auto()
    GBP = auto()
    JPY = auto()
    CAD = auto()
    NOK = auto()


@dataclasses.dataclass
class Mortgage:
    principal: int | float  # original amount borrowed.
    interest_rate: int | float
    years: int = 25
    extra_payment: int | float = 0.0
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
        return self.years * 12

    @property
    def monthly_payment(self) -> float:
        # TODO consider caching?
        # Calculate the monthly payment using the formula for a fixed-rate mortgage
        return (
            self.principal
            * (
                self.monthly_interest_rate
                * (1 + self.monthly_interest_rate) ** self.total_months
            )
            / ((1 + self.monthly_interest_rate) ** self.total_months - 1)
        )


# foo = Mortgage(5_600_000, 5.19)
# interest, downpayment = foo.monthly_payment_alloc()
# print(f"{interest=}")
# print(f"{downpayment=}")
#
# for payment in foo.payment_schedule():
#    print(payment)
