from typing import Dict, Type

from planner.pages.common import Page

PAGE_MAP: Dict[str, Type[Page]] = {name: page for name, page in Page.pages.items()}

__all__ = ["PAGE_MAP"]
