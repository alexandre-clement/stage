from time import time

from generation import *


def castor(cls, length):
    t0 = time()
    printer = Printer()

    for i in cls:
        maxi = -1
        to_prove = []
        result = []
        for program in Main(1, i):
            program = Interpreter().compile(Printer().print(program))
            for j in range(length):
                try:
                    # print(printer.print(program))
                    if program.execute(j, bin_output=True)[1]:
                        if j > maxi:
                            maxi = j
                            result = [program]
                        elif j == maxi:
                            result.append(program)
                        break
                except Exception as e:
                    print(program)
                    print(e)
            else:
                to_prove.append(program)
        print("classe ", i, ":", maxi, [printer.print(p) for p in result])
        print(len(to_prove), [str(printer.print(p)) for p in to_prove])
        print(time() - t0)


def main():
    castor(range(20), 8)


if __name__ == '__main__':
    main()
