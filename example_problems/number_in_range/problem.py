import dataclasses

import algobowl.lib.problem as problemlib


@dataclasses.dataclass
class Input(problemlib.BaseInput):
    low: int
    high: int

    @classmethod
    def read(cls, f):
        lines = f.readlines()
        problemlib.assert_linecount(lines, 2)
        low = problemlib.parse_line_int(lines, 0, bounds=range(1, 101))
        high = problemlib.parse_line_int(lines, 1, bounds=range(1, 101))
        if low > high:
            raise problemlib.FileFormatError("low must be less than or equal to high")
        return cls(low=low, high=high)

    def write(self, f):
        print(self.low, file=f)
        print(self.high, file=f)

    @classmethod
    def generate(cls, rng):
        low = rng.randint(1, 100)
        high = rng.randint(low, 100)
        return cls(low=low, high=high)

    def trivial_solve(self):
        return Output(input=self, score=self.high)


@dataclasses.dataclass
class Output(problemlib.BaseOutput):
    @classmethod
    def read(cls, input, f):
        lines = f.readlines()
        problemlib.assert_linecount(lines, 1)
        score = problemlib.parse_line_int(lines, 0, bounds=range(1, 101))
        return cls(input=input, score=score)

    def compute_actual_score(self):
        if self.score > self.input.high:
            raise problemlib.VerificationError("Score is too high")
        if self.score < self.input.low:
            raise problemlib.VerificationError("Score is too low")
        return self.score

    def write(self, f):
        print(self.repr_score(self.score), file=f)
