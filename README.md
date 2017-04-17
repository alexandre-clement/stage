# stage
SI3 - Stage project on Busy Beavers

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
   
