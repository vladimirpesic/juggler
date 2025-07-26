<?php
/**
 * Comprehensive PHP test file with all structural elements
 * Contains: classes, functions, traits, interfaces, enums (PHP 8.1+)
 */

namespace TestNamespace {

    // Enum (PHP 8.1+)
    enum Color: string {
        case Red = 'red';
        case Green = 'green';
        case Blue = 'blue';
        
        public function getHexValue(): string {
            return match($this) {
                Color::Red => '#FF0000',
                Color::Green => '#00FF00',
                Color::Blue => '#0000FF',
            };
        }
    }

    // Interface
    interface Drawable {
        public function draw(): void;
        public function getArea(): float;
    }

    // Trait
    trait Loggable {
        protected array $logs = [];
        
        public function log(string $message): void {
            $this->logs[] = date('Y-m-d H:i:s') . ': ' . $message;
        }
        
        public function getLogs(): array {
            return $this->logs;
        }
    }

    // Abstract class
    abstract class Shape implements Drawable {
        use Loggable;
        
        protected string $name;
        protected Color $color;
        
        public function __construct(string $name, Color $color) {
            $this->name = $name;
            $this->color = $color;
            $this->log("Shape {$name} created with color {$color->value}");
        }
        
        public function getName(): string {
            return $this->name;
        }
        
        public function getColor(): Color {
            return $this->color;
        }
        
        abstract public function getArea(): float;
    }

    // Concrete class extending abstract class
    class Rectangle extends Shape {
        private float $width;
        private float $height;
        
        public function __construct(string $name, Color $color, float $width, float $height) {
            parent::__construct($name, $color);
            $this->width = $width;
            $this->height = $height;
        }
        
        public function draw(): void {
            echo "Drawing rectangle: {$this->name} ({$this->width}x{$this->height})\n";
        }
        
        public function getArea(): float {
            return $this->width * $this->height;
        }
        
        public function getPerimeter(): float {
            return 2 * ($this->width + $this->height);
        }
    }

    // Another concrete class
    class Circle extends Shape {
        private float $radius;
        
        public function __construct(string $name, Color $color, float $radius) {
            parent::__construct($name, $color);
            $this->radius = $radius;
        }
        
        public function draw(): void {
            echo "Drawing circle: {$this->name} (radius: {$this->radius})\n";
        }
        
        public function getArea(): float {
            return pi() * pow($this->radius, 2);
        }
        
        public function getCircumference(): float {
            return 2 * pi() * $this->radius;
        }
    }

}

namespace TestNamespace\Utils {
    
    // Utility class with static methods
    class MathUtils {
        public static function factorial(int $n): int {
            if ($n <= 1) {
                return 1;
            }
            return $n * self::factorial($n - 1);
        }
        
        public static function fibonacci(int $n): int {
            if ($n <= 1) {
                return $n;
            }
            return self::fibonacci($n - 1) + self::fibonacci($n - 2);
        }
        
        public static function isPrime(int $n): bool {
            if ($n < 2) {
                return false;
            }
            for ($i = 2; $i <= sqrt($n); $i++) {
                if ($n % $i === 0) {
                    return false;
                }
            }
            return true;
        }
    }

}

// Global functions
function globalFunction(string $message): void {
    echo "Global function called: {$message}\n";
}

function arrayProcessor(array $data, callable $callback): array {
    return array_map($callback, $data);
}

function genericProcessor(mixed $data, string $type): mixed {
    return match($type) {
        'string' => (string) $data,
        'int' => (int) $data,
        'float' => (float) $data,
        'bool' => (bool) $data,
        default => $data,
    };
}

// Anonymous class example
$anonymousShape = new class('Anonymous', TestNamespace\Color::Red) extends TestNamespace\Shape {
    public function draw(): void {
        echo "Drawing anonymous shape\n";
    }
    
    public function getArea(): float {
        return 0.0;
    }
};

// Main execution
use TestNamespace\Rectangle;
use TestNamespace\Circle;
use TestNamespace\Color;
use TestNamespace\Utils\MathUtils;

$rectangle = new Rectangle('TestRect', Color::Blue, 10.0, 5.0);
$circle = new Circle('TestCircle', Color::Green, 3.0);

$rectangle->draw();
$circle->draw();

echo "Rectangle area: " . $rectangle->getArea() . "\n";
echo "Circle area: " . $circle->getArea() . "\n";

echo "Factorial of 5: " . MathUtils::factorial(5) . "\n";
echo "10th Fibonacci number: " . MathUtils::fibonacci(10) . "\n";
echo "Is 17 prime? " . (MathUtils::isPrime(17) ? 'Yes' : 'No') . "\n";

globalFunction("Hello from global function");

$numbers = [1, 2, 3, 4, 5];
$squares = arrayProcessor($numbers, fn($x) => $x * $x);
print_r($squares);

?>
