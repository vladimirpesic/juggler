/**
 * TypeScript Language Test File
 * Tests all structural elements supported by the TypeScript parser
 */

// Type definitions
type Point = {
    x: number;
    y: number;
};

type Status = 'pending' | 'completed' | 'failed';
type UserRole = 'admin' | 'user' | 'moderator';

// Interface definitions
interface Shape {
    readonly id: string;
    area(): number;
    perimeter(): number;
}

interface Drawable {
    draw(): void;
    color?: string;
}

// Generic interface
interface Container<T> {
    items: T[];
    add(item: T): void;
    get(index: number): T | undefined;
    size(): number;
}

// Interface with method signatures
interface EventListener<T = any> {
    (event: T): void;
}

// Interface extending other interfaces
interface ColoredShape extends Shape, Drawable {
    backgroundColor: string;
}

// Namespace declaration
namespace Geometry {
    export const PI = Math.PI;
    
    export interface Point3D extends Point {
        z: number;
    }
    
    export class Vector3D implements Point3D {
        constructor(
            public x: number,
            public y: number,
            public z: number
        ) {}
        
        magnitude(): number {
            return Math.sqrt(this.x ** 2 + this.y ** 2 + this.z ** 2);
        }
        
        normalize(): Vector3D {
            const mag = this.magnitude();
            return new Vector3D(this.x / mag, this.y / mag, this.z / mag);
        }
    }
    
    export function distance(p1: Point, p2: Point): number {
        return Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2);
    }
}

// Enum declarations
enum Direction {
    Up = "UP",
    Down = "DOWN",
    Left = "LEFT",
    Right = "RIGHT"
}

enum ResponseCode {
    Success = 200,
    NotFound = 404,
    ServerError = 500
}

const enum Color {
    Red = "#FF0000",
    Green = "#00FF00",
    Blue = "#0000FF"
}

// Type aliases
type Callback<T> = (value: T) => void;
type AsyncCallback<T> = (value: T) => Promise<void>;
type EventHandler<T> = (event: T) => boolean | void;

// Union and intersection types
type StringOrNumber = string | number;
type ReadonlyPoint = Readonly<Point>;
type PartialShape = Partial<Shape>;

// Mapped types
type Optional<T> = {
    [P in keyof T]?: T[P];
};

type Getters<T> = {
    [P in keyof T as `get${Capitalize<string & P>}`]: () => T[P];
};

// Conditional types
type NonNullable<T> = T extends null | undefined ? never : T;
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : any;

// Class with generics and decorators
abstract class BaseShape implements Shape {
    abstract readonly id: string;
    
    constructor(protected name: string) {}
    
    abstract area(): number;
    abstract perimeter(): number;
    
    describe(): string {
        return `${this.name} with area ${this.area().toFixed(2)}`;
    }
}

// Concrete class implementation
class Rectangle extends BaseShape implements ColoredShape {
    readonly id: string;
    color?: string;
    backgroundColor: string;
    
    constructor(
        private width: number,
        private height: number,
        backgroundColor: string = "#FFFFFF"
    ) {
        super("Rectangle");
        this.id = `rect_${Math.random().toString(36).substr(2, 9)}`;
        this.backgroundColor = backgroundColor;
    }
    
    // Getter and setter
    get Width(): number {
        return this.width;
    }
    
    set Width(value: number) {
        if (value <= 0) {
            throw new Error("Width must be positive");
        }
        this.width = value;
    }
    
    get Height(): number {
        return this.height;
    }
    
    set Height(value: number) {
        if (value <= 0) {
            throw new Error("Height must be positive");
        }
        this.height = value;
    }
    
    area(): number {
        return this.width * this.height;
    }
    
    perimeter(): number {
        return 2 * (this.width + this.height);
    }
    
    draw(): void {
        console.log(`Drawing rectangle: ${this.width}x${this.height}`);
    }
    
    // Static method
    static createSquare(side: number, backgroundColor?: string): Rectangle {
        return new Rectangle(side, side, backgroundColor);
    }
    
    // Method overloading
    resize(factor: number): void;
    resize(width: number, height: number): void;
    resize(widthOrFactor: number, height?: number): void {
        if (height === undefined) {
            // Single parameter - scaling factor
            this.width *= widthOrFactor;
            this.height *= widthOrFactor;
        } else {
            // Two parameters - new dimensions
            this.width = widthOrFactor;
            this.height = height;
        }
    }
}

// Generic class
class GenericContainer<T> implements Container<T> {
    items: T[] = [];
    
    add(item: T): void {
        this.items.push(item);
    }
    
    get(index: number): T | undefined {
        return this.items[index];
    }
    
    size(): number {
        return this.items.length;
    }
    
    // Generic method
    transform<U>(mapper: (item: T) => U): GenericContainer<U> {
        const newContainer = new GenericContainer<U>();
        for (const item of this.items) {
            newContainer.add(mapper(item));
        }
        return newContainer;
    }
    
    // Method with constraints
    filter<K extends keyof T>(property: K, value: T[K]): T[] {
        return this.items.filter(item => item[property] === value);
    }
}

// Function types and signatures
type MathOperation = (a: number, b: number) => number;
type AsyncOperation<T> = (input: T) => Promise<T>;

// Function overloads
function combine(a: string, b: string): string;
function combine(a: number, b: number): number;
function combine(a: any, b: any): any {
    return a + b;
}

// Generic functions
function identity<T>(arg: T): T {
    return arg;
}

function mapArray<T, U>(array: T[], mapper: (item: T) => U): U[] {
    return array.map(mapper);
}

// Function with constraints
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
    return obj[key];
}

// Async/await functions
async function fetchUserData(id: number): Promise<{ id: number; name: string; email: string }> {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 100));
    return {
        id,
        name: `User ${id}`,
        email: `user${id}@example.com`
    };
}

async function processUsers(ids: number[]): Promise<string[]> {
    const users = await Promise.all(ids.map(fetchUserData));
    return users.map(user => user.name);
}

// Higher-order functions
function createValidator<T>(
    predicate: (value: T) => boolean,
    errorMessage: string
): (value: T) => T {
    return (value: T): T => {
        if (!predicate(value)) {
            throw new Error(errorMessage);
        }
        return value;
    };
}

// Decorator factory
function deprecated(message: string) {
    return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
        console.warn(`@deprecated: ${message}`);
        const originalMethod = descriptor.value;
        descriptor.value = function (...args: any[]) {
            console.warn(`Warning: ${propertyName} is deprecated. ${message}`);
            return originalMethod.apply(this, args);
        };
    };
}

// Class with decorators
class Calculator {
    private history: string[] = [];
    
    add(a: number, b: number): number {
        const result = a + b;
        this.history.push(`${a} + ${b} = ${result}`);
        return result;
    }
    
    @deprecated("Use add method instead")
    sum(a: number, b: number): number {
        return this.add(a, b);
    }
    
    getHistory(): readonly string[] {
        return [...this.history];
    }
    
    clear(): void {
        this.history = [];
    }
}

// Utility types usage
type User = {
    id: number;
    name: string;
    email: string;
    age?: number;
};

type CreateUserRequest = Omit<User, 'id'>;
type UserUpdate = Partial<Pick<User, 'name' | 'email' | 'age'>>;
type UserResponse = Required<User>;

// Template literal types
type EventName<T extends string> = `on${Capitalize<T>}`;
type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type ApiEndpoint<T extends string> = `/api/${T}`;

// Class with static members
class MathUtils {
    static readonly PI = Math.PI;
    static readonly E = Math.E;
    
    private static instance: MathUtils;
    
    private constructor() {}
    
    static getInstance(): MathUtils {
        if (!MathUtils.instance) {
            MathUtils.instance = new MathUtils();
        }
        return MathUtils.instance;
    }
    
    static add(a: number, b: number): number {
        return a + b;
    }
    
    static multiply(a: number, b: number): number {
        return a * b;
    }
    
    static factorial(n: number): number {
        if (n <= 1) return 1;
        return n * MathUtils.factorial(n - 1);
    }
    
    // Instance method
    calculateCircleArea(radius: number): number {
        return MathUtils.PI * radius ** 2;
    }
}

// Module augmentation
declare global {
    interface Array<T> {
        chunk(size: number): T[][];
    }
}

Array.prototype.chunk = function<T>(this: T[], size: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < this.length; i += size) {
        chunks.push(this.slice(i, i + size));
    }
    return chunks;
};

// Event system
class EventEmitter<T = Record<string, any>> {
    private listeners: { [K in keyof T]?: EventListener<T[K]>[] } = {};
    
    on<K extends keyof T>(event: K, listener: EventListener<T[K]>): void {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event]!.push(listener);
    }
    
    emit<K extends keyof T>(event: K, data: T[K]): void {
        const eventListeners = this.listeners[event];
        if (eventListeners) {
            eventListeners.forEach(listener => listener(data));
        }
    }
    
    off<K extends keyof T>(event: K, listener: EventListener<T[K]>): void {
        const eventListeners = this.listeners[event];
        if (eventListeners) {
            const index = eventListeners.indexOf(listener);
            if (index > -1) {
                eventListeners.splice(index, 1);
            }
        }
    }
}

// Error handling with custom types
class ValidationError extends Error {
    constructor(
        message: string,
        public field: string,
        public code: string
    ) {
        super(message);
        this.name = 'ValidationError';
    }
}

function validateUser(user: CreateUserRequest): UserResponse {
    if (!user.name || user.name.trim().length === 0) {
        throw new ValidationError('Name is required', 'name', 'REQUIRED');
    }
    
    if (!user.email || !user.email.includes('@')) {
        throw new ValidationError('Valid email is required', 'email', 'INVALID');
    }
    
    return {
        id: Math.floor(Math.random() * 1000),
        ...user,
        age: user.age ?? 0
    };
}

// Main execution
async function main(): Promise<void> {
    console.log('=== TypeScript Test Examples ===');
    
    // Basic types and functions
    console.log('Identity:', identity<string>('Hello TypeScript'));
    console.log('Combine strings:', combine('Hello', ' World'));
    console.log('Combine numbers:', combine(5, 3));
    
    // Classes and inheritance
    const rect = new Rectangle(10, 5, Color.Blue);
    console.log(rect.describe());
    rect.draw();
    rect.resize(2); // Scale by factor
    console.log('After scaling:', rect.describe());
    
    const square = Rectangle.createSquare(7);
    console.log('Square:', square.describe());
    
    // Generic containers
    const stringContainer = new GenericContainer<string>();
    stringContainer.add('Hello');
    stringContainer.add('World');
    
    const numberContainer = stringContainer.transform(str => str.length);
    console.log('String lengths:', numberContainer.items);
    
    // Namespace usage
    const vector = new Geometry.Vector3D(1, 2, 3);
    console.log('Vector magnitude:', vector.magnitude().toFixed(2));
    
    const point1: Point = { x: 0, y: 0 };
    const point2: Point = { x: 3, y: 4 };
    console.log('Distance:', Geometry.distance(point1, point2));
    
    // Enums
    console.log('Direction:', Direction.Up);
    console.log('Response code:', ResponseCode.Success);
    
    // Async operations
    try {
        const userNames = await processUsers([1, 2, 3]);
        console.log('User names:', userNames);
    } catch (error) {
        console.error('Error processing users:', error);
    }
    
    // Calculator with decorators
    const calc = new Calculator();
    console.log('Add result:', calc.add(5, 3));
    console.log('Sum result (deprecated):', calc.sum(10, 15));
    console.log('History:', calc.getHistory());
    
    // Math utilities (singleton)
    const mathUtils = MathUtils.getInstance();
    console.log('Circle area:', mathUtils.calculateCircleArea(5));
    console.log('Factorial of 5:', MathUtils.factorial(5));
    
    // Event system
    type AppEvents = {
        userLogin: { userId: number; timestamp: Date };
        userLogout: { userId: number };
    };
    
    const eventEmitter = new EventEmitter<AppEvents>();
    
    eventEmitter.on('userLogin', (data) => {
        console.log(`User ${data.userId} logged in at ${data.timestamp}`);
    });
    
    eventEmitter.emit('userLogin', {
        userId: 123,
        timestamp: new Date()
    });
    
    // Validation
    try {
        const newUser = validateUser({
            name: 'John Doe',
            email: 'john@example.com',
            age: 30
        });
        console.log('Created user:', newUser);
    } catch (error) {
        if (error instanceof ValidationError) {
            console.error(`Validation error in ${error.field}: ${error.message}`);
        }
    }
    
    // Array extension
    const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9];
    const chunks = numbers.chunk(3);
    console.log('Array chunks:', chunks);
    
    console.log('=== All TypeScript tests completed ===');
}

// Export for module system
export {
    Point,
    Status,
    Shape,
    Drawable,
    Container,
    Geometry,
    Direction,
    ResponseCode,
    Color,
    Rectangle,
    GenericContainer,
    MathUtils,
    EventEmitter,
    ValidationError,
    validateUser,
    combine,
    identity,
    mapArray,
    main
};

// Run main if this is the entry point
if (require.main === module) {
    main().catch(console.error);
}
