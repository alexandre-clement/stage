import argparse

from java_builder import Java
from tree_format import format_tree

"""
    The ``abstract_syntax_tree`` module
    ====================================
 
    Use it to build the abstract syntax tree of a recursive language.
    
    Definition of the default recursive language :
    
        Z : f = 0
        I : f = x -> x
        S : f = x -> x + 1
        < : g = f -> x, y -> f(y)
        > : g = f -> x, y -> g(x)
        O : h = g -> f1, f2, ..., fn -> x -> g(f1(x), f2(x), ..., fn(x))
        R : h = f, g -> (0, x) -> f(x)
                     -> (n, x) -> g(n - 1, h(n, x), x)
        
 
    :Examples:
        
        the program RI<>S does the sum of the 2 number given in parameters
    
        you can execute it by using --program option followed by your program and the parameters
        > python abstract_syntax_tree.py --program RI<>S 10 5
        Parameters of the execution  :  10 5
        Result of the execution      :  15
        
        you can also create a file ("sum" for example) within your program, and then run it like this
        > python abstract_syntax_tree.py -f sum 10 5
        Parameters of the execution  :  10 5
        Result of the execution      :  15
        
        you can print the tree structure of the program with --tree option
        > abstract_syntax_tree.py -f sum --tree
        R
        ├── I
        └── <
            └── >
                └── S
                
        you can do both by calling --tree option and giving program parameters
        > abstract_syntax_tree.py -f program/add.rl --tree 10 5
        R
        ├── I
        └── <
            └── >
                └── S
        Parameters of the execution  :  10 5
        Result of the execution      :  15
        
        you can create a java version of the program with the --java option
        > abstract_syntax_tree.py -program RI<>S --java
        
        and force execution on the java version
        > abstract_syntax_tree.py -program RI<>S --java 10 5
        Parameters of the execution  :  10 5
        Result of the execution      :  15
        
        
"""


class Function(object):
    """ The function superclass """
    arity = 0
    depth = 0
    name = ""
    java_class = ""
    children = []

    def __init__(self, program):
        pass

    def __str__(self):
        return self.name

    __repr__ = __str__

    def to_java(self):
        return f"new {self.java_class}({', '.join(child.to_java() for child in self.children)})"


class Language(dict):
    """ The language which contains all the functions defined """

    def __init__(self):
        super(Language, self).__init__()

    def add_function(self, function_name):
        def metaclass(name, bases, attributes):
            attributes["name"] = function_name
            attributes["java_class"] = name
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


class Composition(metaclass=language.add_function('O')):
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
        self.node = next_function(program)
        residue = tuple(program)
        if len(residue) != 0:
            raise NotEmptyProgramError(residue)


class NotEmptyProgramError(Exception):
    """ All the function in the program should be consumed after the tree construction """

    def __init__(self, program):
        self.program = program

    def __str__(self):
        return 'Program should be empty : {program}'.format(program=str(self.program))


class Commandline(argparse.ArgumentParser):
    """ Commandline parser """

    def __init__(self):
        super(Commandline, self).__init__(description="Build tree from a recursive language program")
        program_handler = self.add_mutually_exclusive_group(required=True)
        program_handler.add_argument("-f", "--filename", nargs=1, type=str,
                                     help="The filename of the program", metavar="filename", dest="filename")
        program_handler.add_argument("-p", "--program", nargs=1, type=str,
                                     help="The content of the program", metavar="program", dest="program")
        self.add_argument("params", type=int, metavar="vector", nargs="*", help="Parameters of the program")
        output = self.add_mutually_exclusive_group()
        output.add_argument("--java", action="store_true", help="Create a java version of the program to execute it")
        self.add_argument('--tree', action='store_true', help='Print a representation of the program tree')


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
    return (language[char] for char in text if char in language)


def main():
    commandline = Commandline().parse_args()
    if commandline.filename:
        program = parse(open(commandline.filename[0]).read())
    else:
        program = parse(commandline.program[0])
    tree = Tree(program)
    if commandline.tree:
        print(format_tree(tree.node, format_node=lambda node: str(node), get_children=lambda node: node.children))
    execution = tree.node
    if commandline.java:
        execution = Java(tree.node)
    if commandline.params:
        result = execution(*commandline.params)
        print("Parameters of the execution  : ", *commandline.params)
        print("Result of the execution      : ", *result)


if __name__ == '__main__':
    main()
