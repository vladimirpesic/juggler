/*
 * Rust Language Test File
 * Tests all structural elements supported by the Rust parser
 */

// Module declaration
pub mod geometry {
    use std::f64::consts::PI;
    
    // Struct with public fields
    #[derive(Debug, Clone, Copy)]
    pub struct Point {
        pub x: f64,
        pub y: f64,
    }
    
    impl Point {
        // Associated function (constructor)
        pub fn new(x: f64, y: f64) -> Self {
            Point { x, y }
        }
        
        // Method with self reference
        pub fn distance_from_origin(&self) -> f64 {
            (self.x * self.x + self.y * self.y).sqrt()
        }
        
        // Method with mutable self reference
        pub fn move_by(&mut self, dx: f64, dy: f64) {
            self.x += dx;
            self.y += dy;
        }
    }
    
    // Circle area calculation function
    pub fn circle_area(radius: f64) -> f64 {
        PI * radius * radius
    }
}

use std::collections::HashMap;
use std::fmt::{self, Display, Formatter};

// Global constant
const MAX_ITEMS: usize = 100;

// Static variable
static mut COUNTER: i32 = 0;

// Type alias
type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;
type Point2D = geometry::Point;

// Enum with different variant types
#[derive(Debug, PartialEq)]
pub enum Status {
    Success,
    Error(String),
    Warning { code: i32, message: String },
    Pending(i32),
}

// Enum with methods
impl Status {
    pub fn is_error(&self) -> bool {
        matches!(self, Status::Error(_))
    }
    
    pub fn get_message(&self) -> Option<&str> {
        match self {
            Status::Error(msg) => Some(msg),
            Status::Warning { message, .. } => Some(message),
            _ => None,
        }
    }
}

// Trait definition
pub trait Drawable {
    fn draw(&self);
    fn area(&self) -> f64;
    
    // Default implementation
    fn description(&self) -> String {
        format!("A drawable shape with area: {:.2}", self.area())
    }
}

// Generic trait
pub trait Container<T> {
    fn add(&mut self, item: T);
    fn get(&self, index: usize) -> Option<&T>;
    fn len(&self) -> usize;
    
    fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

// Struct definition
#[derive(Debug)]
pub struct Rectangle {
    width: f64,
    height: f64,
}

impl Rectangle {
    pub fn new(width: f64, height: f64) -> Result<Self> {
        if width <= 0.0 || height <= 0.0 {
            return Err("Dimensions must be positive".into());
        }
        Ok(Rectangle { width, height })
    }
    
    pub fn width(&self) -> f64 {
        self.width
    }
    
    pub fn height(&self) -> f64 {
        self.height
    }
    
    // Associated function
    pub fn square(side: f64) -> Result<Self> {
        Self::new(side, side)
    }
}

// Trait implementation
impl Drawable for Rectangle {
    fn draw(&self) {
        println!("Drawing rectangle: {}x{}", self.width, self.height);
    }
    
    fn area(&self) -> f64 {
        self.width * self.height
    }
}

// Display trait implementation
impl Display for Rectangle {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "Rectangle({}x{})", self.width, self.height)
    }
}

// Generic struct
#[derive(Debug)]
pub struct Vec2D<T> {
    x: T,
    y: T,
}

impl<T> Vec2D<T> 
where 
    T: Copy + std::ops::Add<Output = T>
{
    pub fn new(x: T, y: T) -> Self {
        Vec2D { x, y }
    }
    
    pub fn add(&self, other: &Vec2D<T>) -> Vec2D<T> {
        Vec2D {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }
}

// Tuple struct
#[derive(Debug, PartialEq)]
pub struct Color(pub u8, pub u8, pub u8);

impl Color {
    pub const RED: Color = Color(255, 0, 0);
    pub const GREEN: Color = Color(0, 255, 0);
    pub const BLUE: Color = Color(0, 0, 255);
    
    pub fn mix(&self, other: &Color) -> Color {
        Color(
            (self.0 + other.0) / 2,
            (self.1 + other.1) / 2,
            (self.2 + other.2) / 2,
        )
    }
}

// Unit struct
#[derive(Debug)]
pub struct Empty;

impl Empty {
    pub fn do_nothing(&self) {
        println!("Doing nothing...");
    }
}

// Union (unsafe)
#[repr(C)]
union Data {
    integer: i32,
    float: f32,
    bytes: [u8; 4],
}

impl Data {
    pub fn new_int(value: i32) -> Self {
        Data { integer: value }
    }
    
    pub unsafe fn as_int(&self) -> i32 {
        self.integer
    }
    
    pub unsafe fn as_float(&self) -> f32 {
        self.float
    }
}

// Generic container implementation
#[derive(Debug)]
pub struct SimpleVec<T> {
    items: Vec<T>,
}

impl<T> SimpleVec<T> {
    pub fn new() -> Self {
        SimpleVec { items: Vec::new() }
    }
    
    pub fn with_capacity(capacity: usize) -> Self {
        SimpleVec { 
            items: Vec::with_capacity(capacity) 
        }
    }
}

impl<T> Container<T> for SimpleVec<T> {
    fn add(&mut self, item: T) {
        self.items.push(item);
    }
    
    fn get(&self, index: usize) -> Option<&T> {
        self.items.get(index)
    }
    
    fn len(&self) -> usize {
        self.items.len()
    }
}

// Function with generic parameters
pub fn max<T: PartialOrd + Copy>(a: T, b: T) -> T {
    if a > b { a } else { b }
}

// Function with lifetime parameters
pub fn longest<'a>(s1: &'a str, s2: &'a str) -> &'a str {
    if s1.len() > s2.len() { s1 } else { s2 }
}

// Function with closure parameter
pub fn apply_operation<F>(value: i32, operation: F) -> i32 
where
    F: Fn(i32) -> i32,
{
    operation(value)
}

// Recursive function
pub fn factorial(n: u64) -> u64 {
    match n {
        0 | 1 => 1,
        _ => n * factorial(n - 1),
    }
}

// Function with Result return type
pub fn divide(a: f64, b: f64) -> Result<f64> {
    if b == 0.0 {
        Err("Division by zero".into())
    } else {
        Ok(a / b)
    }
}

// Function with Option return type
pub fn find_in_list<T: PartialEq>(list: &[T], target: &T) -> Option<usize> {
    for (index, item) in list.iter().enumerate() {
        if item == target {
            return Some(index);
        }
    }
    None
}

// Macro definition
macro_rules! create_point {
    ($x:expr, $y:expr) => {
        geometry::Point::new($x as f64, $y as f64)
    };
}

// More complex macro
macro_rules! vec_of {
    ($elem:expr; $n:expr) => {
        vec![$elem; $n]
    };
    ($($x:expr),*) => {
        vec![$($x),*]
    };
}

// Async function
pub async fn fetch_data(id: u32) -> Result<String> {
    // Simulate async work
    tokio::time::sleep(std::time::Duration::from_millis(100)).await;
    Ok(format!("Data for ID: {}", id))
}

// Function with custom error handling
pub fn parse_number(s: &str) -> Result<i32> {
    s.parse::<i32>().map_err(|e| format!("Parse error: {}", e).into())
}

// Function demonstrating pattern matching
pub fn analyze_status(status: &Status) -> String {
    match status {
        Status::Success => "Operation completed successfully".to_string(),
        Status::Error(msg) => format!("Error occurred: {}", msg),
        Status::Warning { code, message } => {
            format!("Warning (code {}): {}", code, message)
        },
        Status::Pending(priority) => {
            format!("Operation pending with priority: {}", priority)
        }
    }
}

// Function with borrowing and ownership
pub fn process_strings(strings: Vec<String>) -> (Vec<String>, usize) {
    let count = strings.len();
    let uppercase: Vec<String> = strings
        .iter()
        .map(|s| s.to_uppercase())
        .collect();
    
    (uppercase, count)
}

// Function with mutable references
pub fn increment_all(numbers: &mut [i32]) {
    for num in numbers.iter_mut() {
        *num += 1;
    }
}

// Main function and tests
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_rectangle_creation() {
        let rect = Rectangle::new(5.0, 3.0).unwrap();
        assert_eq!(rect.area(), 15.0);
    }
    
    #[test]
    fn test_status_matching() {
        let status = Status::Warning { 
            code: 404, 
            message: "Not found".to_string() 
        };
        assert!(status.get_message().is_some());
    }
    
    #[test]
    fn test_generic_container() {
        let mut container = SimpleVec::new();
        container.add(42);
        container.add(24);
        
        assert_eq!(container.len(), 2);
        assert_eq!(container.get(0), Some(&42));
    }
}

// Main function for demonstration
fn main() -> Result<()> {
    // Using modules
    let point = geometry::Point::new(3.0, 4.0);
    println!("Point: {:?}", point);
    println!("Distance from origin: {:.2}", point.distance_from_origin());
    
    // Using enums
    let statuses = vec![
        Status::Success,
        Status::Error("Something went wrong".to_string()),
        Status::Warning { code: 101, message: "Be careful".to_string() },
        Status::Pending(5),
    ];
    
    for status in &statuses {
        println!("{}", analyze_status(status));
    }
    
    // Using structs and traits
    let rect = Rectangle::new(10.0, 5.0)?;
    rect.draw();
    println!("Rectangle: {}", rect);
    println!("Description: {}", rect.description());
    
    // Using generic types
    let int_vec = Vec2D::new(1, 2);
    let float_vec = Vec2D::new(1.5, 2.7);
    println!("Int vector: {:?}", int_vec);
    println!("Float vector: {:?}", float_vec);
    
    // Using colors
    let red = Color::RED;
    let blue = Color::BLUE;
    let purple = red.mix(&blue);
    println!("Mixed color: {:?}", purple);
    
    // Using container
    let mut container = SimpleVec::new();
    container.add("Hello");
    container.add("World");
    println!("Container length: {}", container.len());
    
    // Using functions
    println!("Max of 10 and 20: {}", max(10, 20));
    println!("Factorial of 5: {}", factorial(5));
    
    // Using closures
    let double = |x| x * 2;
    let result = apply_operation(21, double);
    println!("Double of 21: {}", result);
    
    // Pattern matching with results
    match divide(10.0, 2.0) {
        Ok(result) => println!("Division result: {}", result),
        Err(e) => println!("Division error: {}", e),
    }
    
    // Using macros
    let macro_point = create_point!(5, 7);
    println!("Macro-created point: {:?}", macro_point);
    
    let numbers = vec_of![1, 2, 3, 4, 5];
    println!("Macro-created vector: {:?}", numbers);
    
    // String processing
    let strings = vec![
        "hello".to_string(),
        "world".to_string(),
        "rust".to_string(),
    ];
    let (uppercase, count) = process_strings(strings);
    println!("Processed {} strings: {:?}", count, uppercase);
    
    // Mutable reference example
    let mut numbers = [1, 2, 3, 4, 5];
    increment_all(&mut numbers);
    println!("Incremented numbers: {:?}", numbers);
    
    // Unsafe union usage
    let data = Data::new_int(42);
    unsafe {
        println!("Union as int: {}", data.as_int());
        println!("Union as float: {}", data.as_float());
    }
    
    println!("All tests completed successfully!");
    Ok(())
}
