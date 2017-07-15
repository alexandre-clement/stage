
from archive.tree_format import format_tree


class Function(object):
    """ The function superclass """
    arity = 0
    depth = 0
    name = ""
    children = []

    def __init__(self, program):
        pass

    def __str__(self):
        return f"{self.name}"

    __repr__ = __str__


class Language(dict):
    """ The language which contains all the functions defined """

    def __init__(self):
        super(Language, self).__init__()

    def add_function(self, function_name):
        def metaclass(name, bases, attributes):
            attributes["name"] = function_name
            self[function_name] = type(name, (Function,) + bases, attributes)
            return self[function_name]
        return metaclass

# Creation of an instance of the language
language = Language()


class Zero(metaclass=language.add_function('Z')):
    """ The function Zero Z : f = 0 """

    def __call__(self):
        return 0,


class Identity(metaclass=language.add_function('I')):
    """ The function Identity I : f = x -> x """

    def __init__(self, program):
        self.arity = 1

    def __call__(self, x):
        return x,


class Successor(metaclass=language.add_function('S')):
    """ The function Successor S : f = x -> x + 1 """

    def __init__(self, program):
        self.arity = 1

    def __call__(self, x):
        return x + 1,


class Left(metaclass=language.add_function('<')):
    """ The function Left < : f = g -> x -> g(x[1:]) """

    def __init__(self, program):
        self.ast = next_function(program)
        self.children = [self.ast]
        self.arity = self.ast.arity + 1
        self.depth = self.ast.depth

    def __call__(self, *x):
        return self.ast(*x[1:])


class Right(metaclass=language.add_function('>')):
    """ The function Right > : f = g -> x -> g(x[:-1]) """

    def __init__(self, program):
        self.ast = next_function(program)
        self.children = [self.ast]
        self.arity = self.ast.arity + 1
        self.depth = self.ast.depth

    def __call__(self, *x):
        return self.ast(*x[:-1])


class Composition(metaclass=language.add_function('o')):
    """ The function Composition O : f = g -> h1, h2, ..., hn -> x -> g(h1(x), h2(x), ..., hn(x))"""

    def __init__(self, program):
        self.main_function = next_function(program)
        self.compound_function = list(next_function(program) for i in range(self.main_function.arity))
        self.children = [self.main_function] + self.compound_function
        self.arity = self.compound_function[0].arity
        self.depth = max(child.depth for child in self.children)

    def __call__(self, *x):
        return self.main_function(*[value for comp in self.compound_function for value in comp(*list(x))])


class Recursion(metaclass=language.add_function('R')):
    """ The function Recursion R : f = g, h -> (0, x) -> g(x)
                                            -> (n, x) -> h(n - 1, f(n, x), x) """

    def __init__(self, program):
        self.zero = next_function(program)
        self.recursion = next_function(program)
        self.children = [self.zero, self.recursion]
        self.arity = self.zero.arity + 1
        self.depth = max(int(child.depth) for child in self.children) + 1

    def __call__(self, n, *x):
        vector = self.zero(*list(x))
        for i in range(n):
            vector = self.recursion(i, *vector, *x)
        return vector

    def __recursive__call__(self, n, *x):
        if n == 0:
            return self.zero(*x)
        return self.recursion(n-1, *self(n-1, *tuple(x)), *tuple(x))


class Tree(object):
    """ Build the tree structure of the program """

    def __init__(self, program):
        self.program = iter(program)
        self.node = next_function(self.program)
        residue = tuple(self.program)
        if len(residue) != 0:
            raise NotEmptyProgramError(residue)


class NotEmptyProgramError(Exception):
    """ All the function in the program should be consumed after the tree construction """

    def __init__(self, program):
        self.program = program

    def __str__(self):
        return f'Program should be empty : {self.program}'


def next_function(program):
    """
    Consume a token of the program to create the associated Function instance
    The function instance needs the program in constructor to build its children
    :param program: the current program generator of Function
    :return: the next function instance of the tree
    """
    return next(program)(program)


def parse(text):
    """
    Transform a text into a generator of Function
    :param text: string version of the program
    :return: a generator with the Functions representations of the text program
    """
    return list(language[char] for char in text if char in language)


def display_tree(tree):
    return format_tree(tree.node, format_node=lambda node: str(node), get_children=lambda node: node.children)


def display_result(tree, *args):
    return f"f({', '.join(map(str, args))})={','.join(map(str, tree.node(*args)))}"


if __name__ == '__main__':
    for i in range(100):
        print(Tree(parse("oRI<R<Z<RS>>RZ>ISI")).node(i))