class PartialRegion:
    def __init__(self, height: int, width: int, num_input: int, num_output: int) -> None:
        self.is_used = False
        self.height = height
        self.width = width
        self.num_input = num_input
        self.num_output = num_output
