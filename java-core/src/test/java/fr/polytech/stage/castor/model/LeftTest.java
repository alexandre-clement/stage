package fr.polytech.stage.castor.model;

import fr.polytech.stage.castor.interpreter.variables.Vector;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

/**
 * @author Alexandre Clement
 *         Created the 01/04/2017.
 */
public class LeftTest
{
    @Test
    public void apply() throws Exception
    {
        assertEquals(new Vector(0), new Left(new Zero()).apply(new Vector(0)));
        assertEquals(new Vector(1), new Left(new Successor()).apply(new Vector(1, 0)));
        assertEquals(new Vector(2), new Left(new Successor()).apply(new Vector(0, 1)));
    }

    @Test
    public void leftTwiceThenIdentity() throws Exception
    {
        RecursiveFunction leftTwiceThenIdentity = new Left(new Left(new Identity()));
        Vector vector = new Vector(0, 1, 2);
        Vector expected = new Vector(2);
        assertEquals(expected, leftTwiceThenIdentity.apply(vector));
    }

    @Test
    public void leftSuccessor() throws Exception
    {
        RecursiveFunction left = new Left(new Successor());
        Vector vector = new Vector(0, 1);
        Vector expected = new Vector(2);
        assertEquals(expected, left.apply(vector));
    }
}