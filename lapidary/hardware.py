from typing import Optional
from lapidary.architecture import Architecture


class Hardware:
    def __init__(self, architecture: Optional[Architecture] = None) -> None:
        self.architecture = Architecture()
        if architecture is not None:
            self.architecture = architecture
