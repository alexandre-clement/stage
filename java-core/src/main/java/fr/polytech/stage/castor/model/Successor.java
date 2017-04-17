package fr.polytech.stage.castor.model;

import fr.polytech.stage.castor.interpreter.variables.NaturalNumber;
import fr.polytech.stage.castor.interpreter.variables.Vector;

import java.util.List;
import java.util.stream.Collectors;

/**
 * @author Alexandre Clement
 *         Created the 01/04/2017.
 */
public class Successor extends Operator implements RecursiveFunction
{
    public Successor()
    {
        super(OperatorType.SUCCESSOR);
    }

    @Override
    public Vector apply(Vector vector)
    {
        if (vector.size() != 1)
            throw new IllegalArgumentException("vector should have one natural number");
        Vector successors = new Vector(vector);
        successors.push(successors.pop().successor());
        return successors;
    }
}
