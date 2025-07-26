// Gleam test file with all supported structural elements
import gleam/io
import gleam/list
import gleam/result
import gleam/string
import gleam/int
import gleam/bool

// Type aliases
pub type UserId = Int
pub type UserName = String
pub type Result(a, e) = result.Result(a, e)

// Custom types (like enums/algebraic data types)
pub type Color {
  Red
  Green
  Blue
  Custom(red: Int, green: Int, blue: Int)
}

pub type Shape {
  Circle(radius: Float)
  Rectangle(width: Float, height: Float)
  Triangle(base: Float, height: Float)
}

pub type Maybe(a) {
  Some(a)
  None
}

pub type HttpStatus {
  Ok
  NotFound
  BadRequest(String)
  InternalError(String)
}

// Record types (structs)
pub type User {
  User(id: UserId, name: UserName, email: String, age: Int)
}

pub type Point {
  Point(x: Float, y: Float)
}

pub type Config {
  Config(
    host: String,
    port: Int,
    timeout: Int,
    retries: Int,
    debug: Bool,
  )
}

// Functions with pattern matching
pub fn color_to_string(color: Color) -> String {
  case color {
    Red -> "red"
    Green -> "green"
    Blue -> "blue"
    Custom(r, g, b) -> "rgb(" <> int.to_string(r) <> "," <> int.to_string(g) <> "," <> int.to_string(b) <> ")"
  }
}

pub fn shape_area(shape: Shape) -> Float {
  case shape {
    Circle(radius) -> 3.14159 *. radius *. radius
    Rectangle(width, height) -> width *. height
    Triangle(base, height) -> 0.5 *. base *. height
  }
}

pub fn maybe_map(maybe: Maybe(a), func: fn(a) -> b) -> Maybe(b) {
  case maybe {
    Some(value) -> Some(func(value))
    None -> None
  }
}

// Function with guards and multiple clauses
pub fn categorize_age(age: Int) -> String {
  case age {
    age if age < 0 -> "invalid"
    age if age < 13 -> "child"
    age if age < 20 -> "teenager"
    age if age < 65 -> "adult"
    _ -> "senior"
  }
}

// Higher-order functions
pub fn apply_twice(func: fn(a) -> a, value: a) -> a {
  func(func(value))
}

pub fn compose(f: fn(b) -> c, g: fn(a) -> b) -> fn(a) -> c {
  fn(x) { f(g(x)) }
}

// List processing functions
pub fn filter_map(items: List(a), predicate: fn(a) -> Bool, transform: fn(a) -> b) -> List(b) {
  items
  |> list.filter(predicate)
  |> list.map(transform)
}

pub fn sum_list(numbers: List(Int)) -> Int {
  list.fold(numbers, 0, int.add)
}

// Recursive functions
pub fn factorial(n: Int) -> Int {
  case n {
    0 -> 1
    1 -> 1
    n if n > 1 -> n * factorial(n - 1)
    _ -> 0  // Invalid input
  }
}

pub fn fibonacci(n: Int) -> Int {
  case n {
    0 -> 0
    1 -> 1
    n if n > 1 -> fibonacci(n - 1) + fibonacci(n - 2)
    _ -> 0  // Invalid input
  }
}

// String processing functions
pub fn capitalize_words(text: String) -> String {
  text
  |> string.split(" ")
  |> list.map(string.capitalise)
  |> string.join(" ")
}

pub fn reverse_string(text: String) -> String {
  text
  |> string.to_graphemes
  |> list.reverse
  |> string.concat
}

// User manipulation functions
pub fn create_user(id: Int, name: String, email: String, age: Int) -> User {
  User(id: id, name: name, email: email, age: age)
}

pub fn update_user_age(user: User, new_age: Int) -> User {
  User(..user, age: new_age)
}

pub fn is_adult(user: User) -> Bool {
  user.age >= 18
}

pub fn format_user(user: User) -> String {
  user.name <> " (" <> int.to_string(user.age) <> ") - " <> user.email
}

// Point operations
pub fn distance(p1: Point, p2: Point) -> Float {
  let dx = p1.x -. p2.x
  let dy = p1.y -. p2.y
  // Simplified square root calculation
  dx *. dx +. dy *. dy
}

pub fn translate_point(point: Point, dx: Float, dy: Float) -> Point {
  Point(x: point.x +. dx, y: point.y +. dy)
}

pub fn origin() -> Point {
  Point(x: 0.0, y: 0.0)
}

// Result handling functions
pub fn divide(a: Float, b: Float) -> Result(Float, String) {
  case b {
    0.0 -> Error("Division by zero")
    _ -> Ok(a /. b)
  }
}

pub fn safe_parse_int(text: String) -> Result(Int, String) {
  case int.parse(text) {
    Ok(value) -> Ok(value)
    Error(_) -> Error("Invalid integer: " <> text)
  }
}

// Configuration functions
pub fn default_config() -> Config {
  Config(
    host: "localhost",
    port: 8080,
    timeout: 5000,
    retries: 3,
    debug: False,
  )
}

pub fn update_config_port(config: Config, port: Int) -> Config {
  Config(..config, port: port)
}

pub fn is_debug_mode(config: Config) -> Bool {
  config.debug
}

// HTTP status handling
pub fn status_code(status: HttpStatus) -> Int {
  case status {
    Ok -> 200
    NotFound -> 404
    BadRequest(_) -> 400
    InternalError(_) -> 500
  }
}

pub fn status_message(status: HttpStatus) -> String {
  case status {
    Ok -> "OK"
    NotFound -> "Not Found"
    BadRequest(msg) -> "Bad Request: " <> msg
    InternalError(msg) -> "Internal Server Error: " <> msg
  }
}

// Generic utility functions
pub fn identity(x: a) -> a {
  x
}

pub fn constant(value: a) -> fn(b) -> a {
  fn(_) { value }
}

pub fn flip(func: fn(a, b) -> c) -> fn(b, a) -> c {
  fn(b, a) { func(a, b) }
}

// List utility functions
pub fn take_while(items: List(a), predicate: fn(a) -> Bool) -> List(a) {
  case items {
    [] -> []
    [head, ..tail] ->
      case predicate(head) {
        True -> [head, ..take_while(tail, predicate)]
        False -> []
      }
  }
}

pub fn drop_while(items: List(a), predicate: fn(a) -> Bool) -> List(a) {
  case items {
    [] -> []
    [head, ..tail] ->
      case predicate(head) {
        True -> drop_while(tail, predicate)
        False -> [head, ..tail]
      }
  }
}

// Main function demonstrating usage
pub fn main() {
  // Test colors
  let red = Red
  let custom_color = Custom(255, 128, 0)
  io.println("Red color: " <> color_to_string(red))
  io.println("Custom color: " <> color_to_string(custom_color))
  
  // Test shapes
  let circle = Circle(5.0)
  let rectangle = Rectangle(4.0, 3.0)
  io.println("Circle area: " <> string.inspect(shape_area(circle)))
  io.println("Rectangle area: " <> string.inspect(shape_area(rectangle)))
  
  // Test users
  let user = create_user(1, "Alice", "alice@example.com", 25)
  let updated_user = update_user_age(user, 26)
  io.println("User: " <> format_user(updated_user))
  io.println("Is adult: " <> string.inspect(is_adult(updated_user)))
  
  // Test points
  let p1 = Point(1.0, 2.0)
  let p2 = Point(4.0, 6.0)
  let distance_value = distance(p1, p2)
  io.println("Distance: " <> string.inspect(distance_value))
  
  // Test Maybe
  let some_value = Some(42)
  let none_value = None
  let doubled_some = maybe_map(some_value, fn(x) { x * 2 })
  let doubled_none = maybe_map(none_value, fn(x) { x * 2 })
  io.println("Doubled some: " <> string.inspect(doubled_some))
  io.println("Doubled none: " <> string.inspect(doubled_none))
  
  // Test list operations
  let numbers = [1, 2, 3, 4, 5]
  let even_doubled = filter_map(numbers, fn(x) { x % 2 == 0 }, fn(x) { x * 2 })
  io.println("Even numbers doubled: " <> string.inspect(even_doubled))
  
  // Test recursive functions
  let fact_5 = factorial(5)
  let fib_7 = fibonacci(7)
  io.println("Factorial of 5: " <> int.to_string(fact_5))
  io.println("Fibonacci of 7: " <> int.to_string(fib_7))
  
  // Test string operations
  let text = "hello world gleam"
  let capitalized = capitalize_words(text)
  let reversed = reverse_string("gleam")
  io.println("Capitalized: " <> capitalized)
  io.println("Reversed: " <> reversed)
  
  // Test division
  case divide(10.0, 2.0) {
    Ok(result) -> io.println("10 / 2 = " <> string.inspect(result))
    Error(msg) -> io.println("Error: " <> msg)
  }
  
  case divide(10.0, 0.0) {
    Ok(result) -> io.println("10 / 0 = " <> string.inspect(result))
    Error(msg) -> io.println("Error: " <> msg)
  }
  
  // Test higher-order functions
  let add_one = fn(x) { x + 1 }
  let result = apply_twice(add_one, 5)
  io.println("Apply add_one twice to 5: " <> int.to_string(result))
  
  // Test configuration
  let config = default_config()
  let updated_config = update_config_port(config, 9000)
  io.println("Updated port: " <> int.to_string(updated_config.port))
  
  io.println("Gleam test completed!")
}
