from generation import *


def castor(cls, length):
    language = {Zero: 'Z', Identity: 'I', Successor: 'S', Left: '<', Right: '>', Composition: 'o', Recursion: 'R'}
    printer = Printer(language)
    for i in cls:
        maxi = -1
        result = []
        for program in ProgramGenerator(1, i):
            for j in range(length):
                if program.execute(j, bin_output=True)[1]:
                    if j > maxi:
                        maxi = j
                        result = [program]
                    elif j == maxi:
                        result.append(program)
                    break
        print("classe ", i, ":", maxi, f"\t[{', '.join(map(printer.print, result))}]")


def main():
    castor(range(20), 100)


if __name__ == '__main__':
    main()
