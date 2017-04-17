package fr.polytech.stage.castor.model;

import fr.polytech.stage.castor.interpreter.variables.Vector;

/**
 * @author Alexandre Clement
 *         Created the 01/04/2017.
 */
public class Right extends Operator implements RecursiveFunction
{
    private final RecursiveFunction recursiveFunction;

    public Right(RecursiveFunction recursiveFunction)
    {
        super(OperatorType.RIGHT);
        this.recursiveFunction = recursiveFunction;
    }

    @Override
    public Vector apply(Vector vector)
    {
        return recursiveFunction.apply(new Vector(vector).right());
    }
}
