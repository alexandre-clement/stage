import argparse

from abstract_syntax_tree import parse, Tree, display_tree, display_result
from generator import HashFunction, Generator, generate


class Commandline(argparse.ArgumentParser):
    """ Commandline parser """

    def __init__(self):
        super(Commandline, self).__init__(description="Build tree from a recursive language program")

        program_handler = self.add_mutually_exclusive_group(required=True)
        program_handler.add_argument("-f", "--filename", nargs=1, type=str, help="The filename of the program")
        program_handler.add_argument("-p", "--program", nargs=1, type=str, help="The content of the program")
        program_handler.add_argument("-c", "--create", nargs=1, type=int, help="Create the program from hashcode")
        program_handler.add_argument("-g", "--generate", nargs=2, type=str)

        execution = self.add_mutually_exclusive_group()
        execution.add_argument("-i", "--input", type=int, nargs="*", help="Parameters of the program")
        execution.add_argument("-r", '--range', nargs='+', type=int)

        self.add_argument('--tree', action='store_true', help='Print a representation of the program tree')
        self.add_argument("--hashcode", action='store_true', help='Print the hashcode of the program')


def main():
    commandline = Commandline().parse_args()

    if commandline.filename:
        program = parse(open(commandline.filename[0]).read())
    elif commandline.program:
        program = parse(commandline.program[0])
    elif commandline.create:
        program = Generator().create_program(1, commandline.create[0])
    else:
        program = generate(*map(eval, commandline.generate))

    tree = Tree(program)

    if commandline.tree:
        print(display_tree(tree))

    if commandline.hashcode:
        print(HashFunction().value(iter(program)))

    if commandline.input:
        print(display_result(tree, *commandline.input))

    if commandline.range:
        for i in range(*commandline.range):
            print(display_result(tree, i))


if __name__ == '__main__':
    main()
