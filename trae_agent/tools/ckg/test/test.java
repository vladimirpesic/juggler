/**
 * Comprehensive Java test file containing all supported structural elements.
 * This file demonstrates classes, interfaces, enums, and functions.
 */

package com.example.test;

import java.util.*;
import java.util.function.*;

// Enum definition
public enum Color {
    RED("Red Color", 0xFF0000),
    GREEN("Green Color", 0x00FF00),
    BLUE("Blue Color", 0x0000FF);
    
    private final String description;
    private final int hexValue;
    
    Color(String description, int hexValue) {
        this.description = description;
        this.hexValue = hexValue;
    }
    
    public String getDescription() {
        return description;
    }
    
    public int getHexValue() {
        return hexValue;
    }
}

// Interface definition
interface Drawable {
    void draw();
    
    default void setColor(Color color) {
        System.out.println("Setting color to " + color.getDescription());
    }
    
    static void printDrawableInfo() {
        System.out.println("This is a drawable interface");
    }
}

// Functional interface
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);
}

// Generic interface
interface Container<T> {
    void add(T item);
    T get(int index);
    int size();
}

// Abstract class
abstract class Shape implements Drawable {
    protected String name;
    protected Color color;
    
    public Shape(String name) {
        this.name = name;
        this.color = Color.RED;
    }
    
    public abstract double getArea();
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getName() {
        return name;
    }
    
    @Override
    public void draw() {
        System.out.println("Drawing " + name + " in " + color.getDescription());
    }
}

// Concrete class extending abstract class
class Rectangle extends Shape {
    private double width;
    private double height;
    
    public Rectangle(String name, double width, double height) {
        super(name);
        this.width = width;
        this.height = height;
    }
    
    @Override
    public double getArea() {
        return width * height;
    }
    
    // Method overloading
    public void resize(double factor) {
        this.width *= factor;
        this.height *= factor;
    }
    
    public void resize(double newWidth, double newHeight) {
        this.width = newWidth;
        this.height = newHeight;
    }
    
    // Getter and setter methods
    public double getWidth() {
        return width;
    }
    
    public void setWidth(double width) {
        this.width = width;
    }
    
    public double getHeight() {
        return height;
    }
    
    public void setHeight(double height) {
        this.height = height;
    }
}

// Generic class
class GenericContainer<T> implements Container<T> {
    private List<T> items;
    
    public GenericContainer() {
        this.items = new ArrayList<>();
    }
    
    @Override
    public void add(T item) {
        items.add(item);
    }
    
    @Override
    public T get(int index) {
        return items.get(index);
    }
    
    @Override
    public int size() {
        return items.size();
    }
    
    // Generic method
    public <U> void processItems(Function<T, U> processor) {
        for (T item : items) {
            U result = processor.apply(item);
            System.out.println("Processed: " + result);
        }
    }
}

// Nested class example
class OuterClass {
    private String outerField = "Outer field";
    
    // Inner non-static class
    class InnerClass {
        private String innerField = "Inner field";
        
        public void displayFields() {
            System.out.println("Outer: " + outerField);
            System.out.println("Inner: " + innerField);
        }
    }
    
    // Static nested class
    static class StaticNestedClass {
        private String staticField = "Static nested field";
        
        public void display() {
            System.out.println("Static nested: " + staticField);
        }
    }
    
    // Method with local class
    public void methodWithLocalClass() {
        final String localVar = "Local variable";
        
        class LocalClass {
            public void display() {
                System.out.println("Local class accessing: " + localVar);
            }
        }
        
        LocalClass local = new LocalClass();
        local.display();
    }
}

// Class with multiple constructors
class Person {
    private String firstName;
    private String lastName;
    private int age;
    private String email;
    
    // Default constructor
    public Person() {
        this("Unknown", "Unknown", 0, "unknown@example.com");
    }
    
    // Constructor with name only
    public Person(String firstName, String lastName) {
        this(firstName, lastName, 0, "unknown@example.com");
    }
    
    // Constructor with name and age
    public Person(String firstName, String lastName, int age) {
        this(firstName, lastName, age, "unknown@example.com");
    }
    
    // Full constructor
    public Person(String firstName, String lastName, int age, String email) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.age = age;
        this.email = email;
    }
    
    // Static factory method
    public static Person createAdult(String firstName, String lastName) {
        return new Person(firstName, lastName, 18);
    }
    
    // Method with variable arguments
    public void addHobbies(String... hobbies) {
        System.out.println("Hobbies for " + firstName + ":");
        for (String hobby : hobbies) {
            System.out.println("- " + hobby);
        }
    }
    
    // Override toString
    @Override
    public String toString() {
        return String.format("Person{firstName='%s', lastName='%s', age=%d, email='%s'}", 
                           firstName, lastName, age, email);
    }
    
    // Override equals and hashCode
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        
        Person person = (Person) obj;
        return age == person.age &&
               Objects.equals(firstName, person.firstName) &&
               Objects.equals(lastName, person.lastName) &&
               Objects.equals(email, person.email);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(firstName, lastName, age, email);
    }
}

// Main class with static methods
public class TestJava {
    // Static variables
    public static final String APP_NAME = "Java Test Application";
    private static int instanceCount = 0;
    
    // Instance variables
    private String instanceId;
    
    // Constructor
    public TestJava() {
        instanceCount++;
        this.instanceId = "Instance_" + instanceCount;
    }
    
    // Static method
    public static void printAppInfo() {
        System.out.println("Application: " + APP_NAME);
        System.out.println("Instances created: " + instanceCount);
    }
    
    // Instance method
    public void printInstanceInfo() {
        System.out.println("Instance ID: " + instanceId);
    }
    
    // Method with exception handling
    public void demonstrateExceptions() {
        try {
            int result = divideByZero(10, 0);
        } catch (ArithmeticException e) {
            System.out.println("Caught exception: " + e.getMessage());
        } finally {
            System.out.println("Finally block executed");
        }
    }
    
    private int divideByZero(int a, int b) throws ArithmeticException {
        if (b == 0) {
            throw new ArithmeticException("Division by zero");
        }
        return a / b;
    }
    
    // Method demonstrating lambdas and streams
    public void demonstrateLambdas() {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
        
        // Lambda with stream operations
        List<Integer> evenSquares = numbers.stream()
            .filter(n -> n % 2 == 0)
            .map(n -> n * n)
            .collect(java.util.stream.Collectors.toList());
        
        System.out.println("Even squares: " + evenSquares);
        
        // Using functional interface
        Calculator add = (a, b) -> a + b;
        Calculator multiply = (a, b) -> a * b;
        
        System.out.println("Addition: " + add.calculate(5, 3));
        System.out.println("Multiplication: " + multiply.calculate(5, 3));
    }
    
    // Main method
    public static void main(String[] args) {
        System.out.println("=== Java Comprehensive Test ===");
        
        // Test static method
        printAppInfo();
        
        // Test instance creation
        TestJava test = new TestJava();
        test.printInstanceInfo();
        
        // Test enum
        Color color = Color.BLUE;
        System.out.println("Selected color: " + color.getDescription());
        
        // Test inheritance and polymorphism
        Shape rect = new Rectangle("Test Rectangle", 10.0, 5.0);
        rect.draw();
        System.out.println("Area: " + rect.getArea());
        
        // Test generic class
        GenericContainer<String> stringContainer = new GenericContainer<>();
        stringContainer.add("Hello");
        stringContainer.add("World");
        System.out.println("Container size: " + stringContainer.size());
        
        // Test nested classes
        OuterClass outer = new OuterClass();
        OuterClass.InnerClass inner = outer.new InnerClass();
        inner.displayFields();
        
        OuterClass.StaticNestedClass staticNested = new OuterClass.StaticNestedClass();
        staticNested.display();
        
        outer.methodWithLocalClass();
        
        // Test person class
        Person person = Person.createAdult("John", "Doe");
        person.addHobbies("Reading", "Gaming", "Cooking");
        System.out.println(person);
        
        // Test exception handling
        test.demonstrateExceptions();
        
        // Test lambdas
        test.demonstrateLambdas();
    }
}
