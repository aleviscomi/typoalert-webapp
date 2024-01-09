from enum import Enum

class Result(Enum):
    Unknown = 0             # grey
    NotTypo = 1             # green
    ProbablyNotTypo = 2     # greenYellow
    ProbablyTypo = 3        # yellow
    Typo = 4                # red
    TypoPhishing = 5        # darkRed
    Malware = 6             # darkRed

    def __str__(self):
        return self.name