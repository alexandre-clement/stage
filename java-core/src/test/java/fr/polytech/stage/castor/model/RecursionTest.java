package fr.polytech.stage.castor.model;

import org.junit.Test;

import java.util.function.Function;

import static fr.polytech.stage.castor.model.Utils.oneParameterFunction;
import static fr.polytech.stage.castor.model.Utils.twoParameterFunction;

/**
 * @author Alexandre Clement
 *         Created the 01/04/2017.
 */
public class RecursionTest
{
    @Test
    public void multiplyBy3() throws Exception
    {
        RecursiveFunction composition = new Composition(new Composition(new Successor(), new Successor()), new Successor());
        RecursiveFunction multiplyBy3 = new Recursion(new Zero(), new Left(composition));
        Function<Integer, Integer> expectedFunction = x -> 3 * x;
        oneParameterFunction(expectedFunction, multiplyBy3);
    }

    @Test
    public void sum() throws Exception
    {
        RecursiveFunction sum = new Recursion(new Zero(), new Recursion(new Successor(), new Left(new Right(new Successor()))));
        Function<Integer, Integer> expectedFunction = x -> x * (x + 1) / 2;
        oneParameterFunction(expectedFunction, sum);
    }

    @Test
    public void square() throws Exception
    {
        RecursiveFunction square = new Recursion(new Zero(), new Recursion(new Successor(), new Left(new Right(new Composition(new Successor(), new Successor())))));
        Function<Integer, Integer> expectedFunction = x -> x * x;
        oneParameterFunction(expectedFunction, square);
    }

    @Test
    public void ifElse() throws Exception
    {
        RecursiveFunction ifElse = new Composition(new Recursion(new Successor(), new Right(new Right(new Identity()))), new Left(new Identity()), new Right(new Successor()));
        Function<Integer, Function<Integer, Integer>> expectedFunction = x -> y -> y > 0 ? y - 1 : x + 2;
        twoParameterFunction(expectedFunction, ifElse);
    }

    @Test
    public void findXValue() throws Exception
    {
        RecursiveFunction addPlusOne = new Recursion(new Successor(), new Left(new Right(new Successor())));
        RecursiveFunction sum = new Recursion(new Zero(), addPlusOne);
        RecursiveFunction sumPlusOne = new Composition(sum, new Successor());
        RecursiveFunction predecessor = new Recursion(new Zero(), new Right(new Identity()));
        RecursiveFunction sous = new Recursion(new Identity(), new Right(new Left(predecessor)));
        RecursiveFunction sousRightSuccessorByLeftSumPlusOne = new Composition(sous, new Left(sumPlusOne), new Right(new Successor()));
        RecursiveFunction add = new Recursion(new Right(new Zero()), new Left(new Left(new Successor())));
        RecursiveFunction composition = new Composition(add, sousRightSuccessorByLeftSumPlusOne, new Left(new Identity()));
        RecursiveFunction findXValue = new Recursion(new Zero(), composition);

        Function<Integer, Integer> expectedFunction = x -> {
            int n = (int) Math.sqrt(2*x);
            if (n * (n + 1) / 2 > x)
                n -= 1;
            int p = n * (n+1) / 2;
            return x - p;
        };

        oneParameterFunction(expectedFunction, findXValue);
    }

    @Test
    public void composition() throws Exception
    {
        RecursiveFunction addPlusOne = new Recursion(new Successor(), new Left(new Right(new Successor())));
        RecursiveFunction sum = new Recursion(new Zero(), addPlusOne);
        RecursiveFunction sumPlusOne = new Composition(sum, new Successor());
        RecursiveFunction predecessor = new Recursion(new Zero(), new Right(new Identity()));
        RecursiveFunction sous = new Recursion(new Identity(), new Right(new Left(predecessor)));
        RecursiveFunction sousRightSuccessorByLeftSumPlusOne = new Composition(sous, new Left(sumPlusOne), new Right(new Successor()));
        RecursiveFunction addConditional = new Recursion(new Right(new Zero()), new Left(new Left(new Successor())));
        RecursiveFunction composition = new Composition(addConditional, sousRightSuccessorByLeftSumPlusOne, new Left(new Identity()));
        Function<Integer, Function<Integer, Integer>> sousRightSuccessorByLeftSumPlusOneFunction = x -> y -> Math.max(0, x + 1 - (y + 1) * (y + 2) / 2);
        Function<Integer, Function<Integer, Integer>> addConditionalFunction = x -> y -> x == 0 ? 0 : y + 1;
        Function<Integer, Function<Integer, Integer>> expectedFunction = x -> y ->
        {
            int right = sousRightSuccessorByLeftSumPlusOneFunction.apply(x).apply(y);
            return addConditionalFunction.apply(right).apply(y);
        };
        twoParameterFunction(expectedFunction, composition);
    }

    @Test
    public void addConditional() throws Exception
    {
        RecursiveFunction addConditional = new Recursion(new Right(new Zero()), new Left(new Left(new Successor())));
        Function<Integer, Function<Integer, Integer>> expectedFunction = x -> y -> x == 0 ? 0 : y + 1;
        twoParameterFunction(expectedFunction, addConditional);
    }

    @Test
    public void sousRightSuccessorByLeftSumPlusOne() throws Exception
    {
        RecursiveFunction addPlusOne = new Recursion(new Successor(), new Left(new Right(new Successor())));
        RecursiveFunction sum = new Recursion(new Zero(), addPlusOne);
        RecursiveFunction sumPlusOne = new Composition(sum, new Successor());
        RecursiveFunction predecessor = new Recursion(new Zero(), new Right(new Identity()));
        RecursiveFunction sous = new Recursion(new Identity(), new Right(new Left(predecessor)));
        RecursiveFunction sousRightSuccessorByLeftSumPlusOne = new Composition(sous, new Left(sumPlusOne), new Right(new Successor()));
        Function<Integer, Function<Integer, Integer>> expectedFunction = x -> y -> Math.max(0, x + 1 - (y + 1) * (y + 2) / 2);
        twoParameterFunction(expectedFunction, sousRightSuccessorByLeftSumPlusOne);
    }

    @Test
    public void sous() throws Exception
    {
        RecursiveFunction predecessor = new Recursion(new Zero(), new Right(new Identity()));
        RecursiveFunction sous = new Recursion(new Identity(), new Right(new Left(predecessor)));
        Function<Integer, Function<Integer, Integer>> expectedFunction = x -> y -> Math.max(0, y - x);
        twoParameterFunction(expectedFunction, sous);
    }

    @Test
    public void predecessor() throws Exception
    {
        RecursiveFunction predecessor = new Recursion(new Zero(), new Right(new Identity()));
        Function<Integer, Integer> expectedFunction = x -> x > 0 ? x - 1 : 0;
        oneParameterFunction(expectedFunction, predecessor);
    }

    @Test
    public void add() throws Exception
    {
        RecursiveFunction add = new Recursion(new Identity(), new Left(new Right(new Successor())));
        Function<Integer, Function<Integer, Integer>> expectedFunction = x -> y -> x + y;
        twoParameterFunction(expectedFunction, add);
    }

    @Test
    public void sumPlusOne() throws Exception
    {
        RecursiveFunction addPlusOne = new Recursion(new Successor(), new Left(new Right(new Successor())));
        RecursiveFunction sum = new Recursion(new Zero(), addPlusOne);
        RecursiveFunction sumPlusOne = new Composition(sum, new Successor());
        Function<Integer, Integer> expectedFunction = x -> (x+1) * (x+2) / 2;
        oneParameterFunction(expectedFunction, sumPlusOne);
    }

    @Test
    public void addPlusOne() throws Exception
    {
        RecursiveFunction addPlusOne = new Recursion(new Successor(), new Left(new Right(new Successor())));
        Function<Integer, Function<Integer, Integer>> expectedFunction = x -> y -> x + y + 1;
        twoParameterFunction(expectedFunction, addPlusOne);
    }

}