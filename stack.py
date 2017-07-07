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
        if self.closed:
            return self
        self.copy(self.what(*self.params))
        return self

    def copy(self, other):
        self.what = other.what
        self.params = other.params
        self.closed = other.closed

    @property
    def result(self):
        return self().what

    def predecessor(self):
        if self.closed:
            return Expression(self.what - 1)
        return self.result.predecessor()

    def __str__(self):
        if self.closed:
            return str(self.what)
        return f"{self.what}({', '.join(map(str, self.params[1:]))})"

    __repr__ = __str__


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
        stack = []
        stack.append(self.main_function(stack, *[Expression(arg) for arg in args]))
        step_counter = 0
        if step_counter in display:
            print(step_counter, f"{self.main_function}({', '.join(map(str, args))})")
        peek = -1
        while stack and step == -1 or step > step_counter:
            step_counter += 1
            peek = stack[-1]
            if step_counter in display:
                print(step_counter, stack)
            if not peek.closed:
                peek.copy(peek())
            else:
                stack.pop()
        return step_counter, peek


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
    def __call__(self, stack, *expression):
        super().__call__(*expression)
        return Expression(0)


class Identity(Function):
    def __init__(self):
        super().__init__(arity=1)

    def __call__(self, stack, *expression):
        super().__call__(*expression)
        return expression[0]


class Successor(Function):
    def __init__(self):
        super().__init__(arity=1)

    def __call__(self, stack, *expression):
        super().__call__(*expression)
        if expression[0].closed:
            return Expression(expression[0].result + 1)
        stack.append(expression[0])
        return Expression(self, stack, *expression)


class Projection(Function):
    def __init__(self, children: Function):
        super().__init__(children.arity + 1, children.depth, children)

    @classmethod
    def build(cls, program):
        return cls(next_function(program))


class Left(Projection):
    def __call__(self, stack, *expression):
        super().__call__(*expression)
        return Expression(self.children[0], stack, *expression[1:])


class Right(Projection):
    def __call__(self, stack, *expression):
        super().__call__(*expression)
        return Expression(self.children[0], stack, *expression[:-1])


class Composition(Function):
    def __init__(self, *children: Function):
        if len(children) != children[0].arity + 1:
            raise ArityException()
        super().__init__(children[1].arity, max([f.depth for f in children]), *children)

    def __call__(self, stack, *expression):
        super().__call__(*expression)
        return Expression(self.children[0], stack,
                          *[Expression(child, stack, *expression) for child in self.children[1:]])

    @classmethod
    def build(cls, program):
        main_child = next(program).build(program)
        return cls(main_child, *[next_function(program) for _ in range(main_child.arity)])


class Recursion(Function):
    def __init__(self, zero: Function, recursive: Function):
        super().__init__(zero.arity + 1, max(zero.depth, recursive.depth + 1), zero, recursive)
        if zero.arity + 1 != recursive.arity - 1:
            raise ArityException()

    def __call__(self, stack, *expression):
        super().__call__(*expression)
        if expression[0].closed:
            if expression[0].result:
                return Expression(self.children[1], stack, expression[0].predecessor(),
                                  Expression(self, stack, expression[0].predecessor(), *expression[1:]),
                                  *expression[1:])
            else:
                return Expression(self.children[0], stack, *expression[1:])
        stack.append(expression[0])
        return Expression(self, stack, *expression)

    @classmethod
    def build(cls, program):
        return cls(next_function(program), next_function(program))


def main():
    language = {'Z': Zero, 'I': Identity, 'S': Successor, '<': Left, '>': Right, 'o': Composition, 'R': Recursion}
    interpreter = Interpreter(**language)
    step, result = interpreter.compile("RZRS<>oSS").execute(200, step=10, display=range(99))
    print(step, result)


if __name__ == '__main__':
    main()
