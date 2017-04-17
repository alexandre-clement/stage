package fr.polytech.stage.castor.model;

import fr.polytech.stage.castor.interpreter.variables.Vector;

/**
 * @author Alexandre Clement
 *         Created the 01/04/2017.
 */
@FunctionalInterface
public interface RecursiveFunction
{
    /**
     * Applies this function to the given argument.
     *
     * @param vector the function argument
     * @return the function result
     */
    Vector apply(Vector vector);
}
