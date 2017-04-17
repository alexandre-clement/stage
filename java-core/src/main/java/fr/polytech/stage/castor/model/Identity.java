package fr.polytech.stage.castor.model;

import fr.polytech.stage.castor.interpreter.variables.Vector;

/**
 * @author Alexandre Clement
 *         Created the 01/04/2017.
 */
public class Identity extends Operator implements RecursiveFunction
{
    public Identity()
    {
        super(OperatorType.IDENTITY);
    }

    @Override
    public Vector apply(Vector vector)
    {
        if (vector.size() != 1)
            throw new IllegalArgumentException("vector should have one natural number");
        return new Vector(vector);
    }
}
