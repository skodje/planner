from abc import ABC, abstractmethod


class Page(ABC):
    pages = {}

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        cls.pages[cls.__name__] = cls

    @abstractmethod
    def write(self):
        """Write the UI using streamlit."""
