/**
 * JavaScript Language Test File
 * Tests all structural elements supported by the JavaScript parser
 */

// Global variables
var globalVar = "I'm global";
let globalLet = "I'm also global";
const GLOBAL_CONST = "I'm a constant";

// Function declaration
function add(a, b) {
    return a + b;
}

// Function expression
const multiply = function(a, b) {
    return a * b;
};

// Arrow function
const divide = (a, b) => {
    if (b === 0) {
        throw new Error("Division by zero");
    }
    return a / b;
};

// Arrow function (single expression)
const square = x => x * x;

// Async function
async function fetchData(url) {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching data:", error);
        throw error;
    }
}

// Generator function
function* numberGenerator(max) {
    let current = 0;
    while (current < max) {
        yield current++;
    }
}

// Higher-order function
function applyOperation(a, b, operation) {
    return operation(a, b);
}

// Function with default parameters
function greet(name = "World", greeting = "Hello") {
    return `${greeting}, ${name}!`;
}

// Function with rest parameters
function sum(...numbers) {
    return numbers.reduce((total, num) => total + num, 0);
}

// Function with destructuring parameters
function processUser({name, age, email = "unknown"}) {
    return {
        displayName: name.toUpperCase(),
        isAdult: age >= 18,
        contact: email
    };
}

// Recursive function
function factorial(n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// Constructor function (old style)
function Person(name, age) {
    this.name = name;
    this.age = age;
    
    this.introduce = function() {
        return `Hi, I'm ${this.name} and I'm ${this.age} years old.`;
    };
}

// Prototype method
Person.prototype.celebrate = function() {
    this.age++;
    console.log(`${this.name} is now ${this.age} years old!`);
};

// ES6 Class
class Animal {
    constructor(name, species) {
        this.name = name;
        this.species = species;
        this._energy = 100;
    }
    
    // Getter
    get energy() {
        return this._energy;
    }
    
    // Setter
    set energy(value) {
        this._energy = Math.max(0, Math.min(100, value));
    }
    
    // Method
    speak() {
        console.log(`${this.name} makes a sound`);
        this._energy -= 5;
    }
    
    // Static method
    static compare(animal1, animal2) {
        return animal1.energy - animal2.energy;
    }
}

// Class inheritance
class Dog extends Animal {
    constructor(name, breed) {
        super(name, "Canine");
        this.breed = breed;
    }
    
    // Override method
    speak() {
        console.log(`${this.name} barks!`);
        this._energy -= 3;
    }
    
    // Additional method
    fetch() {
        console.log(`${this.name} fetches the ball`);
        this._energy -= 10;
    }
}

// Object literal with methods
const calculator = {
    result: 0,
    
    add(value) {
        this.result += value;
        return this;
    },
    
    multiply(value) {
        this.result *= value;
        return this;
    },
    
    subtract(value) {
        this.result -= value;
        return this;
    },
    
    divide(value) {
        if (value !== 0) {
            this.result /= value;
        }
        return this;
    },
    
    reset() {
        this.result = 0;
        return this;
    },
    
    getValue() {
        return this.result;
    }
};

// Module pattern (IIFE)
const MathUtils = (function() {
    // Private variables
    const PI = Math.PI;
    let calculations = 0;
    
    // Private function
    function incrementCalculations() {
        calculations++;
    }
    
    // Public API
    return {
        circleArea(radius) {
            incrementCalculations();
            return PI * radius * radius;
        },
        
        circleCircumference(radius) {
            incrementCalculations();
            return 2 * PI * radius;
        },
        
        getCalculationCount() {
            return calculations;
        }
    };
})();

// Object creation patterns
const ObjectFactory = {
    createPoint(x, y) {
        return {
            x: x || 0,
            y: y || 0,
            
            distanceFromOrigin() {
                return Math.sqrt(this.x * this.x + this.y * this.y);
            },
            
            distanceTo(other) {
                const dx = this.x - other.x;
                const dy = this.y - other.y;
                return Math.sqrt(dx * dx + dy * dy);
            },
            
            move(dx, dy) {
                this.x += dx;
                this.y += dy;
                return this;
            }
        };
    },
    
    createRectangle(width, height) {
        return {
            width: width || 0,
            height: height || 0,
            
            get area() {
                return this.width * this.height;
            },
            
            get perimeter() {
                return 2 * (this.width + this.height);
            },
            
            resize(newWidth, newHeight) {
                this.width = newWidth;
                this.height = newHeight;
                return this;
            }
        };
    }
};

// Closure examples
function createCounter(initialValue = 0) {
    let count = initialValue;
    
    return {
        increment() {
            return ++count;
        },
        
        decrement() {
            return --count;
        },
        
        getValue() {
            return count;
        },
        
        reset() {
            count = initialValue;
            return count;
        }
    };
}

// Promise-based function
function delay(ms, value) {
    return new Promise((resolve) => {
        setTimeout(() => resolve(value), ms);
    });
}

// Promise chain example
function processData(data) {
    return Promise.resolve(data)
        .then(data => data.map(item => item * 2))
        .then(data => data.filter(item => item > 10))
        .then(data => data.reduce((sum, item) => sum + item, 0));
}

// Array processing functions
const arrayUtils = {
    // Functional programming style
    pipe(...functions) {
        return (value) => functions.reduce((acc, fn) => fn(acc), value);
    },
    
    compose(...functions) {
        return (value) => functions.reduceRight((acc, fn) => fn(acc), value);
    },
    
    // Array manipulation
    chunk(array, size) {
        const chunks = [];
        for (let i = 0; i < array.length; i += size) {
            chunks.push(array.slice(i, i + size));
        }
        return chunks;
    },
    
    unique(array) {
        return [...new Set(array)];
    },
    
    flatten(array) {
        return array.reduce((flat, item) => {
            return flat.concat(Array.isArray(item) ? this.flatten(item) : item);
        }, []);
    }
};

// Event handling simulation
function EventEmitter() {
    this.events = {};
    
    this.on = function(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
        return this;
    };
    
    this.emit = function(event, ...args) {
        if (this.events[event]) {
            this.events[event].forEach(callback => callback(...args));
        }
        return this;
    };
    
    this.off = function(event, callback) {
        if (this.events[event]) {
            this.events[event] = this.events[event].filter(cb => cb !== callback);
        }
        return this;
    };
}

// Mixin pattern
const Flyable = {
    fly() {
        console.log(`${this.name} is flying!`);
    }
};

const Swimmable = {
    swim() {
        console.log(`${this.name} is swimming!`);
    }
};

function createDuck(name) {
    const duck = {
        name: name,
        quack() {
            console.log(`${this.name} says quack!`);
        }
    };
    
    // Apply mixins
    Object.assign(duck, Flyable, Swimmable);
    return duck;
}

// Error handling patterns
class CustomError extends Error {
    constructor(message, code) {
        super(message);
        this.name = "CustomError";
        this.code = code;
    }
}

function validateInput(input) {
    if (!input) {
        throw new CustomError("Input is required", "MISSING_INPUT");
    }
    
    if (typeof input !== "string") {
        throw new CustomError("Input must be a string", "INVALID_TYPE");
    }
    
    if (input.length < 3) {
        throw new CustomError("Input must be at least 3 characters", "TOO_SHORT");
    }
    
    return input.trim().toLowerCase();
}

// Debounce utility function
function debounce(func, delay) {
    let timeoutId;
    
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// Throttle utility function
function throttle(func, limit) {
    let inThrottle;
    
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Main execution and examples
function main() {
    console.log("=== JavaScript Test Examples ===");
    
    // Basic functions
    console.log("Add:", add(5, 3));
    console.log("Multiply:", multiply(4, 7));
    console.log("Square:", square(9));
    
    // Objects and classes
    const person = new Person("Alice", 25);
    console.log(person.introduce());
    person.celebrate();
    
    const dog = new Dog("Buddy", "Golden Retriever");
    dog.speak();
    dog.fetch();
    console.log("Dog energy:", dog.energy);
    
    // Calculator chaining
    const result = calculator
        .reset()
        .add(10)
        .multiply(2)
        .subtract(5)
        .divide(3)
        .getValue();
    console.log("Calculator result:", result);
    
    // Math utilities
    console.log("Circle area:", MathUtils.circleArea(5));
    console.log("Calculations made:", MathUtils.getCalculationCount());
    
    // Factory pattern
    const point = ObjectFactory.createPoint(3, 4);
    console.log("Distance from origin:", point.distanceFromOrigin());
    
    // Counter with closures
    const counter = createCounter(10);
    console.log("Counter:", counter.increment());
    console.log("Counter:", counter.increment());
    console.log("Counter:", counter.decrement());
    
    // Array utilities
    const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    const doubled = numbers.map(n => n * 2);
    const filtered = doubled.filter(n => n > 10);
    console.log("Processed array:", filtered);
    
    // Generator
    const gen = numberGenerator(5);
    console.log("Generated numbers:");
    for (const num of gen) {
        console.log(num);
    }
    
    // Event emitter
    const emitter = new EventEmitter();
    emitter.on('test', (message) => console.log("Event received:", message));
    emitter.emit('test', 'Hello from event!');
    
    // Duck with mixins
    const duck = createDuck("Donald");
    duck.quack();
    duck.fly();
    duck.swim();
    
    // Error handling
    try {
        validateInput("ab");
    } catch (error) {
        console.log("Validation error:", error.message, "Code:", error.code);
    }
    
    // Promise example
    processData([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        .then(result => console.log("Promise result:", result))
        .catch(error => console.error("Promise error:", error));
    
    console.log("=== All JavaScript tests completed ===");
}

// React Components (JSX Examples)
function WelcomeComponent(props) {
    return <div className="welcome">
        <h1>Hello, {props.name}!</h1>
        <UserProfile user={props.user} />
    </div>;
}

const UserProfile = ({ user }) => {
    return <div className="user-profile">
        <img src={user.avatar} alt={user.name} />
        <span>{user.name}</span>
        <StatusIndicator isOnline={user.isOnline} />
    </div>;
};

function StatusIndicator({ isOnline }) {
    return <span className={isOnline ? 'online' : 'offline'}>
        {isOnline ? '🟢' : '🔴'}
    </span>;
}

// Class-based React Component
class NavigationMenu extends Component {
    constructor(props) {
        super(props);
        this.state = { isOpen: false };
    }
    
    render() {
        return <nav className="navigation">
            <MenuButton onClick={() => this.setState({ isOpen: !this.state.isOpen })} />
            {this.state.isOpen && <MenuItems items={this.props.items} />}
        </nav>;
    }
}

// Immediately invoked function expression (IIFE) to run main
(function() {
    // Check if running in browser or Node.js
    if (typeof window !== 'undefined') {
        // Browser environment
        console.log("Running in browser");
        window.addEventListener('load', main);
    } else if (typeof module !== 'undefined' && module.exports) {
        // Node.js environment
        console.log("Running in Node.js");
        main();
    } else {
        // Fallback
        main();
    }
})();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        add,
        multiply,
        factorial,
        Person,
        Animal,
        Dog,
        calculator,
        MathUtils,
        ObjectFactory,
        createCounter,
        arrayUtils,
        EventEmitter,
        createDuck,
        CustomError,
        validateInput,
        debounce,
        throttle
    };
}
