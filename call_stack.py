def next_function(program):
    """
    Consume a token of the program to create the associated Function instance
    The function instance needs the program in constructor to build its children
    :param program: the current program generator of Function
    :return: the next function instance of the tree
    """
    return next(program).build(program)


class Interpreter:
    def __init__(self, **language):
        self.language = language

    def compile(self, code):
        program = self.parse(code)
        return Program(next_function(program))

    def parse(self, code):
        return (self.language[char] for char in code if char in self.language)


class Program:
    def __init__(self, main_function):
        self.main_function = main_function

    def execute(self, *args):
        step = 0
        result = self.main_function(*[Expression(arg, master=self) for arg in args])
        try:
            while True:
                step += 1
                result = result()

        except TypeError as e:
            return step, result
            # raise e
            # finally:
            # return step, result


class Expression:
    def __init__(self, what, *params, master=None):
        self.master = master
        self.what = what
        self.params = params
        self.closed = not callable(what)

    def __call__(self, *args, **kwargs):
        return self.result

    @property
    def result(self):
        if not self.closed:
            self.what = self.what(*self.params)
            self.closed = self.what.closed
        return self.what

    def __str__(self):
        if not self.closed:
            return f"{self.master}({', '.join(map(str, self.params))})"
        return f"Expression({self.what}, master={self.master})"

    __repr__ = __str__


class ArityException(Exception):
    pass


class Function:
    def __init__(self, arity=0, depth=0, *children):
        self.arity = arity
        self.depth = depth
        self.children = children

    def __call__(self, *expression):
        if len(expression) != self.arity:
            raise ArityException()

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

    @classmethod
    def build(cls, program):
        return cls()


class Zero(Function):
    def __call__(self, *expression):
        super().__call__(*expression)
        return Expression(0, master=self)


class Identity(Function):
    def __init__(self):
        super().__init__(arity=1)

    def __call__(self, *expression):
        super().__call__(*expression)
        if expression[0].closed:
            return Expression(expression[0].result, master=self)
        return Expression(self, expression[0].result, master=self)


class Successor(Function):
    def __init__(self):
        super().__init__(arity=1)

    def __call__(self, *expression):
        super().__call__(*expression)
        if expression[0].closed:
            return Expression(expression[0].result + 1, master=self)
        return Expression(self, expression[0].result, master=self)


class Projection(Function):
    def __init__(self, children: Function):
        super().__init__(children.arity + 1, children.depth, children)

    @classmethod
    def build(cls, program):
        return cls(next_function(program))


class Left(Projection):
    def __call__(self, *expression):
        super().__call__(*expression)
        return Expression(self.children[0], *expression[1:], master=self)


class Right(Projection):
    def __call__(self, *expression):
        super().__call__(*expression)
        return Expression(self.children[0], *expression[:-1], master=self)


class Composition(Function):
    def __init__(self, *children: Function):
        if len(children) != children[0].arity + 1:
            raise ArityException()
        super().__init__(children[1].arity, max([f.depth for f in children]), *children)

    def __call__(self, *expression):
        super().__call__(*expression)
        return Expression(self.children[0],
                          *[Expression(child, *expression, master=self) for child in self.children[1:]], master=self)

    @classmethod
    def build(cls, program):
        main_child = next(program).build(program)
        return cls(main_child, *[next_function(program) for _ in range(main_child.arity)])


class Recursion(Function):
    def __init__(self, zero: Function, recursive: Function):
        super().__init__(zero.arity + 1, max(zero.depth, recursive.depth + 1), zero, recursive)
        if zero.arity + 1 != recursive.arity - 1:
            raise ArityException()

    def __call__(self, *expression):
        super().__call__(*expression)
        if not expression[0].closed:
            return Expression(self, expression[0].result, *expression[1:], master='compteur')
        if not expression[0].result:
            return Expression(self.children[0], *expression[1:], master='f')
        counter = Expression(expression[0].result - 1, master='compteur - 1')
        return Expression(self.children[1], counter, Expression(self, counter, *expression[1:], master='recurtion'),
                          *expression[1:], master='g')

    @classmethod
    def build(cls, program):
        return cls(next_function(program), next_function(program))


def main():
    language = {'Z': Zero, 'I': Identity, 'S': Successor, '<': Left, '>': Right, 'o': Composition, 'R': Recursion}
    interpreter = Interpreter(**language)
    step, result = interpreter.compile("""R
├── Z
└── R
    ├── I
    └── <
        └── R
            ├── I
            └── <
                └── >
                    └── S""").execute(3)
    print(step, result)


if __name__ == '__main__':
    main()
