UNKNOWN_RESULT = -1


class Language(dict):
    def __call__(self, name, args, kwargs):
        token = kwargs[Function.token]
        self[token] = type(name, args, kwargs)
        return self[token]

    @staticmethod
    def parse(text):
        program = (Function.language[char] for char in text if char in Function.language)
        return program


class Expression:
    def __init__(self, what, *args):
        self.what = what
        self.args = args

    def __call__(self) -> int:
        if self.args != ():
            self.what = self.what(*self.args)
            self.args = ()
        return self.what


class Function(Expression):
    token = 'token'
    language = Language()

    def __init__(self, *children, what=UNKNOWN_RESULT, args=(), arity=0, depth=0):
        super().__init__(what, args)
        self.arity = arity
        self.depth = depth
        self.children = children

    def __call__(self, *expression: Expression) -> int:
        return Expression.__call__(self)


class Zero(Function):
    token = 'Z'

    def __init__(self):
        super().__init__(what=0)

    def __call__(self):
        return Function.__call__(self)


class Identity(Function):
    token = 'I'

    def __init__(self):
        super().__init__(arity=1)

    def __call__(self, expression: Expression):
        return expression()


class Successor(Function):
    token = 'S'

    def __init__(self):
        super().__init__(arity=1)

    def __call__(self, expression: Expression):
        return expression() + 1


class Left(Function):
    token = '<'

    def __init__(self, inner_function):
        super().__init__(inner_function, arity=inner_function.arity + 1)
        self.inner_function = inner_function

    def __call__(self, *expression: Expression):
        return self.inner_function(*expression[1:])


class Right(Function):
    token = '>'

    def __init__(self, inner_function):
        super().__init__(inner_function, arity=inner_function.arity + 1)
        self.inner_function = inner_function

    def __call__(self, *expression: Expression):
        return self.inner_function(*expression[:-1])


class Composition(Function):
    token = 'o'

    def __init__(self, main_function, *compound):
        super().__init__(main_function, *compound, arity=compound[0].arity)
        if main_function.arity != len(compound) or any(comp.arity != self.arity for comp in compound):
            raise ArityException()
        self.main_function = main_function
        self.compound = compound

    def __call__(self, *expression: Expression):
        return self.main_function(*[Expression(comp, *expression) for comp in self.compound])


class Recursion(Function):
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


class ArityException(Exception):
    pass


def main():
    print(Composition(Left(Right(Identity())), Identity(), Successor(), Successor())(Expression(10)))


if __name__ == '__main__':
    main()
