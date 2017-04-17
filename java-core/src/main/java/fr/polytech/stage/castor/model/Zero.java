package fr.polytech.stage.castor.model;

import fr.polytech.stage.castor.interpreter.variables.NaturalNumber;
import fr.polytech.stage.castor.interpreter.variables.Vector;

/**
 * @author Alexandre Clement
 *         Created the 01/04/2017.
 */
public class Zero extends Operator implements RecursiveFunction
{
    public Zero()
    {
        super(OperatorType.ZERO);
    }

    @Override
    public Vector apply(Vector vector)
    {
        if (!vector.isEmpty())
            throw new IllegalArgumentException("vector should be empty");
        return new Vector(new NaturalNumber());
    }
}
