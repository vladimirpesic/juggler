# Comprehensive Ruby test file with all structural elements
# Contains: classes, modules, functions, mixins, constants

# Module with constants and methods
module Drawable
  PI = 3.14159
  
  def draw
    raise NotImplementedError, "Must implement draw method"
  end
  
  def get_area
    raise NotImplementedError, "Must implement get_area method"
  end
  
  module_function
  
  def default_color
    "white"
  end
end

# Mixin module (trait-like behavior)
module Loggable
  def initialize_logging
    @logs = []
  end
  
  def log(message)
    @logs ||= []
    @logs << "#{Time.now}: #{message}"
  end
  
  def get_logs
    @logs || []
  end
end

# Enumeration using constants
module Color
  RED = "red"
  GREEN = "green"
  BLUE = "blue"
  
  ALL_COLORS = [RED, GREEN, BLUE].freeze
  
  def self.valid?(color)
    ALL_COLORS.include?(color)
  end
end

# Base class with abstract-like behavior
class Shape
  include Drawable
  include Loggable
  
  attr_reader :name, :color
  
  def initialize(name, color)
    @name = name
    @color = color
    initialize_logging
    log("Shape #{name} created with color #{color}")
  end
  
  def describe
    "#{@name} shape in #{@color} color"
  end
  
  # Virtual method (to be overridden)
  def get_area
    raise NotImplementedError, "Subclass must implement get_area"
  end
end

# Concrete class
class Rectangle < Shape
  attr_accessor :width, :height
  
  def initialize(name, color, width, height)
    super(name, color)
    @width = width
    @height = height
  end
  
  def draw
    puts "Drawing rectangle: #{@name} (#{@width}x#{@height})"
  end
  
  def get_area
    @width * @height
  end
  
  def get_perimeter
    2 * (@width + @height)
  end
end

# Another concrete class
class Circle < Shape
  attr_accessor :radius
  
  def initialize(name, color, radius)
    super(name, color)
    @radius = radius
  end
  
  def draw
    puts "Drawing circle: #{@name} (radius: #{@radius})"
  end
  
  def get_area
    Drawable::PI * (@radius ** 2)
  end
  
  def get_circumference
    2 * Drawable::PI * @radius
  end
end

# Class with class methods and variables
class MathUtils
  @@calculation_count = 0
  
  def self.factorial(n)
    @@calculation_count += 1
    return 1 if n <= 1
    n * factorial(n - 1)
  end
  
  def self.fibonacci(n)
    @@calculation_count += 1
    return n if n <= 1
    fibonacci(n - 1) + fibonacci(n - 2)
  end
  
  def self.is_prime?(n)
    @@calculation_count += 1
    return false if n < 2
    (2..Math.sqrt(n)).none? { |i| n % i == 0 }
  end
  
  def self.calculation_count
    @@calculation_count
  end
  
  def self.reset_count
    @@calculation_count = 0
  end
end

# Singleton class
class DatabaseConnection
  @@instance = nil
  
  private_class_method :new
  
  def self.instance
    @@instance ||= new
  end
  
  def initialize
    @connected = false
    @connection_id = rand(10000)
  end
  
  def connect
    @connected = true
    puts "Connected with ID: #{@connection_id}"
  end
  
  def disconnect
    @connected = false
    puts "Disconnected"
  end
  
  def connected?
    @connected
  end
end

# Struct-like class
Person = Struct.new(:name, :age, :email) do
  def adult?
    age >= 18
  end
  
  def introduce
    "Hi, I'm #{name}, #{age} years old"
  end
end

# Module with nested classes
module Graphics
  class Renderer
    def initialize(type)
      @type = type
    end
    
    def render(shape)
      puts "Rendering #{shape.class.name} with #{@type} renderer"
      shape.draw
    end
  end
  
  class Canvas
    def initialize(width, height)
      @width = width
      @height = height
      @shapes = []
    end
    
    def add_shape(shape)
      @shapes << shape
    end
    
    def render_all(renderer)
      @shapes.each { |shape| renderer.render(shape) }
    end
    
    def total_area
      @shapes.sum(&:get_area)
    end
  end
end

# Global functions
def global_function(message)
  puts "Global function called: #{message}"
end

def array_processor(data, &block)
  data.map(&block)
end

def type_converter(data, type)
  case type
  when :string
    data.to_s
  when :integer
    data.to_i
  when :float
    data.to_f
  when :symbol
    data.to_sym
  else
    data
  end
end

# Lambda and Proc examples
square_lambda = ->(x) { x * x }
cube_proc = proc { |x| x ** 3 }

# Class with method visibility
class SecureClass
  def initialize(secret)
    @secret = secret
  end
  
  def public_method
    "This is public: #{reveal_secret}"
  end
  
  protected
  
  def protected_method
    "Protected method"
  end
  
  private
  
  def reveal_secret
    decrypt(@secret)
  end
  
  def decrypt(data)
    data.reverse
  end
end

# Metaclass example
class DynamicClass
  def self.create_method(name, &block)
    define_method(name, &block)
  end
end

# Usage examples
if __FILE__ == $0
  # Create shapes
  rectangle = Rectangle.new("TestRect", Color::BLUE, 10.0, 5.0)
  circle = Circle.new("TestCircle", Color::GREEN, 3.0)
  
  # Test drawing
  rectangle.draw
  circle.draw
  
  puts "Rectangle area: #{rectangle.get_area}"
  puts "Circle area: #{circle.get_area}"
  
  # Test utility functions
  puts "Factorial of 5: #{MathUtils.factorial(5)}"
  puts "10th Fibonacci number: #{MathUtils.fibonacci(10)}"
  puts "Is 17 prime? #{MathUtils.is_prime?(17)}"
  puts "Total calculations: #{MathUtils.calculation_count}"
  
  # Test global function
  global_function("Hello from Ruby!")
  
  # Test array processing
  numbers = [1, 2, 3, 4, 5]
  squares = array_processor(numbers, &square_lambda)
  cubes = array_processor(numbers, &cube_proc)
  
  puts "Squares: #{squares}"
  puts "Cubes: #{cubes}"
  
  # Test struct
  person = Person.new("Alice", 25, "alice@example.com")
  puts person.introduce
  puts "Is adult? #{person.adult?}"
  
  # Test graphics module
  renderer = Graphics::Renderer.new("OpenGL")
  canvas = Graphics::Canvas.new(800, 600)
  
  canvas.add_shape(rectangle)
  canvas.add_shape(circle)
  
  canvas.render_all(renderer)
  puts "Total canvas area: #{canvas.total_area}"
  
  # Test singleton
  db1 = DatabaseConnection.instance
  db2 = DatabaseConnection.instance
  
  puts "Same instance? #{db1.object_id == db2.object_id}"
  db1.connect
  
  # Test dynamic method creation
  DynamicClass.create_method(:dynamic_hello) do |name|
    "Hello, #{name}!"
  end
  
  obj = DynamicClass.new
  puts obj.dynamic_hello("World")
end
