from itertools import product
from math import factorial

from execution import *


class Generation:
    def __init__(self, arity, size):
        self.arity = arity
        self.size = size


class LeftGenerator(Generation):
    def __iter__(self):
        for g in Generator(self.arity - 1, self.size - 1):
            yield Left(g)


class RightGenerator(Generation):
    def __iter__(self):
        if self.arity - 1:
            for g in NoLeft(self.arity - 1, self.size - 1):
                yield Right(g)


class CompositionGenerator(Generation):
    def __iter__(self):
        for size in range(1, self.size - 1):
            for arity in range(1, size + 1):
                for main_program in NoIdentityNorProjection(arity, size):
                    for compound_program in self._compound(arity, self.size - 1 - size):
                        if main_program == Predecessor() and all(
                                all(isinstance(child, Successor) or isinstance(child, Composition) for child in
                                    compound) for compound in compound_program):
                            continue
                        if main_program == Successor() and compound_program == (Predecessor(),):
                            continue
                        if main_program == Add() and Zero() in compound_program:
                            continue
                        if all(isinstance(child, Successor) or isinstance(child, Composition) for child in
                               main_program):
                            if all(all(isinstance(child, Successor) or isinstance(child, Composition) for child in
                                       compound) for compound in compound_program):
                                if isinstance(main_program, Composition):
                                    continue
                        yield Composition(main_program, *compound_program)

    def _compound(self, n, size):
        for composition in self._composition(n, size):
            if len(composition) == 1:
                for prod in product(*[NoIdentityNorProjection(self.arity, l) for l in composition]):
                    yield prod
            else:
                for prod in product(*[Generator(self.arity, l) for l in composition]):
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
            for recursive in Generator(self.arity + 1, self.size - 1 - size):
                if recursive == Left(Identity()):
                    continue
                for zero in Generator(self.arity - 1, size):
                    if zero == Zero():
                        if recursive == Left(Left(Zero())):
                            continue
                        if recursive == Left(Recursion(Zero(), Function(2))):
                            continue
                        if recursive == Left(Successor()):
                            continue
                        if recursive == Right(Successor()):
                            continue
                        if recursive == Right(Composition(Successor(), Successor())):
                            continue
                        if recursive == Left(Left(Composition(Successor(), Zero()))):
                            continue
                        if recursive == Recursion(Identity(), Left(Left(Successor()))):
                            continue
                        if recursive == Recursion(Successor(), Left(Left(Successor()))):
                            continue
                        if recursive == Recursion(Identity(), Left(Right(Identity()))):
                            continue
                        if recursive == Recursion(Successor(), Left(Right(Identity()))):
                            continue
                        if recursive == Recursion(Identity(), Right(Right(Successor()))):
                            continue
                    if zero == Identity() and recursive == Left(Left(Identity())):
                        continue
                    if isinstance(zero, Right) and isinstance(recursive, Right):
                        continue
                    if zero == Composition(Successor(), Zero()) and recursive == Left(Successor()):
                        continue
                    yield Recursion(zero, recursive)


class Generator(Generation):
    def __iter__(self):
        if self.size == 1:
            if self.arity == 0:
                yield from self.zero()
            elif self.arity == 1:
                yield from self.identity()
                yield from self.successor()
        elif self.size > 1:
            yield from self.composition()
            if self.arity:
                yield from self.left()
                yield from self.right()
                yield from self.recursion()

    def zero(self):
        yield Zero()

    def identity(self):
        yield Identity()

    def successor(self):
        yield Successor()

    def composition(self):
        yield from CompositionGenerator(self.arity, self.size)

    def left(self):
        yield from LeftGenerator(self.arity, self.size)

    def right(self):
        yield from RightGenerator(self.arity, self.size)

    def recursion(self):
        yield from RecursionGenerator(self.arity, self.size)


class NoLeft(Generator):
    def left(self):
        if False:
            yield


class NoIdentity(Generator):
    def identity(self):
        if False:
            yield


class NoRight(Generator):
    def right(self):
        if False:
            yield


class NoProjection(NoLeft, NoRight):
    pass


class NoIdentityNorProjection(NoIdentity, NoProjection):
    pass


class Main(NoProjection):
    def __len__(self):
        return len(list(iter(self)))


def main():
    for i in range(20):
        print(i, len(Main(1, i)))
        #for p in Main(1, i):
            #print(Printer().tree(p))


if __name__ == '__main__':
    main()
