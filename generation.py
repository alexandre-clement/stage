from itertools import product
from math import factorial

from execution import *


def printer(language, program):
    return f"{language[program.__class__]}{''.join(printer(language, child) for child in program.children)}"


class Generation:
    def __init__(self, arity, size):
        self.arity = arity
        self.size = size


class LeftGenerator(Generation):
    def __iter__(self):
        for g in ZISRLoR(self.arity - 1, self.size - 1):
            yield Left(g)


class RightGenerator(Generation):
    def __iter__(self):
        if self.arity - 1:
            for g in ZISRoR(self.arity - 1, self.size - 1):
                yield Right(g)


class CompositionGenerator(Generation):
    def __iter__(self):
        for size in range(1, self.size - 1):
            for arity in range(1, size + 1):
                for main_program in ZoR(arity, size):
                    for compound_program in self._compound(arity, self.size - 1 - size):
                        yield Composition(main_program, *compound_program)

    def _compound(self, n, size):
        for composition in self._composition(n, size):
            if composition == (1,):
                for prod in product(*[ZoR(self.arity, l) for l in composition]):
                    yield prod
            else:
                for prod in product(*[ZISRLoR(self.arity, l) for l in composition]):
                    yield prod

    def _composition(self, n, size):
        min_length = 1 if self.arity == 0 else self.arity
        if n == 1:
            yield (size,)
        else:
            for length in range(min_length, size - (n - 1) * min_length + 1):
                for recursive_composition in self._composition(n - 1, size - length):
                    yield (length,) + recursive_composition


class MainCompositionGenerator(CompositionGenerator):
    def _compound(self, n, size):
        for composition in self._composition(n, size):
            if composition == (1,):
                for prod in product(*[ZoR(self.arity, l) for l in composition]):
                    yield prod
            else:
                for prod in product(*[ZoR(self.arity, l) for l in composition]):
                    yield prod


class RecursionGenerator(Generation):
    def __iter__(self):
        for size in range(1, self.size - 1):
            for recursive in ZISRLoR(self.arity + 1, self.size - 1 - size):
                if isinstance(recursive, Left) and isinstance(recursive.children[0], Identity):
                    continue
                if isinstance(recursive, Right) and isinstance(recursive.children[0], Successor):
                    continue
                for zero in ZISRLoR(self.arity - 1, size):
                    yield Recursion(zero, recursive)


class ZoR(Generation):
    def __iter__(self):
        if self.size == 1:
            if self.arity == 0:
                yield Zero()
            elif self.arity == 1:
                yield from self.IS()
        elif self.size >= 2:
            yield from CompositionGenerator(self.arity, self.size)
            if self.arity:
                yield from self.RLoR()

    def IS(self):
        if False:
            yield

    def RLoR(self):
        yield from RecursionGenerator(self.arity, self.size)


class ZSoR(ZoR):
    def IS(self):
        yield Successor()


class ZISoR(ZSoR):
    def IS(self):
        yield Identity()
        yield from super().IS()

    def __len__(self):
        return len(tuple(iter(self)))


class ProgramGenerator(ZISoR):
    def __iter__(self):
        if self.size == 1:
            if self.arity == 0:
                yield Zero()
            elif self.arity == 1:
                yield from self.IS()
        elif self.size >= 2:
            yield from MainCompositionGenerator(self.arity, self.size)
            if self.arity:
                yield from self.RLoR()

    def __len__(self):
        return len(list(iter(self)))


class ZISRoR(ZISoR):
    def RLoR(self):
        yield from RightGenerator(self.arity, self.size)
        yield from super().RLoR()


class ZISRLoR(ZISRoR):
    def RLoR(self):
        yield from LeftGenerator(self.arity, self.size)
        yield from super().RLoR()


def main():
    language = {Zero: 'Z', Identity: 'I', Successor: 'S', Left: '<', Right: '>', Composition: 'o', Recursion: 'R'}
    printer = Printer(language)
    result = [factorial(x) for x in range(10)]
    for i in range(21):
        print(i, len(ProgramGenerator(1, i)))


if __name__ == '__main__':
    main()
