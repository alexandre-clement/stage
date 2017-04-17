import os
import subprocess

JAVA_MAIN = """
package fr.polytech.stage.castor;

import fr.polytech.stage.castor.interpreter.variables.Vector;
import fr.polytech.stage.castor.model.*;

/**
 * @author Alexandre Clement
 *         Created the 30/03/2017.
 */
public class Main
{
    private Main()
    {
    }

    public static void main(String[] args)
    {
        Vector vector = Vector.valueOf(args);
        %s
        System.out.println(vector);
    }
}
"""


class ChangeDir:

    def __init__(self, new_path):
        self.newPath = os.path.expanduser(new_path)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)
        return self

    def __exit__(self, e_type, value, traceback):
        os.chdir(self.savedPath)


class Java(object):

    def __init__(self, root):
        with open(r"java-core\src\main\java\fr\polytech\stage\castor\Main.java", "w") as main:
            main.write(JAVA_MAIN % f"vector = {root.to_java()}.apply(vector);")
        with ChangeDir("java-core") as root_path, open("maven_log", "w") as mvn_log:
            subprocess.call(["mvn", "-q", "clean", "install", ], shell=True, stdout=mvn_log)

    def __call__(self, *x):
        return Java.execute(*x)

    @staticmethod
    def execute(*x):
        with ChangeDir("java-core") as root_path, open("output_temp", "w") as stdout:
            subprocess.call(f'mvn exec:java -q -Dexec.args="{" ".join(str(y) for y in x)}"', shell=True, stdout=stdout)
            return eval(open("output_temp").read())
