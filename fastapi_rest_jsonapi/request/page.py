from typing import Optional


class Page:
    def __init__(self, number: int, size: Optional[int] = None) -> None:
        self.number = number
        self.size = size
