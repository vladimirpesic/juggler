// Comprehensive Scala test file with all structural elements
// Contains: classes, objects, traits, case classes, enums, functions, type aliases

import scala.collection.mutable
import scala.util.{Try, Success, Failure}

// Package declaration
package testpackage {

  // Enum (Scala 3 style)
  enum Color(val hexValue: String):
    case Red extends Color("#FF0000")
    case Green extends Color("#00FF00")
    case Blue extends Color("#0000FF")

  // Type aliases
  type Point2D = (Double, Double)
  type ShapeId = Long
  type Area = Double

  // Trait (interface-like)
  trait Drawable {
    def draw(): Unit
    def getArea(): Area
  }

  // Trait with implementation
  trait Loggable {
    private val logs = mutable.ListBuffer[String]()
    
    def log(message: String): Unit = {
      logs += s"${java.time.LocalDateTime.now()}: $message"
    }
    
    def getLogs: List[String] = logs.toList
  }

  // Abstract class
  abstract class Shape(val name: String, val color: Color) extends Drawable with Loggable {
    protected val id: ShapeId = Shape.nextId()
    
    log(s"Shape $name created with color ${color.hexValue}")
    
    def describe: String = s"$name shape in ${color.hexValue} color"
    
    // Abstract method to be implemented by subclasses
    def getArea(): Area
    
    // Concrete method with default implementation
    def getId: ShapeId = id
  }

  // Companion object for Shape
  object Shape {
    private var counter: ShapeId = 0L
    
    def nextId(): ShapeId = {
      counter += 1
      counter
    }
    
    def resetCounter(): Unit = {
      counter = 0L
    }
  }

  // Case class (immutable data class)
  case class Rectangle(
    override val name: String,
    override val color: Color,
    width: Double,
    height: Double
  ) extends Shape(name, color) {
    
    def draw(): Unit = {
      println(s"Drawing rectangle: $name (${width}x$height)")
    }
    
    def getArea(): Area = width * height
    
    def getPerimeter: Double = 2 * (width + height)
    
    // Method with pattern matching
    def classify: String = (width, height) match {
      case (w, h) if w == h => "Square"
      case (w, h) if w > h => "Landscape rectangle"
      case _ => "Portrait rectangle"
    }
  }

  // Another case class
  case class Circle(
    override val name: String,
    override val color: Color,
    radius: Double
  ) extends Shape(name, color) {
    
    def draw(): Unit = {
      println(s"Drawing circle: $name (radius: $radius)")
    }
    
    def getArea(): Area = math.Pi * radius * radius
    
    def getCircumference: Double = 2 * math.Pi * radius
  }

  // Class with generic type parameters
  class Container[T](private var content: T) {
    def get: T = content
    def set(newContent: T): Unit = content = newContent
    def transform[U](f: T => U): Container[U] = new Container(f(content))
    
    override def toString: String = s"Container($content)"
  }

  // Singleton object
  object MathUtils {
    def factorial(n: Int): Int = {
      if (n <= 1) 1
      else n * factorial(n - 1)
    }
    
    def fibonacci(n: Int): Int = {
      @scala.annotation.tailrec
      def fibHelper(n: Int, a: Int, b: Int): Int = {
        if (n == 0) a
        else fibHelper(n - 1, b, a + b)
      }
      fibHelper(n, 0, 1)
    }
    
    def isPrime(n: Int): Boolean = {
      if (n < 2) false
      else (2 to math.sqrt(n).toInt).forall(n % _ != 0)
    }
    
    def gcd(a: Int, b: Int): Int = {
      if (b == 0) a else gcd(b, a % b)
    }
  }

  // Class with companion object
  class Person(val name: String, val age: Int) {
    def isAdult: Boolean = age >= 18
    def introduce: String = s"Hi, I'm $name, $age years old"
    
    override def toString: String = s"Person($name, $age)"
  }

  object Person {
    def apply(name: String): Person = new Person(name, 0)
    def unapply(person: Person): Option[(String, Int)] = Some((person.name, person.age))
    
    val defaultAge = 0
  }

  // Sealed trait for ADT (Algebraic Data Type)
  sealed trait Result[+T]
  case class Success[T](value: T) extends Result[T]
  case class Error(message: String) extends Result[Nothing]
  case object Pending extends Result[Nothing]

  // Class with higher-order functions
  class FunctionUtils {
    def applyTwice[T](f: T => T, x: T): T = f(f(x))
    
    def compose[A, B, C](f: B => C, g: A => B): A => C = x => f(g(x))
    
    def curry[A, B, C](f: (A, B) => C): A => B => C = a => b => f(a, b)
    
    def uncurry[A, B, C](f: A => B => C): (A, B) => C = (a, b) => f(a)(b)
  }

  // Class with implicits
  class ImplicitExample {
    implicit class StringOps(s: String) {
      def toTitleCase: String = s.split(" ").map(_.capitalize).mkString(" ")
      def isPalindrome: Boolean = s == s.reverse
    }
    
    implicit def stringToInt(s: String): Int = s.toInt
    
    def processWithImplicit(x: Int)(implicit multiplier: Int): Int = x * multiplier
  }

  // Trait with self-type annotation
  trait DatabaseAccess {
    def connect(): Unit
    def disconnect(): Unit
  }

  trait Service {
    self: DatabaseAccess =>
    
    def performOperation(): Unit = {
      connect()
      println("Performing operation...")
      disconnect()
    }
  }

  // Class with multiple parameter lists
  class ParameterListExample {
    def calculate(x: Int, y: Int)(operation: (Int, Int) => Int)(implicit precision: Int): Double = {
      val result = operation(x, y)
      result.toDouble / math.pow(10, precision)
    }
  }

  // Generic trait with covariant type parameter
  trait Producer[+T] {
    def produce(): T
  }

  // Generic trait with contravariant type parameter
  trait Consumer[-T] {
    def consume(item: T): Unit
  }

  // Class implementing both traits
  class StringProcessor extends Producer[String] with Consumer[String] {
    private val buffer = mutable.ListBuffer[String]()
    
    def produce(): String = {
      if (buffer.nonEmpty) buffer.remove(0)
      else "empty"
    }
    
    def consume(item: String): Unit = {
      buffer += item.toUpperCase
    }
  }

}

// Main application object
object ScalaTestApp extends App {
  import testpackage._
  
  // Create shapes
  val rectangle = Rectangle("TestRect", Color.Blue, 10.0, 5.0)
  val circle = Circle("TestCircle", Color.Green, 3.0)
  
  // Test drawing
  rectangle.draw()
  circle.draw()
  
  println(s"Rectangle area: ${rectangle.getArea()}")
  println(s"Circle area: ${circle.getArea()}")
  println(s"Rectangle classification: ${rectangle.classify}")
  
  // Test utility functions
  println(s"Factorial of 5: ${MathUtils.factorial(5)}")
  println(s"10th Fibonacci number: ${MathUtils.fibonacci(10)}")
  println(s"Is 17 prime? ${MathUtils.isPrime(17)}")
  println(s"GCD of 48 and 18: ${MathUtils.gcd(48, 18)}")
  
  // Test container with generics
  val intContainer = new Container(42)
  val stringContainer = intContainer.transform(_.toString)
  println(s"Transformed container: $stringContainer")
  
  // Test person
  val person = Person("Alice", 25)
  println(person.introduce)
  println(s"Is adult? ${person.isAdult}")
  
  // Test pattern matching with case classes
  val shapes: List[Shape] = List(rectangle, circle)
  shapes.foreach { shape =>
    shape match {
      case Rectangle(name, color, w, h) => 
        println(s"Found rectangle $name: ${w}x$h")
      case Circle(name, color, r) => 
        println(s"Found circle $name with radius $r")
      case _ => 
        println("Unknown shape")
    }
  }
  
  // Test Result ADT
  val results: List[Result[Int]] = List(
    Success(42),
    Error("Something went wrong"),
    Pending
  )
  
  results.foreach {
    case Success(value) => println(s"Success: $value")
    case Error(msg) => println(s"Error: $msg")
    case Pending => println("Pending...")
  }
  
  // Test higher-order functions
  val funcUtils = new FunctionUtils()
  val double = (x: Int) => x * 2
  val addOne = (x: Int) => x + 1
  
  println(s"Apply twice: ${funcUtils.applyTwice(double, 5)}")
  
  val composed = funcUtils.compose(double, addOne)
  println(s"Composed function: ${composed(5)}")
  
  // Test implicit classes
  val implicitExample = new ImplicitExample()
  import implicitExample._
  
  println("hello world".toTitleCase)
  println("racecar".isPalindrome)
  
  // Test currying
  val curriedAdd = funcUtils.curry((x: Int, y: Int) => x + y)
  val addFive = curriedAdd(5)
  println(s"Curried addition: ${addFive(3)}")
  
  // Test collections with higher-order functions
  val numbers = List(1, 2, 3, 4, 5)
  val evenNumbers = numbers.filter(_ % 2 == 0)
  val squares = numbers.map(x => x * x)
  val sum = numbers.reduce(_ + _)
  
  println(s"Even numbers: $evenNumbers")
  println(s"Squares: $squares")
  println(s"Sum: $sum")
  
  // Test Option monad
  val maybeValue: Option[Int] = Some(42)
  val result = maybeValue
    .map(_ * 2)
    .filter(_ > 50)
    .getOrElse(0)
  
  println(s"Option result: $result")
  
  // Test for-comprehension
  val pairs = for {
    x <- 1 to 3
    y <- 1 to 3
    if x != y
  } yield (x, y)
  
  println(s"Pairs: $pairs")
  
  // Test String processor
  val processor = new StringProcessor()
  processor.consume("hello")
  processor.consume("world")
  
  println(s"Produced: ${processor.produce()}")
  println(s"Produced: ${processor.produce()}")
}

// Additional utility functions outside the package
def globalFunction(message: String): Unit = {
  println(s"Global function called: $message")
}

def arrayProcessor[T, U](data: List[T], f: T => U): List[U] = {
  data.map(f)
}

def typeConverter[T](data: String, converter: String => T): Option[T] = {
  Try(converter(data)).toOption
}
