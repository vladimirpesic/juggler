/*
 * C# Language Test File
 * Tests all structural elements supported by the C# parser
 */

using System;
using System.Collections.Generic;
using System.Linq;

// Namespace declaration
namespace TestApplication
{
    // Enum definition
    public enum Status
    {
        Success = 0,
        Error = 1,
        Pending = 2
    }

    // Flags enum
    [Flags]
    public enum FilePermissions
    {
        None = 0,
        Read = 1,
        Write = 2,
        Execute = 4,
        All = Read | Write | Execute
    }

    // Interface definition
    public interface IShape
    {
        double Area { get; }
        double Perimeter { get; }
        void Display();
        string GetShapeInfo();
    }

    // Generic interface
    public interface IContainer<T>
    {
        void Add(T item);
        T Get(int index);
        int Count { get; }
    }

    // Struct definition
    public struct Point
    {
        public int X { get; set; }
        public int Y { get; set; }

        public Point(int x, int y)
        {
            X = x;
            Y = y;
        }

        public double DistanceFromOrigin()
        {
            return Math.Sqrt(X * X + Y * Y);
        }

        // Operator overloading in struct
        public static Point operator +(Point p1, Point p2)
        {
            return new Point(p1.X + p2.X, p1.Y + p2.Y);
        }
    }

    // Abstract class
    public abstract class Shape : IShape
    {
        protected string name;
        
        public Shape(string name)
        {
            this.name = name;
        }

        // Abstract property
        public abstract double Area { get; }
        
        // Abstract method
        public abstract double Perimeter { get; }
        
        // Virtual method
        public virtual void Display()
        {
            Console.WriteLine($"Shape: {name}");
        }

        // Concrete method
        public string GetShapeInfo()
        {
            return $"{name} - Area: {Area:F2}, Perimeter: {Perimeter:F2}";
        }

        // Static method
        public static void PrintShapeCount(int count)
        {
            Console.WriteLine($"Total shapes: {count}");
        }
    }

    // Derived class
    public class Rectangle : Shape
    {
        private double width;
        private double height;

        public Rectangle(double width, double height) : base("Rectangle")
        {
            this.width = width;
            this.height = height;
        }

        // Property with getter and setter
        public double Width
        {
            get { return width; }
            set { width = value > 0 ? value : throw new ArgumentException("Width must be positive"); }
        }

        public double Height
        {
            get { return height; }
            set { height = value > 0 ? value : throw new ArgumentException("Height must be positive"); }
        }

        // Override abstract properties
        public override double Area => width * height;
        public override double Perimeter => 2 * (width + height);

        // Override virtual method
        public override void Display()
        {
            base.Display();
            Console.WriteLine($"Dimensions: {width} x {height}");
        }

        // Method with optional parameters
        public void Resize(double widthFactor = 1.0, double heightFactor = 1.0)
        {
            width *= widthFactor;
            height *= heightFactor;
        }
    }

    // Sealed class
    public sealed class Circle : Shape
    {
        private double radius;

        public Circle(double radius) : base("Circle")
        {
            this.radius = radius;
        }

        public double Radius
        {
            get { return radius; }
            set { radius = value > 0 ? value : throw new ArgumentException("Radius must be positive"); }
        }

        public override double Area => Math.PI * radius * radius;
        public override double Perimeter => 2 * Math.PI * radius;
    }

    // Generic class
    public class Container<T> : IContainer<T> where T : class
    {
        private List<T> items = new List<T>();

        public void Add(T item)
        {
            if (item != null)
                items.Add(item);
        }

        public T Get(int index)
        {
            if (index >= 0 && index < items.Count)
                return items[index];
            throw new IndexOutOfRangeException("Index is out of range");
        }

        public int Count => items.Count;

        // Generic method
        public U Transform<U>(T item, Func<T, U> transformer)
        {
            return transformer(item);
        }
    }

    // Static class
    public static class MathUtilities
    {
        public static double Pi => Math.PI;

        public static int Add(int a, int b)
        {
            return a + b;
        }

        public static double Add(double a, double b)
        {
            return a + b;
        }

        // Extension method
        public static double Square(this double value)
        {
            return value * value;
        }

        // Generic static method
        public static T Max<T>(T a, T b) where T : IComparable<T>
        {
            return a.CompareTo(b) >= 0 ? a : b;
        }
    }

    // Delegate definitions
    public delegate void EventHandler(string message);
    public delegate T GenericFunc<T, U>(U input);

    // Event handling class
    public class EventPublisher
    {
        // Event declaration
        public event EventHandler OnMessageReceived;

        // Generic event
        public event Action<string, DateTime> OnTimestampedMessage;

        public void PublishMessage(string message)
        {
            OnMessageReceived?.Invoke(message);
            OnTimestampedMessage?.Invoke(message, DateTime.Now);
        }

        // Method with lambda expression
        public void ProcessNumbers(IEnumerable<int> numbers)
        {
            var evenNumbers = numbers.Where(n => n % 2 == 0).ToList();
            var squares = numbers.Select(n => n * n).ToArray();
            
            Console.WriteLine($"Even numbers: {string.Join(", ", evenNumbers)}");
            Console.WriteLine($"Squares: {string.Join(", ", squares)}");
        }
    }

    // Partial class (first part)
    public partial class PartialClassExample
    {
        private string firstName;

        public string FirstName
        {
            get { return firstName; }
            set { firstName = value; }
        }

        partial void OnNameChanged();
    }

    // Partial class (second part)
    public partial class PartialClassExample
    {
        private string lastName;

        public string LastName
        {
            get { return lastName; }
            set 
            { 
                lastName = value;
                OnNameChanged();
            }
        }

        partial void OnNameChanged()
        {
            Console.WriteLine($"Name changed to: {FirstName} {LastName}");
        }

        public string FullName => $"{FirstName} {LastName}";
    }

    // Main program class
    public class Program
    {
        // Recursive method
        public static long Factorial(int n)
        {
            if (n <= 1) return 1;
            return n * Factorial(n - 1);
        }

        // Method with out parameter
        public static bool TryParsePoint(string input, out Point point)
        {
            point = new Point();
            var parts = input.Split(',');
            if (parts.Length == 2 && 
                int.TryParse(parts[0], out int x) && 
                int.TryParse(parts[1], out int y))
            {
                point = new Point(x, y);
                return true;
            }
            return false;
        }

        // Method with ref parameter
        public static void SwapValues(ref int a, ref int b)
        {
            int temp = a;
            a = b;
            b = temp;
        }

        // Async method
        public static async System.Threading.Tasks.Task<string> GetDataAsync()
        {
            await System.Threading.Tasks.Task.Delay(1000); // Simulate async work
            return "Async data retrieved";
        }

        // Main method
        public static void Main(string[] args)
        {
            // Using enum
            Status currentStatus = Status.Success;
            Console.WriteLine($"Current status: {currentStatus}");

            // Using struct
            Point p1 = new Point(3, 4);
            Point p2 = new Point(1, 2);
            Point sum = p1 + p2;
            Console.WriteLine($"Point sum: ({sum.X}, {sum.Y})");

            // Using classes and inheritance
            Rectangle rect = new Rectangle(5.0, 3.0);
            Circle circle = new Circle(2.5);
            
            rect.Display();
            Console.WriteLine(rect.GetShapeInfo());
            
            circle.Display();
            Console.WriteLine(circle.GetShapeInfo());

            // Using generic class
            Container<Rectangle> rectContainer = new Container<Rectangle>();
            rectContainer.Add(rect);
            Console.WriteLine($"Container count: {rectContainer.Count}");

            // Using static class
            Console.WriteLine($"Max of 10 and 20: {MathUtilities.Max(10, 20)}");
            Console.WriteLine($"Square of 5: {5.0.Square()}");

            // Using events and delegates
            EventPublisher publisher = new EventPublisher();
            publisher.OnMessageReceived += msg => Console.WriteLine($"Received: {msg}");
            publisher.OnTimestampedMessage += (msg, time) => 
                Console.WriteLine($"[{time:HH:mm:ss}] {msg}");
            
            publisher.PublishMessage("Hello World");

            // LINQ and lambda expressions
            int[] numbers = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
            publisher.ProcessNumbers(numbers);

            // Using partial class
            PartialClassExample person = new PartialClassExample();
            person.FirstName = "John";
            person.LastName = "Doe";
            Console.WriteLine($"Full name: {person.FullName}");

            // Factorial calculation
            Console.WriteLine($"Factorial of 5: {Factorial(5)}");

            // Out and ref parameters
            if (TryParsePoint("10,20", out Point parsedPoint))
            {
                Console.WriteLine($"Parsed point: ({parsedPoint.X}, {parsedPoint.Y})");
            }

            int x = 100, y = 200;
            SwapValues(ref x, ref y);
            Console.WriteLine($"Swapped values: x={x}, y={y}");

            // Async method call
            var task = GetDataAsync();
            Console.WriteLine("Waiting for async operation...");
            Console.WriteLine(task.Result);

            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();
        }
    }
}

// Additional namespace for extension methods
namespace TestApplication.Extensions
{
    public static class StringExtensions
    {
        public static string Reverse(this string input)
        {
            if (string.IsNullOrEmpty(input)) return input;
            
            char[] chars = input.ToCharArray();
            Array.Reverse(chars);
            return new string(chars);
        }

        public static bool IsPalindrome(this string input)
        {
            if (string.IsNullOrEmpty(input)) return false;
            
            string cleaned = input.ToLower().Replace(" ", "");
            return cleaned == cleaned.Reverse();
        }
    }
}
