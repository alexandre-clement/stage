from time import time


class ArityException(Exception):
    def __init__(self, expression, expected, value):
        self.expression = expression
        self.expected = expected
        self.value = value

    def __str__(self):
        return f"Arity Exception: expression '{self.expression}' expected {self.expected} but {self.value} given"


class InvalidProgram(Exception):
    pass


class Language:
    def __init__(self):
        self.functions = dict()
        self.grammar = dict()

    def __getitem__(self, item):
        if isinstance(item, str):
            if item not in self.functions:
                def metaclass(name, bases, attributes):
                    cls = type(name, bases, attributes)
                    self.functions[item] = cls
                    self.grammar[cls] = item
                    return cls
                return metaclass
            return self.functions[item]
        return self.grammar[item]

    def __contains__(self, item):
        return item in self.functions or item in self.grammar


language = Language()


class Expression:
    def __init__(self, what, *params):
        self.what = what
        self.closed = isinstance(what, int)
        self.params = params

    def __call__(self):
        if not self.closed:
            self.what(self, *self.params)

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
        return f"{self.print()}{''.join(map(str, self.children))}"

    __repr__ = __str__

    @classmethod
    def print(cls):
        return language[cls]

    def execute(self, *params, step=-1, display=(), bin_output=False):
        step_counter = 0
        stack = list()
        peek = Expression(self, stack, *[Expression(arg) for arg in params])
        stack.append(peek)
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
            return step_counter, peek.what
        return step_counter, peek.what

    @classmethod
    def build(cls, program):
        return cls()

    def __iter__(self):
        yield self
        for child in self.children:
            yield from child

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


class Zero(Function, metaclass=language['Z']):
    def __call__(self, master, stack, *expression):
        super().__call__(*expression)
        master.what = 0
        master.closed = True


class Identity(Function, metaclass=language['I']):
    def __init__(self):
        super().__init__(arity=1)

    def __call__(self, master, stack, *expression):
        super().__call__(*expression)
        if expression[0].closed:
            master.what = expression[0].what
            master.closed = True
        else:
            stack.append(expression[0])


class Successor(Function, metaclass=language['S']):
    def __init__(self):
        super().__init__(arity=1)

    def __call__(self, master, stack, *expression):
        super().__call__(*expression)
        if expression[0].closed:
            master.closed = True
            master.what = expression[0].what + 1
        else:
            stack.append(expression[0])


class Projection(Function):
    def __init__(self, children: Function):
        super().__init__(children.arity + 1, children.depth, children)

    @classmethod
    def build(cls, program):
        return cls(Interpreter.next_function(program))


class Left(Projection, metaclass=language['<']):
    def __call__(self, master, stack, *expression):
        super().__call__(*expression)
        master.what = self.children[0]
        master.params = (stack, *expression[1:])


class Right(Projection, metaclass=language['>']):
    def __call__(self, master, stack, *expression):
        super().__call__(*expression)
        master.what = self.children[0]
        master.params = (stack, *expression[:-1])


class Composition(Function, metaclass=language['o']):
    def __init__(self, *children: Function):
        super().__init__(children[1].arity, max([f.depth for f in children]), *children)
        if len(children) != children[0].arity + 1:
            raise ArityException(self, children[0].arity + 1, len(children))

    def __call__(self, master, stack, *expression):
        super().__call__(*expression)
        master.what = self.children[0]
        master.params = (stack, *[Expression(child, stack, *expression) for child in self.children[1:]])

    @classmethod
    def build(cls, program):
        main_child = next(program).build(program)
        return cls(main_child, *[Interpreter.next_function(program) for _ in range(main_child.arity)])


class Recursion(Function, metaclass=language['R']):
    def __init__(self, zero: Function, recursive: Function):
        super().__init__(zero.arity + 1, max(zero.depth, recursive.depth + 1), zero, recursive)
        if zero.arity + 1 != recursive.arity - 1:
            raise ArityException(self, zero.arity + 1, recursive.arity - 1)

    def __call__(self, master, stack, *expression):
        super().__call__(*expression)
        if expression[0].closed:
            if expression[0].what:
                ne = Expression(expression[0].what - 1)
                master.what = self.children[1]
                master.params = (stack, ne, Expression(self, stack, ne, *expression[1:]), *expression[1:])
            else:
                master.what = self.children[0]
                master.params = (stack, *expression[1:])
        else:
            stack.append(expression[0])

    @classmethod
    def build(cls, program):
        return cls(Interpreter.next_function(program), Interpreter.next_function(program))


class Interpreter:
    def __init__(self, functions=language):
        self.language = functions

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


def main():
    t0 = time()
    executable = Interpreter().compile("""
oRI<R<Z<RS>>RZ>ISI""")
    print(repr(executable))
    for i in range(100):
        for j in range(1):
            step, result = executable.execute(i, display=range(0), bin_output=False)
            print(i, j, step, result)
    # print(repr(executable))
    print(time() - t0)


if __name__ == '__main__':
    main()
