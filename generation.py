from itertools import product
from math import factorial

from stack import *


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
        for g in ZISRoR(self.arity - 1, self.size - 1):
            yield Right(g)


class CompositionGenerator(Generation):
    def __iter__(self):
        for size in range(1, self.size - 1):
            for arity in range(1, size + 1):
                for main_program in ZSoR(arity, size):
                    for compound_program in self._compound(arity, self.size - 1 - size):
                        yield Composition(main_program, *compound_program)

    def _compound(self, n, size):
        for composition in self._composition(n, size):
            for prod in product(*[ZISRLoR(self.arity, l) for l in composition]):
                print(prod)
                yield prod

    def _composition(self, n, size):
        min_length = 1 if self.arity == 0 else self.arity
        if n == 1:
            yield (size,)
        else:
            for length in range(min_length, size - (n - 1) * min_length + 1):
                for recursive_composition in self._composition(n - 1, size - length):
                    yield (length,) + recursive_composition


class RecursionGenerator(Generation):
    def __iter__(self):
        for size in range(1, self.size - 1):
            for zero in ZISRLoR(self.arity - 1, size):
                for recursive in ZISRLoR(self.arity + 1, self.size - 1 - size):
                    yield Recursion(zero, recursive)


class ZSoR(Generation):
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
        yield Successor()

    def RLoR(self):
        yield from RecursionGenerator(self.arity, self.size)


class ZISoR(ZSoR):
    def IS(self):
        yield Identity()
        yield from super().IS()

    def __len__(self):
        return len(tuple(iter(self)))


class ZISRoR(ZISoR):
    def RLoR(self):
        yield from RightGenerator(self.arity, self.size)
        yield from super().RLoR()


class ZISRLoR(ZISRoR):
    def RLoR(self):
        yield from LeftGenerator(self.arity, self.size)
        yield from super().RLoR()


def check(language, program, lst):
    for i in range(len(lst)):
        if Program(program).execute(i)[1].what != lst[i]:
            return
    print(printer(language, program))


def main():
    language = {Zero: 'Z', Identity: 'I', Successor: 'S', Left: '<', Right: '>', Composition: 'o', Recursion: 'R'}
    result = [factorial(x) for x in range(10)]
    for i in range(15):
        print(i)
        for program in ZISoR(1, i):
            check(language, program, result)


if __name__ == '__main__':
    main()
