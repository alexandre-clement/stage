from archive.tree_format import format_tree


class ArityException(Exception):
    def __init__(self, expression, expected, value):
        self.expression = expression
        self.expected = expected
        self.value = value

    def __str__(self):
        return f"Arity Exception: expression '{self.expression}' expected {self.expected} but {self.value} given"


class InvalidProgram(Exception):
    pass


class Interpreter:
    def __init__(self, **language):
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
    def __init__(self, language):
        self.language = language

    def print(self, program):
        return f"{self.language[program.__class__]}{''.join(map(lambda child: self.print(child), program.children))}"

    def tree(self, program):
        return format_tree(program, format_node=lambda node: self.language[node.__class__],
                           get_children=lambda node: node.children)


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
        return f"{self.__class__.__name__[0]}({', '.join(map(repr, self.children))})"

    def execute(self, *params, step=-1, display=(), bin_output=False):
        step_counter = 0
        peek = 0
        stack = list()
        stack.append(self(stack, *[Expression(arg) for arg in params]))
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
            expression[0].what += 1
            return expression[0]
        stack.append(expression[0])
        return Expression(self, False, stack, *expression)


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


class Right(Projection):
    def __call__(self, stack, *expression):
        super().__call__(*expression)
        return Expression(self.children[0], False, stack, *expression[:-1])


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


class Recursion(Function):
    def __init__(self, zero: Function, recursive: Function):
        super().__init__(zero.arity + 1, max(zero.depth, recursive.depth + 1), zero, recursive)
        if zero.arity + 1 != recursive.arity - 1:
            raise ArityException(self, zero.arity + 1, recursive.arity - 1)

    def __call__(self, stack, *expression):
        super().__call__(*expression)
        if expression[0].closed:
            if expression[0].what:
                expression[0].what -= 1
                return Expression(self.children[1], False, stack, Expression(expression[0].what),
                                  Expression(self, False, stack, expression[0], *expression[1:]), *expression[1:])
            else:
                return Expression(self.children[0], False, stack, *expression[1:])
        stack.append(expression[0])
        return Expression(self, False, stack, *expression)

    @classmethod
    def build(cls, program):
        return cls(Interpreter.next_function(program), Interpreter.next_function(program))


def main():
    interpreter = Interpreter(Z=Zero, I=Identity, S=Successor, **{'<': Left, '>': Right}, o=Composition, R=Recursion)
    executable = interpreter.compile('oRZ>IRZRI<RS>>I')
    for i in range(40):
        step, result = executable.execute(i, display=range(0), bin_output=False)
        print(step, result)
    language = {Zero: 'Z', Identity: 'I', Successor: 'S', Left: '<', Right: '>', Composition: 'o', Recursion: 'R'}
    printer = Printer(language)
    print(printer.tree(executable))


if __name__ == '__main__':
    main()
