package fr.polytech.stage.castor.model;

import fr.polytech.stage.castor.interpreter.variables.Vector;

import java.util.function.Function;

import static org.junit.Assert.assertEquals;

/**
 * @author Alexandre Clement
 *         Created the 02/04/2017.
 */
class Utils
{
    static void oneParameterFunction(Function<Integer, Integer> expectedFunction, RecursiveFunction recursiveFunction) throws Exception
    {
        Vector vector;
        Vector expected;

        for (int i = 0; i < 30; i++)
        {
            vector = new Vector(i);
            expected = new Vector(expectedFunction.apply(i));
            assertEquals(expected, recursiveFunction.apply(vector));
        }
    }

    static void twoParameterFunction(Function<Integer, Function<Integer, Integer>> expectedFunction, RecursiveFunction recursiveFunction) throws Exception
    {
        Vector vector;
        Vector expected;

        for (int i = 0; i < 30; i++)
        {
            for (int j = 0; j < 30; j++)
            {
                vector = new Vector(i, j);
                expected = new Vector(expectedFunction.apply(i).apply(j));
                try
                {
                    assertEquals(expected, recursiveFunction.apply(vector));
                }
                catch (AssertionError assertionError)
                {
                    throw new AssertionError(assertionError.getMessage() + String.format("x = %d; y = %d", i, j));
                }
            }
        }
    }
}
