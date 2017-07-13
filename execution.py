from math import log
from time import time

from archive.tree_format import format_tree


def newton(n):
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def cantor(value):
    n = newton(2 * value)
    if n * (n + 1) // 2 > value:
        n -= 1
    p = n * (n + 1) // 2
    x = value - p
    return x, n - x


def cantor_inverse(x, y):
    return ((x + y) * (x + y) + 3 * x + y) // 2


def cantor_n(value, n):
    if n == 1:
        return value,
    if n == 2:
        return cantor(value)
    mid = n // 2
    i, j = cantor(value)
    return cantor_n(i, mid) + cantor_n(j, n - mid)


def cantor_inverse_n(*args):
    n = len(args)
    if n == 1:
        return args[0]
    if n == 2:
        return cantor_inverse(*args)
    mid = n // 2
    return cantor_inverse(cantor_inverse_n(*args[:mid]), cantor_inverse_n(*args[mid:]))


def pairing_exp2(n):
    if not n:
        return 0, 0
    x = n
    while not x & 1:
        x = x // 2
    v = (x + 1) // 2
    y = n // x
    return int(log(y, 2)), v


def pairing_exp2_inverse(u, v):
    if not u and not v:
        return 0
    return 2 ** u * (2 * v - 1)


class ArityException(Exception):
    def __init__(self, expression, expected, value):
        self.expression = expression
        self.expected = expected
        self.value = value

    def __str__(self):
        return f"Arity Exception: expression '{self.expression}' expected {self.expected} but {self.value} given"


class InvalidProgram(Exception):
    pass


class Expression:
    def __init__(self, what, closed=True, *params):
        self.what = what
        self.closed = closed
        self.params = params

    def __call__(self):
        if self.closed:
            return self
        result = self.what(*self.params)
        self.what = result.what
        self.closed = result.closed
        self.params = result.params
        return self

    def __str__(self):
        if self.closed:
            return str(self.what)
        return f"{self.what}({', '.join(map(str, self.params[1:]))})"

    __repr__ = __str__


class Function:
    def __new__(cls, *children):
        instance = super().__new__(cls)
        instance.__init__(*children)
        for p, inst in table:
            if instance == p and instance.__class__ != Function:
                return inst(*children)
        return instance

    def __init__(self, arity=0, depth=0, *children):
        self.arity = arity
        self.depth = depth
        self.children = children

    def __call__(self, *expression):
        if self.arity != len(expression):
            raise ArityException(self, self.arity, len(expression))

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(map(repr, self.children))})"

    def execute(self, *params, step=-1, display=(), bin_output=False):
        step_counter = 0
        peek = None
        stack = list()
        stack.insert(0, self(stack, *[Expression(arg) for arg in params]))
        if step_counter in display:
            print(step_counter, f"{self}({', '.join(map(str, params))})")
        while stack and (step == -1 or step > step_counter):
            if bin_output and isinstance(stack[0].what, Successor):
                return step_counter, True
            step_counter += 1
            peek = stack[-1]
            if step_counter in display:
                print(step_counter, stack)
            if peek.closed:
                stack.pop()
            else:
                peek()
        if bin_output:
            return step_counter, peek.what > 0
        return step_counter, peek.what

    @classmethod
    def build(cls, program):
        return cls()

    def __contains__(self, item):
        if any(child == item for child in self.children):
            return True
        return any(item in child for child in self.children)

    def __eq__(self, other):
        if other.__class__ == Function:
            return self.arity == other.arity
        if self.__class__ == other.__class__:
            return all(self_child == other_child for self_child, other_child in zip(self.children, other.children))
        return False

    def __hash__(self):
        return 0


class Zero(Function):
    def __call__(self, stack, *expression):
        super().__call__(*expression)
        return Expression(0)

    def __hash__(self):
        return 1


class Identity(Function):
    def __init__(self):
        super().__init__(arity=1)

    def __call__(self, stack, *expression):
        super().__call__(*expression)
        return expression[0]

    def __hash__(self):
        return 2


class Successor(Function):
    def __init__(self):
        super().__init__(arity=1)

    def __call__(self, stack, *expression):
        super().__call__(*expression)
        if expression[0].closed:
            return Expression(expression[0].what + 1)
        stack.append(expression[0])
        return Expression(self, False, stack, *expression)

    def __hash__(self):
        return 3


class Projection(Function):
    def __init__(self, children: Function):
        super().__init__(children.arity + 1, children.depth, children)

    @classmethod
    def build(cls, program):
        return cls(Interpreter.next_function(program))


class Left(Projection):
    def __call__(self, stack, *expression):
        super().__call__(*expression)
        return Expression(self.children[0], False, stack, *expression[1:])

    def __hash__(self):
        return 4 * hash(self.children[0])


class Right(Projection):
    def __call__(self, stack, *expression):
        super().__call__(*expression)
        return Expression(self.children[0], False, stack, *expression[:-1])

    def __hash__(self):
        return 5 * hash(self.children[0])


class Composition(Function):
    def __init__(self, *children: Function):
        if len(children) != children[0].arity + 1:
            raise ArityException(self, children[0].arity + 1, len(children))
        super().__init__(children[1].arity, max([f.depth for f in children]), *children)

    def __call__(self, stack, *expression):
        super().__call__(*expression)
        return Expression(self.children[0], False, stack,
                          *[Expression(child, False, stack, *expression) for child in self.children[1:]])

    @classmethod
    def build(cls, program):
        main_child = next(program).build(program)
        return cls(main_child, *[Interpreter.next_function(program) for _ in range(main_child.arity)])

    def __hash__(self):
        return 6 * cantor_inverse_n(*map(hash, self.children))


class Recursion(Function):
    def __init__(self, zero: Function, recursive: Function):
        super().__init__(zero.arity + 1, max(zero.depth, recursive.depth + 1), zero, recursive)
        if zero.arity + 1 != recursive.arity - 1:
            raise ArityException(self, zero.arity + 1, recursive.arity - 1)

    def __call__(self, stack, *expression):
        super().__call__(*expression)
        if expression[0].closed:
            if expression[0].what:
                return Expression(self.children[1], False, stack, Expression(expression[0].what - 1),
                                  Expression(self, False, stack, Expression(expression[0].what - 1), *expression[1:]),
                                  *expression[1:])
            else:
                return Expression(self.children[0], False, stack, *expression[1:])
        stack.append(expression[0])
        return Expression(self, False, stack, *expression)

    @classmethod
    def build(cls, program):
        return cls(Interpreter.next_function(program), Interpreter.next_function(program))

    def __hash__(self):
        return 7 * cantor_inverse(hash(self.children[0]), hash(self.children[1]))


class Add(Function):
    def __init__(self, *children):
        super().__init__(2, 1)

    def __call__(self, stack, *expression):
        super().__call__(*expression)
        if expression[0].closed and expression[1].closed:
            return Expression(expression[0].what + expression[1].what)
        for e in expression:
            if not e.closed:
                stack.append(e)
        return Expression(self, False, stack, *expression)


class Mul(Function):
    def __init__(self, *children):
        super().__init__(2, 2, *children)

    def __call__(self, stack, *expression):
        if len(expression) == self.arity:
            zero_result = Expression(self.children[0], False, stack, expression[1])
            stack.append(zero_result)
            return Expression(self, False, stack, *expression, zero_result)
        elif len(expression) == self.arity + 1:
            result = expression[self.arity]
            if expression[0].closed and expression[1].closed and result.closed:
                return Expression(result.what + expression[0].what * expression[1].what)
            for e in expression:
                if not e.closed:
                    stack.append(e)
            return Expression(self, False, stack, *expression)
        super().__call__(*expression)


class Sous(Function):
    def __init__(self, *children):
        super().__init__(2, 2)

    def __call__(self, stack, *expression):
        super().__call__(*expression)
        if expression[0].closed and expression[1].closed:
            result = expression[0].what - expression[1].what
            if result >= 0:
                return Expression(expression[0].what - expression[1].what)
            return Expression(0)
        for e in expression:
            if not e.closed:
                stack.append(e)
        return Expression(self, False, stack, *expression)


class Predecessor(Function):
    def __init__(self, *children):
        super().__init__(1, 1, *children)

    def __call__(self, stack, *expression):
        super().__call__(*expression)

        if expression[0].closed:
            if expression[0].what:
                return Expression(expression[0].what - 1)
            return Expression(0)
        stack.append(expression[0])
        return Expression(self, False, stack, *expression)


class Interpreter:
    default = {'F': Function, 'Z': Zero, 'I': Identity, 'S': Successor, '<': Left, '>': Right, 'o': Composition,
               'R': Recursion, 'A': Add, 'P': Predecessor, 'M': Mul, 'D': Sous}

    def __init__(self, language=default):
        self.language = language

    def compile(self, code):
        instructions = self.parse(code)
        program = Interpreter.next_function(instructions)
        if len(list(instructions)):
            raise InvalidProgram()
        return program

    @staticmethod
    def next_function(instructions):
        try:
            return next(instructions).build(instructions)
        except StopIteration:
            raise InvalidProgram()

    def parse(self, code):
        return (self.language[char] for char in code if char in self.language)


class Printer:
    default = {Function: 'F', Zero: 'Z', Identity: 'I', Successor: 'S', Left: '<', Right: '>', Composition: 'o',
               Recursion: 'R', Add: 'A', Predecessor: 'P', Mul: 'M', Sous: 'D'}

    def __init__(self, language=default):
        self.language = language

    def print(self, program):
        return f"{self.language[program.__class__]}{''.join(map(lambda child: self.print(child), program.children))}"

    def tree(self, program):
        return format_tree(program, format_node=lambda node: self.language[node.__class__],
                           get_children=lambda node: node.children)


table = list()
table.append((Recursion(Identity(), Left(Right(Successor()))), Add))
table.append((Recursion(Zero(), Right(Function(1))), Predecessor))
table.append((Recursion(Function(1), Left(Add())), Mul))
table.append((Recursion(Identity(), Left(Right(Predecessor()))), Sous))


def main():
    t0 = time()
    executable = Interpreter().compile("""
    R
    ├── oSS
    └── <
        └── R
            ├── I
            └── <
                └── >
                    └── S""")
    for i in range(10):
        for j in range(10):
            step, result = executable.execute(i, j, display=range(0), bin_output=False)
            print(i, j, step, result)
    # print(repr(executable))
    print(time() - t0)


if __name__ == '__main__':
    main()
