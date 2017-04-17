
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
        vector = new Recursion(new Identity(), new Left(new Right(new Successor()))).apply(vector);
        System.out.println(vector);
    }
}
