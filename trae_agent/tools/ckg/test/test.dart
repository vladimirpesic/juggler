// Dart test file with all supported structural elements
import 'dart:io';
import 'dart:async';

// Module-level constants and variables
const String APP_NAME = 'TestApp';
var globalCounter = 0;

// Type alias
typedef StringProcessor = String Function(String);
typedef IntCallback = void Function(int);

// Enum
enum Color {
  red,
  green,
  blue;
  
  const Color();
  
  String get displayName {
    switch (this) {
      case Color.red:
        return 'Red Color';
      case Color.green:
        return 'Green Color';
      case Color.blue:
        return 'Blue Color';
    }
  }
}

// Enhanced enum with fields and methods
enum Priority {
  low(1),
  medium(5),
  high(10);
  
  const Priority(this.value);
  final int value;
  
  bool isHigherThan(Priority other) {
    return value > other.value;
  }
}

// Abstract class
abstract class Shape {
  double get area;
  double get perimeter;
  
  void describe() {
    print('This is a shape with area $area');
  }
}

// Interface (abstract class with only abstract methods)
abstract class Drawable {
  void draw();
  void erase();
}

// Mixin
mixin Colorable {
  Color? _color;
  
  Color? get color => _color;
  
  void setColor(Color color) {
    _color = color;
  }
  
  void printColor() {
    print('Color: ${_color?.displayName ?? 'No color'}');
  }
}

// Class implementing interface and using mixin
class Circle extends Shape with Colorable implements Drawable {
  double radius;
  
  Circle(this.radius);
  
  @override
  double get area => 3.14159 * radius * radius;
  
  @override
  double get perimeter => 2 * 3.14159 * radius;
  
  @override
  void draw() {
    print('Drawing a circle with radius $radius');
  }
  
  @override
  void erase() {
    print('Erasing circle');
  }
  
  // Static method
  static Circle createUnitCircle() {
    return Circle(1.0);
  }
  
  // Factory constructor
  factory Circle.fromDiameter(double diameter) {
    return Circle(diameter / 2);
  }
  
  // Named constructor
  Circle.withColor(this.radius, Color color) {
    setColor(color);
  }
}

// Class with generics
class Container<T> {
  T _value;
  
  Container(this._value);
  
  T get value => _value;
  
  void setValue(T newValue) {
    _value = newValue;
  }
  
  // Generic method
  R transform<R>(R Function(T) transformer) {
    return transformer(_value);
  }
}

// Extension on built-in type
extension StringExtensions on String {
  String capitalize() {
    if (isEmpty) return this;
    return '${this[0].toUpperCase()}${substring(1)}';
  }
  
  bool get isValidEmail {
    return RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(this);
  }
}

// Extension on custom type
extension CircleExtensions on Circle {
  double get diameter => radius * 2;
  
  void scale(double factor) {
    radius *= factor;
  }
}

// Global function
String formatMessage(String message, {String prefix = 'Info'}) {
  return '[$prefix] $message';
}

// Async function
Future<String> fetchData(String url) async {
  await Future.delayed(Duration(seconds: 1));
  return 'Data from $url';
}

// Generator function
Iterable<int> generateNumbers(int count) sync* {
  for (int i = 0; i < count; i++) {
    yield i;
  }
}

// Async generator function
Stream<String> generateMessages(int count) async* {
  for (int i = 0; i < count; i++) {
    await Future.delayed(Duration(milliseconds: 100));
    yield 'Message $i';
  }
}

// Function with callback
void processItems<T>(List<T> items, void Function(T) processor) {
  for (final item in items) {
    processor(item);
  }
}

// Class with complex inheritance
class Rectangle extends Shape {
  double width;
  double height;
  
  Rectangle(this.width, this.height);
  
  @override
  double get area => width * height;
  
  @override
  double get perimeter => 2 * (width + height);
  
  // Nested function
  double calculateDiagonal() {
    double square(double x) => x * x;
    return (square(width) + square(height)).sqrt();
  }
}

// Class with operator overloading
class Point {
  double x, y;
  
  Point(this.x, this.y);
  
  Point operator +(Point other) {
    return Point(x + other.x, y + other.y);
  }
  
  Point operator -(Point other) {
    return Point(x - other.x, y - other.y);
  }
  
  @override
  bool operator ==(Object other) {
    return other is Point && x == other.x && y == other.y;
  }
  
  @override
  int get hashCode => Object.hash(x, y);
  
  @override
  String toString() => 'Point($x, $y)';
}

// Main function
void main() async {
  print(formatMessage('Starting application'));
  
  // Test enum
  final color = Color.red;
  print('Selected color: ${color.displayName}');
  
  // Test priority enum
  final priority = Priority.high;
  print('Priority value: ${priority.value}');
  print('High > Medium: ${priority.isHigherThan(Priority.medium)}');
  
  // Test shapes
  final circle = Circle(5.0);
  circle.setColor(Color.blue);
  circle.draw();
  circle.printColor();
  print('Circle area: ${circle.area}');
  
  final coloredCircle = Circle.withColor(3.0, Color.green);
  coloredCircle.describe();
  
  // Test container
  final stringContainer = Container<String>('Hello');
  final length = stringContainer.transform<int>((s) => s.length);
  print('String length: $length');
  
  // Test extensions
  final text = 'hello world';
  print('Capitalized: ${text.capitalize()}');
  print('Is valid email: ${'test@example.com'.isValidEmail}');
  
  // Test circle extension
  print('Circle diameter: ${circle.diameter}');
  circle.scale(2.0);
  print('Scaled circle radius: ${circle.radius}');
  
  // Test async function
  final data = await fetchData('https://api.example.com');
  print('Fetched: $data');
  
  // Test generators
  final numbers = generateNumbers(5);
  print('Generated numbers: ${numbers.toList()}');
  
  await for (final message in generateMessages(3)) {
    print('Received: $message');
  }
  
  // Test function with callback
  processItems([1, 2, 3], (item) => print('Processing: $item'));
  
  // Test rectangle
  final rect = Rectangle(4.0, 3.0);
  print('Rectangle diagonal: ${rect.calculateDiagonal()}');
  
  // Test point operations
  final p1 = Point(1, 2);
  final p2 = Point(3, 4);
  final sum = p1 + p2;
  print('Point sum: $sum');
  
  print(formatMessage('Application finished'));
}
