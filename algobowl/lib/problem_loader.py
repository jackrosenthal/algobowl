"""Problem loading infrastructure for the AlgoBOWL website."""

import pathlib
import sys
import types

import algobowl.lib.problem as problemlib

_module_cache = {}
_statement_cache = {}


def _cache_getent(cache, path, loader=lambda pth: pth.read_bytes()):
    path = path.resolve()
    mtime = path.stat().st_mtime
    if path in cache:
        c_mtime, c_val = cache[path]
        if c_mtime == mtime:
            return c_val
    val = loader(path)
    cache[path] = (mtime, val)
    return val


class Problem:
    """High-level wrapper around the problem format."""

    def __init__(self, path):
        self.path = path

    def get_module(self):
        def loader(path):
            contents = path.read_text()
            module = types.ModuleType("problem")
            sys.modules["problem"] = module
            code = compile(contents, str(path), "exec")
            exec(code, module.__dict__)
            return module

        return _cache_getent(_module_cache, self.path / "problem.py", loader=loader)

    def get_statement_pdf(self):
        return _cache_getent(_statement_cache, self.path / "statement.pdf")

    def generate_input(self, rng):
        module = self.get_module()
        return module.Input.generate(rng)

    def parse_input(self, input_file):
        module = self.get_module()
        return module.Input.read(input_file)

    def parse_output(self, input, output_file):
        module = self.get_module()
        if not isinstance(input, module.Input):
            input = module.Input.read(input)
        return module.Output.read(input, output_file)

    def verify_output(self, input, output_file):
        output = self.parse_output(input, output_file)
        output.verify()

    def run_tests(self, pytest_extra_args=()):
        """Run tests on this problem."""
        from algobowl.lib import problem_tester  # noqa: PLC0415

        retcode = problem_tester.run_problem_tests(self.path, pytest_extra_args)
        if retcode != 0:
            raise problemlib.ProblemTestError(f"Tests failed with error code {retcode}")


class DefaultProblem(Problem):
    """Used when the problem is unspecified."""

    def __init__(self):
        pass

    def get_module(self):
        module = types.ModuleType("problem")
        module.Input = problemlib.BaseInput
        module.Output = problemlib.BaseOutput
        return module


def load_problem(competition):
    import tg  # noqa: PLC0415

    if not competition.problem:
        return DefaultProblem()

    for path in tg.config.get("problems.search_paths", "").split():
        if not path:
            continue
        path = pathlib.Path(path)
        if (path / competition.problem).is_dir():
            return Problem(path / competition.problem)
    raise ValueError(f"No problem named {competition.problem}")
