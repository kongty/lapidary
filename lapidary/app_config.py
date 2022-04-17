from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    pe: int
    mem: int
    input: int
    output: int
    runtime: int
