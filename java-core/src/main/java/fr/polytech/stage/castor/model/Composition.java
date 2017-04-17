package fr.polytech.stage.castor.model;

import fr.polytech.stage.castor.interpreter.variables.Vector;

/**
 * @author Alexandre Clement
 *         Created the 01/04/2017.
 */
public class Composition extends Operator implements RecursiveFunction
{
    private final RecursiveFunction compound;
    private final RecursiveFunction[] recursiveFunctions;

    public Composition(RecursiveFunction compound, RecursiveFunction... recursiveFunctions)
    {
        super(OperatorType.COMPOSITION);
        this.compound = compound;
        this.recursiveFunctions = recursiveFunctions;
    }

    @Override
    public Vector apply(Vector vector)
    {
        Vector map = new Vector();
        for (RecursiveFunction recursiveFunction : recursiveFunctions)
        {
            map.addAll(recursiveFunction.apply(new Vector(vector)));
        }
        return compound.apply(new Vector(map));
    }
}
