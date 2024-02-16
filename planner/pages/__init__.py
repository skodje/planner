from typing import Type

from planner.pages.common import Page
from planner.pages.page1 import Page1
from planner.pages.page2 import Page2

PAGE_MAP: dict[str, Type[Page]] = dict(Page.pages.items())

__all__ = ["PAGE_MAP"]
