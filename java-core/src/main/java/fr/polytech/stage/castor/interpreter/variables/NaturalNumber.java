package fr.polytech.stage.castor.interpreter.variables;

/**
 * @author Alexandre Clement
 *         Created the 30/03/2017.
 */
public class NaturalNumber
{
    private int value;

    public NaturalNumber()
    {
        value = 0;
    }

    public NaturalNumber(int value)
    {
        if (value < 0)
            throw new ArithmeticException("negative value");
        this.value = value;
    }

    public NaturalNumber(String value)
    {
        this(Integer.parseInt(value));
    }

    public NaturalNumber(NaturalNumber naturalNumber)
    {
        value = naturalNumber.value;
    }

    public NaturalNumber successor()
    {
        if (value == Integer.MAX_VALUE)
            throw new ArithmeticException("integer overflow");
        return new NaturalNumber(value + 1);
    }

    public NaturalNumber predecessor()
    {
        if (value == 0)
            throw new ArithmeticException("negative value");
        return new NaturalNumber(value - 1);
    }

    @Override
    public String toString()
    {
        return Integer.toString(value);
    }

    @Override
    public boolean equals(Object object)
    {
        return object != null && getClass() == object.getClass() && value == ((NaturalNumber) object).value;
    }

    @Override
    public int hashCode()
    {
        return value;
    }
}
