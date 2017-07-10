def next_function(program):
    try:
        return next(program).build(program)
    except StopIteration:
        raise InvalidProgram()


class Expression:
    def __init__(self, what, *params):
        self.what = what
        self.params = params
        self.closed = isinstance(what, int)

    def __call__(self):
        return self.result

    @property
    def result(self):
        if self.closed:
            return self.what
        return self.what(*self.params)

    def successor(self):
        if self.closed:
            return Expression(self.what + 1)
        return Expression(Successor, self)

    def predecessor(self):
        if self.closed:
            return Expression(self.what - 1)
        return self.result.predecessor()

    def __str__(self):
        if self.closed:
            return str(self.what)
        return f"{self.what}({', '.join(map(str, self.params))})"


class InvalidProgram(Exception):
    pass


class Interpreter:
    def __init__(self, **language):
        self.language = language

    def compile(self, code):
        instructions = self.parse(code)
        program = Program(next_function(instructions))
        try:
            next(instructions)
        except StopIteration:
            return program
        raise InvalidProgram()

    def parse(self, code):
        return (self.language[char] for char in code if char in self.language)


class Program:
    def __init__(self, main_function):
        self.main_function = main_function

    def execute(self, *args, step=-1, display=()):
        program = self.main_function(*[Expression(arg) for arg in args])
        step_counter = 0
        print(0, f"{self.main_function}({', '.join(map(str, args))})")
        try:
            while step == -1 or step > step_counter:
                step_counter += 1
                if step_counter in display:
                    print(step_counter, program)
                program = program()
        except TypeError:
            pass
        return step_counter - 1, program


class ArityException(Exception):
    pass


class Function:
    def __init__(self, arity=0, depth=0, *children):
        self.arity = arity
        self.depth = depth
        self.children = children

    def __call__(self, *expression):
        if self.arity != len(expression):
            raise ArityException()

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"{self.__class__.__name__[0]}({', '.join(map(repr, self.children))})"

    @classmethod
    def build(cls, program):
        return cls()


class Zero(Function):
    def __call__(self, *expression):
        super().__call__(*expression)
        return Expression(0)


class Identity(Function):
    def __init__(self):
        super().__init__(arity=1)

    def __call__(self, *expression):
        super().__call__(*expression)
        return expression[0]


class Successor(Function):
    def __init__(self):
        super().__init__(arity=1)

    def __call__(self, *expression):
        super().__call__(*expression)
        if expression[0].closed:
            return expression[0].successor()
        return Expression(self, expression[0].result)


class Projection(Function):
    def __init__(self, children: Function):
        super().__init__(children.arity + 1, children.depth, children)

    @classmethod
    def build(cls, program):
        return cls(next_function(program))


class Left(Projection):
    def __call__(self, *expression):
        super().__call__(*expression)
        return Expression(self.children[0], *expression[1:])


class Right(Projection):
    def __call__(self, *expression):
        super().__call__(*expression)
        return Expression(self.children[0], *expression[:-1])


class Composition(Function):
    def __init__(self, *children: Function):
        if len(children) != children[0].arity + 1:
            raise ArityException()
        super().__init__(children[1].arity, max([f.depth for f in children]), *children)

    def __call__(self, *expression):
        super().__call__(*expression)
        return Expression(self.children[0], *[Expression(child, *expression) for child in self.children[1:]])

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
        if expression[0].closed:
            if expression[0].result:
                return Expression(self.children[1], expression[0].predecessor(),
                                  Expression(self, expression[0].predecessor(), *expression[1:]), *expression[1:])
            else:
                return Expression(self.children[0], *expression[1:])
        return Expression(self, expression[0].result, *expression[1:])

    @classmethod
    def build(cls, program):
        return cls(next_function(program), next_function(program))


def main():
    interpreter = Interpreter(Z=Zero, I=Identity, S=Successor, **{'<': Left, '>': Right}, o=Composition, R=Recursion)
    step, result = interpreter.compile("RZRS<>oSS").execute(2, display=range(9999))
    print(step, result)


if __name__ == '__main__':
    main()
