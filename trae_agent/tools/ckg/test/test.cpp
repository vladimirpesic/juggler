/*
 * C++ Language Test File
 * Tests all structural elements supported by the C++ parser
 */

#include <iostream>
#include <vector>
#include <string>
#include <memory>

// Namespace declaration
namespace Math {
    const double PI = 3.14159;
    
    // Function in namespace
    double calculate_area(double radius) {
        return PI * radius * radius;
    }
}

// Nested namespace (C++17)
namespace Graphics::Geometry {
    struct Point2D {
        double x, y;
    };
}

// Global variable
int global_counter = 0;

// Enum class (C++11)
enum class Status {
    SUCCESS = 0,
    ERROR = 1,
    PENDING = 2
};

// Traditional enum
enum Color {
    RED, GREEN, BLUE
};

// Struct with constructor
struct Point {
    int x, y;
    
    // Constructor
    Point(int x_val, int y_val) : x(x_val), y(y_val) {}
    
    // Member function
    double distance_from_origin() const {
        return std::sqrt(x * x + y * y);
    }
};

// Union
union Data {
    int integer_value;
    float float_value;
    char string_value[100];
    
    // Constructor for union (C++11)
    Data(int val) : integer_value(val) {}
};

// Class with inheritance
class Shape {
protected:
    std::string name;
    
public:
    Shape(const std::string& n) : name(n) {}
    virtual ~Shape() = default;
    
    // Pure virtual function
    virtual double area() const = 0;
    
    // Virtual function
    virtual void display() const {
        std::cout << "Shape: " << name << std::endl;
    }
    
    // Static member function
    static int get_shape_count() {
        return shape_count;
    }
    
private:
    static int shape_count;
};

// Static member definition
int Shape::shape_count = 0;

// Derived class
class Rectangle : public Shape {
private:
    double width, height;
    
public:
    Rectangle(double w, double h) : Shape("Rectangle"), width(w), height(h) {}
    
    // Override virtual function
    double area() const override {
        return width * height;
    }
    
    void display() const override {
        Shape::display();
        std::cout << "Width: " << width << ", Height: " << height << std::endl;
    }
    
    // Friend function declaration
    friend std::ostream& operator<<(std::ostream& os, const Rectangle& rect);
};

// Friend function implementation
std::ostream& operator<<(std::ostream& os, const Rectangle& rect) {
    os << "Rectangle(" << rect.width << "x" << rect.height << ")";
    return os;
}

// Template class
template<typename T>
class Container {
private:
    std::vector<T> data;
    
public:
    void add(const T& item) {
        data.push_back(item);
    }
    
    T get(size_t index) const {
        if (index < data.size()) {
            return data[index];
        }
        throw std::out_of_range("Index out of range");
    }
    
    size_t size() const {
        return data.size();
    }
};

// Template function
template<typename T>
T max_value(T a, T b) {
    return (a > b) ? a : b;
}

// Template specialization
template<>
std::string max_value<std::string>(std::string a, std::string b) {
    return (a.length() > b.length()) ? a : b;
}

// Lambda function usage in a function
void demonstrate_lambdas() {
    auto square = [](int x) { return x * x; };
    auto add = [](int a, int b) -> int { return a + b; };
    
    std::cout << "Square of 5: " << square(5) << std::endl;
    std::cout << "Add 3 + 4: " << add(3, 4) << std::endl;
}

// Function overloading
int add(int a, int b) {
    return a + b;
}

double add(double a, double b) {
    return a + b;
}

std::string add(const std::string& a, const std::string& b) {
    return a + b;
}

// Function with default parameters
void print_info(const std::string& name, int age = 0, bool verbose = false) {
    std::cout << "Name: " << name;
    if (age > 0) {
        std::cout << ", Age: " << age;
    }
    if (verbose) {
        std::cout << " (verbose mode)";
    }
    std::cout << std::endl;
}

// Recursive function
long long fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Function with reference parameters
void swap_values(int& a, int& b) {
    int temp = a;
    a = b;
    b = temp;
}

// Function using smart pointers
std::unique_ptr<Rectangle> create_rectangle(double w, double h) {
    return std::make_unique<Rectangle>(w, h);
}

// Operator overloading
class Complex {
private:
    double real, imag;
    
public:
    Complex(double r = 0, double i = 0) : real(r), imag(i) {}
    
    // Operator overloading
    Complex operator+(const Complex& other) const {
        return Complex(real + other.real, imag + other.imag);
    }
    
    Complex operator*(const Complex& other) const {
        return Complex(
            real * other.real - imag * other.imag,
            real * other.imag + imag * other.real
        );
    }
    
    // Member function
    void display() const {
        std::cout << real << " + " << imag << "i" << std::endl;
    }
};

// Main function
int main() {
    // Using namespace
    std::cout << "Circle area: " << Math::calculate_area(5.0) << std::endl;
    
    // Using struct
    Point p(3, 4);
    std::cout << "Distance from origin: " << p.distance_from_origin() << std::endl;
    
    // Using class hierarchy
    auto rect = create_rectangle(5.0, 3.0);
    rect->display();
    std::cout << "Area: " << rect->area() << std::endl;
    
    // Using template
    Container<int> int_container;
    int_container.add(10);
    int_container.add(20);
    std::cout << "Container size: " << int_container.size() << std::endl;
    
    // Template function
    std::cout << "Max of 10 and 20: " << max_value(10, 20) << std::endl;
    std::cout << "Max string: " << max_value<std::string>("hello", "world") << std::endl;
    
    // Function overloading
    std::cout << "Add ints: " << add(5, 3) << std::endl;
    std::cout << "Add doubles: " << add(5.5, 3.3) << std::endl;
    std::cout << "Add strings: " << add(std::string("Hello "), std::string("World")) << std::endl;
    
    // Lambda demonstration
    demonstrate_lambdas();
    
    // Complex number operations
    Complex c1(3, 4);
    Complex c2(1, 2);
    Complex sum = c1 + c2;
    Complex product = c1 * c2;
    
    std::cout << "Sum: ";
    sum.display();
    std::cout << "Product: ";
    product.display();
    
    // Fibonacci
    std::cout << "Fibonacci(10): " << fibonacci(10) << std::endl;
    
    // Swap values
    int x = 10, y = 20;
    swap_values(x, y);
    std::cout << "Swapped: x=" << x << ", y=" << y << std::endl;
    
    return 0;
}
