from itertools import product
from math import factorial
from time import time

from tree_format import format_tree


class Language(dict):
    def __call__(self, name, args, kwargs):
        token = kwargs[Function.token]
        self[token] = type(name, args, kwargs)
        return self[token]

    def parse(self, text):
        return (self[char] for char in text if char in self)


class Function(object):
    language = Language()
    token = 'token'

    def __init__(self):
        self.arity = 0
        self.depth = 0
        self.children = ()

    def __call__(self, *x: int) -> int:
        pass

    def __str__(self):
        return format_tree(self, format_node=lambda node: node.token, get_children=lambda node: node.children)

    def __repr__(self):
        return f"{self.token}{''.join(map(repr, self.children))}"

    @staticmethod
    def build(program):
        return next(program).build(program)


class Zero(Function, metaclass=Function.language):
    token = 'Z'

    def __init__(self):
        super().__init__()

    def __call__(self) -> int:
        return 0

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Zero()


class Identity(Function, metaclass=Function.language):
    token = 'I'

    def __init__(self):
        super().__init__()
        self.arity = 1

    def __call__(self, x: int) -> int:
        return x

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Identity()


class Successor(Function, metaclass=Function.language):
    token = 'S'

    def __init__(self):
        super().__init__()
        self.arity = 1

    def __call__(self, x: int) -> int:
        return x + 1

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Successor()


class Left(Function, metaclass=Function.language):
    token = '<'

    def __init__(self, f: Function):
        super().__init__()
        self.f = f
        self.arity = f.arity + 1
        self.depth = f.depth
        self.children = (f,)

    def __call__(self, *x: int) -> int:
        return self.f(*x[1:])

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Left(building(program))


class Right(Function, metaclass=Function.language):
    token = '>'

    def __init__(self, f: Function):
        super().__init__()
        self.f = f
        self.arity = f.arity + 1
        self.depth = f.depth
        self.children = (f,)

    def __call__(self, *x: int) -> int:
        return self.f(*x[:-1])

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Right(building(program))


class Composition(Function, metaclass=Function.language):
    token = 'o'

    def __init__(self, f: Function, *g):
        super().__init__()
        self.f = f
        self.g = g
        self.children = (f,) + g
        self.arity = g[0].arity
        self.depth = max(int(child.depth) for child in self.children)

    def __call__(self, *x: int) -> int:
        return self.f(*[compound(*x) for compound in self.g])

    @staticmethod
    def build(program, building=Function.build) -> Function:
        f = building(program)
        g = [building(program) for _ in range(f.arity)]
        return Composition(f, *g)


class Recursion(Function, metaclass=Function.language):
    token = 'R'

    def __init__(self, f: Function, g: Function):
        super().__init__()
        self.f = f
        self.g = g
        self.children = (f, g)
        self.arity = f.arity + 1
        self.depth = max(int(child.depth) for child in self.children) + 1

    def __call__(self, n: int, *x: int) -> int:
        result = self.f(*x)
        for i in range(n):
            result = self.g(i, result, *x)
        return result

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Recursion(building(program), building(program))


class Generator(object):
    def __init__(self, arity: int = 0, size: int = 0):
        self.size = size
        self.arity = arity

    def __iter__(self):
        if self.size == 1:
            yield from self._atom()
        elif self.size > 1:
            if self.arity == 0:
                yield from self.zero_arity()
            else:
                yield from self.left()
                yield from self.right()
                yield from self.composition()
                yield from self.recursion()

    def _atom(self):
        if self.arity == 0:
            yield Zero()
        elif self.arity == 1:
            yield from (Identity(), Successor())

    def zero_arity(self):
        yield from CompositionGenerator(self.arity, self.size)

    def left(self):
        yield from LeftGenerator(self.arity, self.size)

    def right(self):
        yield from RightGenerator(self.arity, self.size)

    def composition(self):
        yield from CompositionGenerator(self.arity, self.size)

    def recursion(self):
        yield from RecursionGenerator(self.arity, self.size)


class NoLeftOrRightGenerator(Generator):
    def __init__(self, arity: int = 0, size: int = 0):
        super().__init__(arity, size)

    def __iter__(self):
        if self.size == 1:
            yield from self._atom()
        elif self.size > 1:
            if self.arity == 0:
                yield from self.zero_arity()
            else:
                yield from self.composition()
                yield from self.recursion()


class ProgramGenerator(NoLeftOrRightGenerator):
    def __init__(self, arity: int = 0, size: int = 0):
        super().__init__(arity, size)

    def __len__(self):
        return len(list(iter(self)))


class NoLeftOrRightOrIdentityGenerator(NoLeftOrRightGenerator):
    def __init__(self, arity: int = 0, size: int = 0):
        super().__init__(arity, size)

    def _atom(self):
        if self.arity == 0:
            yield Zero()
        elif self.arity == 1:
            yield Successor()


class LeftGenerator(Generator):
    def __init__(self, arity: int = 0, size: int = 0):
        super().__init__(arity - 1, size - 1)

    def __iter__(self):
        for program in Generator(self.arity, self.size):
            yield Left(program)


class NoMoreLeftGenerator(Generator):
    def __init__(self, arity: int = 0, size: int = 0):
        super().__init__(arity, size)

    def left(self):
        yield from iter(())


class RightGenerator(Generator):
    def __init__(self, arity: int = 0, size: int = 0):
        super().__init__(arity - 1, size - 1)

    def __iter__(self):
        for program in NoMoreLeftGenerator(self.arity, self.size):
            yield Right(program)


class CompositionGenerator(Generator):
    def __init__(self, arity: int = 0, size: int = 0):
        super().__init__(arity, size - 1)

    def __iter__(self):
        for size in range(1, self.size):
            for arity in range(1, size + 1):
                for main_program in NoLeftOrRightOrIdentityGenerator(arity, size):
                    for compound_program in self._compound(arity, self.size - size):
                        yield Composition(main_program, *compound_program)

    def _compound(self, n, size):
        for composition in self._composition(n, size):
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


class RecursionGenerator(Generator):
    def __init__(self, arity: int = 0, size: int = 0):
        super().__init__(arity, size - 1)

    def __iter__(self):
        for size in range(1, self.size):
            for zero in Generator(self.arity - 1, size):
                for recursive in Generator(self.arity + 1, self.size - size):
                    yield Recursion(zero, recursive)


def test_interpreter():
    addition = Recursion(Identity(), Left(Right(Successor())))
    print(7 + 8, addition(7, 8))
    print(addition)

    multiplication = Function.build(Language.parse("R<Z<RI<>SIS"))
    print(7 * 8, multiplication(7, 8))
    print(multiplication)

    fibonacci = Function.build(Language.parse(open("program/code.rl").read()))
    for i in range(1):
        print(i, fibonacci(i))
    print(fibonacci)

    test = Function.build(Language.parse("RI<R<Z<RI<>S"))
    for i in range(4):
        for j in range(10):
            print(j ** (i + 1), test(i, j))
    print(test)


def check(program, lst):
    for i in range(len(lst)):
        if program(i) != lst[i]:
            return
    print(program)
    print(repr((program)))


def main():
    # print(Function.build(Function.language.parse(open("program/facto.rl").read()))(8))
    result = [factorial(x) - 1 for x in range(10)]
    print(result)
    t0 = time()
    for i in range(0, 15):
        print(i, len(ProgramGenerator(1, i)))
    print(time() - t0)


if __name__ == '__main__':
    main()
