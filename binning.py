from typing import NamedTuple
from .analysis_tools import calculate_bins

class Binning(NamedTuple):
    bin_width: float
    bin_low: float
    bin_high: float

    def get_num_bins(self) -> int:
        return calculate_bins(self.bin_low, self.bin_high, self.bin_width) if self.bin_width > 0 else 0
    
    def __str__(self) -> str:
        return f"({self.get_num_bins()},{self.bin_low:.5f},{self.bin_high:.5f})"
