from archive.tree_format import format_tree


class Language(dict):
    def parse(self, text):
        return (self[char] for char in text if char in self)


class Expression:
    def __init__(self, result=-1):
        self.closed = result != -1
        self.result = result

    def __call__(self, *args):
        return self.result

    def __str__(self):
        return str(self.result)


class Call(Expression):
    def __init__(self, expression, *params):
        super().__init__()
        self.expression = expression
        self.params = params

    def __call__(self, call_stack=None):
        if not self.closed:
            self.result = self.expression(*self.params)
            self.closed = self.expression.closed
        return self.result

    def __str__(self):
        return str(self.expression) + str(self.params)


class Function(Expression):
    def __init__(self, arity=0, depth=0, *children):
        super().__init__()
        self.arity = arity
        self.depth = depth
        self.children = children

    def __str__(self):
        return format_tree(self, format_node=lambda node: node.__class__.__name__,
                           get_children=lambda node: node.children)

    def __repr__(self):
        return f"{self.__class__.__name__}{''.join(map(repr, self.children))}"

    def copy(self):
        return self

    @staticmethod
    def build(program):
        try:
            return next(program).build(program)
        except StopIteration:
            raise InvalidProgram()


class ArityException(Exception):
    pass


class InvalidProgram(Exception):
    pass


class Zero(Function):
    def __init__(self):
        super().__init__()
        self.closed = True
        self.result = 0

    def call(self, calls_tack):
        return self.result

    def __copy__(self):
        return Zero()

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Zero()


class Identity(Function):
    def __init__(self):
        super().__init__(1)

    def __call__(self, call_stack, expression: Expression):
        if expression.closed:
            self.closed = True
            self.result = expression.result
        else:
            call_stack.append(Call(self, call_stack, expression))
            call_stack.append(Call(expression, call_stack))
        return self.result

    def copy(self):
        return Identity()

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Identity()


class Successor(Function):
    def __init__(self):
        super().__init__(1)

    def __call__(self, call_stack, expression: Expression):
        if expression.closed:
            self.closed = True
            self.result = expression.result + 1
        else:
            call_stack.append(Call(self, call_stack, expression))
            call_stack.append(Call(expression, call_stack))
        return self.result

    def copy(self):
        return Successor()

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Successor()


class Left(Function):
    def __init__(self, inner_function):
        super().__init__(inner_function.arity + 1, inner_function.depth, inner_function)
        self.inner_function = inner_function

    def __call__(self, call_stack, *expression):
        if self.inner_function.closed:
            self.closed = True
            self.result = self.inner_function.result
        else:
            call_stack.append(Call(self, call_stack, *expression))
            call_stack.append(Call(self.inner_function, call_stack, *expression[1:]))
        return self.result

    def copy(self):
        return Left(self.inner_function.copy())

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Left(building(program))


class Right(Function):
    def __init__(self, inner_function):
        super().__init__(inner_function.arity + 1, inner_function.depth, inner_function)
        self.inner_function = inner_function

    def __call__(self, call_stack, *expression):
        if self.inner_function.closed:
            self.closed = True
            self.result = self.inner_function.result
        else:
            call_stack.append(Call(self, call_stack, *expression))
            call_stack.append(Call(self.inner_function, call_stack, *expression[:-1]))
        return self.result

    def copy(self):
        return Right(self.inner_function.copy())

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Right(building(program))


class Composition(Function):
    def __init__(self, main_function: Function, *compound):
        super().__init__(compound[0].arity, max(f.arity for f in (main_function, *compound)), main_function, *compound)
        if main_function.arity != len(compound):
            raise ArityException()
        self.main_function = main_function
        self.compound = compound

    def __call__(self, call_stack, *expression):
        if len(expression) != self.arity:
            raise ArityException()
        if self.main_function.closed:
            self.closed = True
            self.result = self.main_function.result
        else:
            call_stack.append(Call(self, call_stack, *expression))
            call_stack.append(
                Call(self.main_function, call_stack, *[Call(comp, call_stack, *expression) for comp in self.compound]))
        return self.result

    def copy(self):
        return Composition(self.main_function.copy(), *(comp.copy() for comp in self.compound))

    @staticmethod
    def build(program, building=Function.build) -> Function:
        f = building(program)
        g = [building(program) for _ in range(f.arity)]
        return Composition(f, *g)


class Recursion(Function):
    def __init__(self, zero, recursive):
        super().__init__(zero.arity + 1, max(zero.depth, recursive.depth + 1), zero, recursive)
        self.zero = zero
        self.recursive = recursive

    def __call__(self, call_stack, counter, *params):
        if counter.closed:
            if counter.result:
                if self.recursive.closed:
                    self.closed = True
                    self.result = self.recursive.result
                else:
                    call_stack.append(Call(self, call_stack, counter, *params))
                    counter = Expression(counter.result - 1)
                    call_stack.append(
                        Call(self.recursive, call_stack, counter,
                             Call(self.copy(), call_stack, counter, *params),
                             *params))
            else:
                if self.zero.closed:
                    self.closed = True
                    self.result = self.zero.result
                else:
                    call_stack.append(Call(self, call_stack, counter, *params))
                    call_stack.append(Call(self.zero, call_stack, *params))
        else:
            call_stack.append(Call(self, call_stack, counter, *params))
            call_stack.append(Call(counter))
        return self.result

    def copy(self):
        return Recursion(self.zero.copy(), self.recursive.copy())

    @staticmethod
    def build(program, building=Function.build) -> Function:
        return Recursion(building(program), building(program))


def create_language():
    language = Language()
    language['Z'] = Zero
    language['I'] = Identity
    language['S'] = Successor
    language['<'] = Left
    language['>'] = Right
    language['o'] = Composition
    language['R'] = Recursion
    return language


def build(language, text):
    generator = language.parse(text)
    program = Function.build(generator)
    try:
        next(generator)
    except StopIteration:
        return program
    raise InvalidProgram()


def main():
    program = build(create_language(), 'oR<Z<RI<>SII')
    call_stack = list()
    param = (Expression(20),)
    program(call_stack, *param)
    i = 0
    while len(call_stack):
        i += 1
        call = call_stack.pop()
        call()
    print(i)
    print(program.result)


if __name__ == '__main__':
    main()
