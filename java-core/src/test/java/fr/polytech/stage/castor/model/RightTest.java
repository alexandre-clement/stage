package fr.polytech.stage.castor.model;

import fr.polytech.stage.castor.interpreter.variables.Vector;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

/**
 * @author Alexandre Clement
 *         Created the 01/04/2017.
 */
public class RightTest
{
    @Test
    public void apply() throws Exception
    {
        assertEquals(new Vector(0), new Right(new Zero()).apply(new Vector(0)));
        assertEquals(new Vector(1), new Right(new Successor()).apply(new Vector(0, 1)));
        assertEquals(new Vector(2), new Right(new Successor()).apply(new Vector(1, 0)));
    }

    @Test
    public void leftRightLeft() throws Exception
    {
        assertEquals(new Vector(2), new Left(new Right(new Left(new Identity()))).apply(new Vector(0, 1, 2, 3)));
        assertEquals(new Vector(2), new Right(new Left(new Left(new Identity()))).apply(new Vector(0, 1, 2, 3)));
        assertEquals(new Vector(2), new Left(new Left(new Right(new Identity()))).apply(new Vector(0, 1, 2, 3)));
    }
}