from tree_format import format_tree

UNKNOWN_RESULT = -1


class Language(dict):
    def __call__(self, name, args, kwargs):
        token = kwargs[Function.token]
        self[token] = type(name, args, kwargs)
        return self[token]

    def parse(self, text):
        return (self[char] for char in text if char in self)


class Expression:
    def __init__(self, what, *args):
        self.what = what
        self.args = args

    def __call__(self) -> int:
        try:
            self.what = self.what(*self.args)
        except TypeError:
            pass
        return self.what

    def __str__(self):
        return f"{self.what}({', '.join(map(str, self.args))})"


class Function(Expression):
    token = 'token'
    language = Language()

    def __init__(self, *children, what=UNKNOWN_RESULT, args=(), arity=0, depth=0):
        super().__init__(what, *args)
        self.arity = arity
        self.depth = depth
        self.children = children

    def __call__(self, *expression: Expression) -> int:
        return Expression.__call__(self)

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
        super().__init__(what=0)

    def __call__(self):
        return Function.__call__(self)

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Zero()


class Identity(Function, metaclass=Function.language):
    token = 'I'

    def __init__(self):
        super().__init__(arity=1)

    def __call__(self, expression: Expression):
        return expression()

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Identity()


class Successor(Function, metaclass=Function.language):
    token = 'S'

    def __init__(self):
        super().__init__(arity=1)

    def __call__(self, expression: Expression):
        return expression() + 1

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Successor()


class Left(Function, metaclass=Function.language):
    token = '<'

    def __init__(self, inner_function):
        super().__init__(inner_function, arity=inner_function.arity + 1)
        self.inner_function = inner_function

    def __call__(self, *expression: Expression):
        return self.inner_function(*expression[1:])

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Left(building(program))


class Right(Function, metaclass=Function.language):
    token = '>'

    def __init__(self, inner_function):
        super().__init__(inner_function, arity=inner_function.arity + 1)
        self.inner_function = inner_function

    def __call__(self, *expression: Expression):
        return self.inner_function(*expression[:-1])

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Right(building(program))


class Composition(Function, metaclass=Function.language):
    token = 'o'

    def __init__(self, main_function, *compound):
        super().__init__(main_function, *compound, arity=compound[0].arity)
        if main_function.arity != len(compound) or any(comp.arity != self.arity for comp in compound):
            raise ArityException()
        self.main_function = main_function
        self.compound = compound

    def __call__(self, *expression: Expression):
        return self.main_function(*[Expression(comp, *expression) for comp in self.compound])

    @staticmethod
    def build(program, building=Function.build) -> Function:
        f = building(program)
        g = [building(program) for _ in range(f.arity)]
        return Composition(f, *g)


class Recursion(Function, metaclass=Function.language):
    token = 'R'

    def __init__(self, zero, recursive):
        super().__init__(zero, recursive, arity=zero.arity + 1)
        if self.arity != recursive.arity - 1:
            raise ArityException()
        self.zero = zero
        self.recursive = recursive

    def __call__(self, counter: Expression, *expression: Expression):
        self.n = counter()
        self.expression = expression
        return self._recursive_call()

    def _recursive_call(self):
        if self.n == 0:
            return self.zero(*self.expression)
        self.n -= 1
        return self.recursive(Expression(self.n), self._recursive_call, *self.expression)

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Recursion(building(program), building(program))


class ArityException(Exception):
    pass


class InvalidProgram(Exception):
    pass


def build(text):
    generator = Function.language.parse(text)
    program = Function.build(generator)
    try:
        next(generator)
    except StopIteration:
        return program
    raise InvalidProgram()


def main():
    program = build(open("program/facto.rl").read())
    print(program(Expression(7)))


if __name__ == '__main__':
    main()
