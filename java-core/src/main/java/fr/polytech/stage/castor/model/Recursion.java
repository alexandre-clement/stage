package fr.polytech.stage.castor.model;

import fr.polytech.stage.castor.interpreter.variables.NaturalNumber;
import fr.polytech.stage.castor.interpreter.variables.Vector;

/**
 * @author Alexandre Clement
 *         Created the 01/04/2017.
 */
public class Recursion extends Operator implements RecursiveFunction
{
    private final RecursiveFunction zero;
    private final RecursiveFunction recursiveFunction;

    public Recursion(RecursiveFunction zero, RecursiveFunction recursiveFunction)
    {
        super(OperatorType.RECURSION);
        this.zero = zero;
        this.recursiveFunction = recursiveFunction;
    }

    @Override
    public Vector apply(Vector vector)
    {
        if (vector.isEmpty())
            throw new IllegalArgumentException("recursion requires at least one parameter");
        if (new NaturalNumber().equals(vector.peek()))
            return zero.apply(new Vector(vector).left());
        Vector recursion = new Vector(vector);
        recursion.push(recursion.pop().predecessor());
        return recursiveFunction.apply(new Vector(new NaturalNumber(recursion.peek()), apply(new Vector(recursion)), new Vector(recursion).left()));
    }
}
