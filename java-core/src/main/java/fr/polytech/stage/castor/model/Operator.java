package fr.polytech.stage.castor.model;

/**
 * @author Alexandre Clement
 *         Created the 01/04/2017.
 */
public class Operator
{
    private final OperatorType operatorType;

    Operator(OperatorType operatorType)
    {
        this.operatorType = operatorType;
    }

    public OperatorType getOperatorType()
    {
        return operatorType;
    }
}
