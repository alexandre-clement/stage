package fr.polytech.stage.castor.model;

import fr.polytech.stage.castor.interpreter.variables.Vector;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

/**
 * @author Alexandre Clement
 *         Created the 01/04/2017.
 */
public class CompositionTest
{
    @Test
    public void zeroIdentity() throws Exception
    {
        RecursiveFunction composition = new Composition(new Identity(), new Zero());
        assertEquals(new Vector(0), composition.apply(new Vector()));
    }

    @Test
    public void zeroSuccessor() throws Exception
    {
        RecursiveFunction composition = new Composition(new Successor(), new Zero());
        assertEquals(new Vector(1), composition.apply(new Vector()));
    }

    @Test
    public void add3Function() throws Exception
    {
        RecursiveFunction composition = new Composition(new Composition(new Successor(), new Successor()), new Successor());
        assertEquals(new Vector(3), composition.apply(new Vector(0)));
        assertEquals(new Vector(4), composition.apply(new Vector(1)));
    }

    @Test
    public void composition() throws Exception
    {
        RecursiveFunction add = new Recursion(new Right(new Zero()), new Left(new Left(new Successor())));
        RecursiveFunction composition = new Composition(add, new Left(new Successor()), new Right(new Identity()));
        assertEquals(new Vector(5), composition.apply(new Vector(4, 5)));
        assertEquals(new Vector(4), composition.apply(new Vector(3, 5)));
        assertEquals(new Vector(3), composition.apply(new Vector(2, 0)));
    }
}