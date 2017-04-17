package fr.polytech.stage.castor.model;

import fr.polytech.stage.castor.interpreter.variables.Vector;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

/**
 * @author Alexandre Clement
 *         Created the 01/04/2017.
 */
public class ZeroTest
{
    @Test
    public void apply() throws Exception
    {
        assertEquals(new Vector(0), new Zero().apply(new Vector()));
    }
}