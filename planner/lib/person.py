import dataclasses

from planner.lib.loan import Currency


@dataclasses.dataclass
class Person:
    name: str
    salary: float | int = 0.0
    assets: float | int = 0.0
    currency: Currency = Currency.NOK
