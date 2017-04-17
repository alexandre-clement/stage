package fr.polytech.stage.castor.interpreter.variables;

import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;

/**
 * @author Alexandre Clement
 *         Created the 01/04/2017.
 */
public class Vector extends LinkedList<NaturalNumber>
{
    public Vector()
    {
        super();
    }

    public Vector(int... ints)
    {
        for (int anInt : ints)
        {
            add(new NaturalNumber(anInt));
        }
    }

    public Vector(NaturalNumber... naturalNumbers)
    {
        super(Arrays.asList(naturalNumbers));
    }

    public Vector(List<Vector> vectors)
    {
        for (Vector vector : vectors)
        {
            addAll(vector);
        }
    }

    public Vector(Vector vector)
    {
        super(vector);
    }

    public Vector(NaturalNumber peek, Vector apply)
    {
        super(apply);
        push(peek);
    }

    public Vector(NaturalNumber peek, Vector apply, Vector left)
    {
        this(peek, apply);
        addAll(left);
    }

    public static Vector valueOf(String[] args)
    {
        Vector vector = new Vector();
        for (String arg : args)
        {
            vector.add(new NaturalNumber(arg));
        }
        return vector;
    }

    public Vector left()
    {
        Vector left = new Vector(this);
        left.removeFirst();
        return left;
    }

    public Vector right()
    {
        Vector right = new Vector(this);
        right.removeLast();
        return right;
    }
}
