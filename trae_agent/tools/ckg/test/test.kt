package com.example.test

// Kotlin test file with all supported structural elements

// Top-level constants
const val APP_NAME = "KotlinTestApp"
const val VERSION = "1.0.0"

// Type aliases
typealias UserId = Int
typealias UserName = String
typealias EmailAddress = String

// Enum classes
enum class Color(val rgb: Int) {
    RED(0xFF0000),
    GREEN(0x00FF00),
    BLUE(0x0000FF);
    
    fun toHex(): String = "#${rgb.toString(16).padStart(6, '0')}"
    
    companion object {
        fun fromRgb(rgb: Int): Color? = values().find { it.rgb == rgb }
    }
}

enum class Priority {
    LOW, MEDIUM, HIGH, CRITICAL;
    
    fun isHigherThan(other: Priority) = ordinal > other.ordinal
}

// Sealed classes (algebraic data types)
sealed class Result<out T, out E> {
    data class Success<out T>(val value: T) : Result<T, Nothing>()
    data class Error<out E>(val error: E) : Result<Nothing, E>()
    
    fun <R> map(transform: (T) -> R): Result<R, E> = when (this) {
        is Success -> Success(transform(value))
        is Error -> this
    }
    
    fun <R> flatMap(transform: (T) -> Result<R, E>): Result<R, E> = when (this) {
        is Success -> transform(value)
        is Error -> this
    }
}

sealed class Shape {
    abstract fun area(): Double
    abstract fun perimeter(): Double
    
    data class Circle(val radius: Double) : Shape() {
        override fun area() = kotlin.math.PI * radius * radius
        override fun perimeter() = 2 * kotlin.math.PI * radius
    }
    
    data class Rectangle(val width: Double, val height: Double) : Shape() {
        override fun area() = width * height
        override fun perimeter() = 2 * (width + height)
    }
    
    data class Triangle(val a: Double, val b: Double, val c: Double) : Shape() {
        override fun area(): Double {
            val s = (a + b + c) / 2
            return kotlin.math.sqrt(s * (s - a) * (s - b) * (s - c))
        }
        override fun perimeter() = a + b + c
    }
}

// Data classes
data class User(
    val id: UserId,
    val name: UserName,
    val email: EmailAddress,
    val age: Int,
    val isActive: Boolean = true
) {
    fun isAdult() = age >= 18
    
    fun validate(): Result<Unit, String> = when {
        name.isBlank() -> Result.Error("Name cannot be blank")
        age < 0 -> Result.Error("Age cannot be negative")
        !email.contains("@") -> Result.Error("Invalid email format")
        else -> Result.Success(Unit)
    }
}

data class Point(val x: Double, val y: Double) {
    operator fun plus(other: Point) = Point(x + other.x, y + other.y)
    operator fun minus(other: Point) = Point(x - other.x, y - other.y)
    operator fun times(scalar: Double) = Point(x * scalar, y * scalar)
    
    fun distanceTo(other: Point): Double {
        val dx = x - other.x
        val dy = y - other.y
        return kotlin.math.sqrt(dx * dx + dy * dy)
    }
    
    companion object {
        val ORIGIN = Point(0.0, 0.0)
        fun fromPolar(radius: Double, angle: Double) = Point(
            radius * kotlin.math.cos(angle),
            radius * kotlin.math.sin(angle)
        )
    }
}

// Interfaces
interface Drawable {
    fun draw(): String
    fun getColor(): Color
    fun setColor(color: Color)
}

interface Moveable {
    fun move(dx: Double, dy: Double)
    fun getPosition(): Point
}

interface Scalable {
    fun scale(factor: Double)
}

// Abstract classes
abstract class GameObject(
    protected var position: Point,
    protected var color: Color
) : Drawable, Moveable {
    
    abstract val name: String
    
    override fun move(dx: Double, dy: Double) {
        position += Point(dx, dy)
    }
    
    override fun getPosition() = position
    
    override fun getColor() = color
    
    override fun setColor(color: Color) {
        this.color = color
    }
    
    abstract fun update(deltaTime: Double)
}

// Concrete implementations
class GameCircle(
    position: Point,
    color: Color,
    private var radius: Double
) : GameObject(position, color), Scalable {
    
    override val name = "Circle"
    
    override fun draw(): String = 
        "Drawing ${color.name.lowercase()} circle at $position with radius $radius"
    
    override fun scale(factor: Double) {
        radius *= factor
    }
    
    override fun update(deltaTime: Double) {
        // Simple animation - oscillate size
        radius += kotlin.math.sin(System.currentTimeMillis() / 1000.0) * 0.1
    }
    
    fun getRadius() = radius
    fun area() = kotlin.math.PI * radius * radius
}

class GameRectangle(
    position: Point,
    color: Color,
    private var width: Double,
    private var height: Double
) : GameObject(position, color), Scalable {
    
    override val name = "Rectangle"
    
    override fun draw(): String = 
        "Drawing ${color.name.lowercase()} rectangle at $position (${width}x${height})"
    
    override fun scale(factor: Double) {
        width *= factor
        height *= factor
    }
    
    override fun update(deltaTime: Double) {
        // Simple rotation effect
        val time = System.currentTimeMillis() / 1000.0
        width = kotlin.math.abs(kotlin.math.cos(time)) * 10 + 5
        height = kotlin.math.abs(kotlin.math.sin(time)) * 10 + 5
    }
    
    fun getDimensions() = Pair(width, height)
    fun area() = width * height
}

// Generic classes
class Container<T> {
    private val items = mutableListOf<T>()
    
    fun add(item: T) = items.add(item)
    
    fun remove(item: T) = items.remove(item)
    
    fun get(index: Int): T? = items.getOrNull(index)
    
    fun size() = items.size
    
    fun isEmpty() = items.isEmpty()
    
    fun filter(predicate: (T) -> Boolean) = items.filter(predicate)
    
    fun <R> map(transform: (T) -> R) = items.map(transform)
    
    fun forEach(action: (T) -> Unit) = items.forEach(action)
    
    fun find(predicate: (T) -> Boolean) = items.find(predicate)
    
    fun toList(): List<T> = items.toList()
}

// Generic functions
inline fun <T> T.applyIf(condition: Boolean, block: T.() -> T): T = 
    if (condition) block() else this

inline fun <T, R> T.runCatching(block: T.() -> R): Result<R, Exception> = try {
    Result.Success(block())
} catch (e: Exception) {
    Result.Error(e)
}

fun <T> List<T>.second(): T = this[1]
fun <T> List<T>.secondOrNull(): T? = getOrNull(1)

// Extension functions
fun String.isValidEmail(): Boolean = 
    contains("@") && contains(".") && length > 5

fun String.capitalize(): String = 
    replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }

fun Int.factorial(): Long = 
    if (this <= 1) 1 else this * (this - 1).factorial()

fun Double.toDegrees() = this * 180.0 / kotlin.math.PI
fun Double.toRadians() = this * kotlin.math.PI / 180.0

// Extension properties
val String.wordCount: Int
    get() = split("\\s+".toRegex()).size

val List<Int>.average: Double
    get() = sum().toDouble() / size

// Object declarations (singletons)
object MathUtils {
    const val PI = kotlin.math.PI
    const val E = kotlin.math.E
    
    fun gcd(a: Int, b: Int): Int = if (b == 0) a else gcd(b, a % b)
    
    fun lcm(a: Int, b: Int): Int = a * b / gcd(a, b)
    
    fun isPrime(n: Int): Boolean {
        if (n < 2) return false
        for (i in 2..kotlin.math.sqrt(n.toDouble()).toInt()) {
            if (n % i == 0) return false
        }
        return true
    }
    
    fun fibonacci(n: Int): Long = when (n) {
        0 -> 0
        1 -> 1
        else -> fibonacci(n - 1) + fibonacci(n - 2)
    }
}

object StringUtils {
    fun reverse(str: String): String = str.reversed()
    
    fun isPalindrome(str: String): Boolean {
        val cleaned = str.replace("\\s+".toRegex(), "").lowercase()
        return cleaned == cleaned.reversed()
    }
    
    fun countOccurrences(text: String, substring: String): Int {
        var count = 0
        var index = 0
        while (text.indexOf(substring, index).also { index = it } != -1) {
            count++
            index += substring.length
        }
        return count
    }
}

// Class with companion object
class UserManager {
    private val users = mutableMapOf<UserId, User>()
    
    fun addUser(user: User): Result<Unit, String> {
        return when (val validation = user.validate()) {
            is Result.Success -> {
                users[user.id] = user
                Result.Success(Unit)
            }
            is Result.Error -> validation
        }
    }
    
    fun getUser(id: UserId): User? = users[id]
    
    fun getAllUsers(): List<User> = users.values.toList()
    
    fun removeUser(id: UserId): Boolean = users.remove(id) != null
    
    fun updateUser(id: UserId, updater: (User) -> User): Result<Unit, String> {
        val user = users[id] ?: return Result.Error("User not found")
        val updatedUser = updater(user)
        return when (val validation = updatedUser.validate()) {
            is Result.Success -> {
                users[id] = updatedUser
                Result.Success(Unit)
            }
            is Result.Error -> validation
        }
    }
    
    companion object {
        const val MAX_USERS = 10000
        
        fun createDefaultUser(id: UserId): User = User(
            id = id,
            name = "User$id",
            email = "user$id@example.com",
            age = 25
        )
        
        fun validateId(id: UserId): Boolean = id > 0
    }
}

// Higher-order functions
fun <T> measureTime(block: () -> T): Pair<T, Long> {
    val startTime = System.currentTimeMillis()
    val result = block()
    val endTime = System.currentTimeMillis()
    return Pair(result, endTime - startTime)
}

fun retry(times: Int, delay: Long = 1000, block: () -> Unit): Boolean {
    repeat(times) { attempt ->
        try {
            block()
            return true
        } catch (e: Exception) {
            if (attempt == times - 1) return false
            Thread.sleep(delay)
        }
    }
    return false
}

inline fun <T> List<T>.partitionBy(predicate: (T) -> Boolean): Pair<List<T>, List<T>> = 
    partition(predicate)

// Lambda expressions and function types
val add: (Int, Int) -> Int = { a, b -> a + b }
val multiply = { a: Int, b: Int -> a * b }
val isEven: (Int) -> Boolean = { it % 2 == 0 }

// Function with receiver
fun StringBuilder.appendLineIf(condition: Boolean, text: String): StringBuilder = 
    if (condition) appendLine(text) else this

// Inline functions
inline fun <T> T.also(block: (T) -> Unit): T {
    block(this)
    return this
}

inline fun <T, R> T.let(block: (T) -> R): R = block(this)

// Main function
fun main() {
    println("Starting $APP_NAME version $VERSION")
    
    // Test enums
    val color = Color.RED
    println("Color: ${color.name}, RGB: ${color.toHex()}")
    
    val priority = Priority.HIGH
    println("Priority is higher than MEDIUM: ${priority.isHigherThan(Priority.MEDIUM)}")
    
    // Test data classes and operators
    val p1 = Point(3.0, 4.0)
    val p2 = Point(1.0, 2.0)
    val sum = p1 + p2
    println("Point sum: $sum")
    println("Distance: ${p1.distanceTo(p2)}")
    
    // Test shapes
    val shapes = listOf(
        Shape.Circle(5.0),
        Shape.Rectangle(4.0, 3.0),
        Shape.Triangle(3.0, 4.0, 5.0)
    )
    
    shapes.forEach { shape ->
        println("${shape::class.simpleName}: area=${shape.area()}, perimeter=${shape.perimeter()}")
    }
    
    // Test game objects
    val gameObjects = listOf(
        GameCircle(Point(10.0, 10.0), Color.BLUE, 5.0),
        GameRectangle(Point(20.0, 20.0), Color.GREEN, 8.0, 6.0)
    )
    
    gameObjects.forEach { obj ->
        println(obj.draw())
        obj.move(1.0, 1.0)
        obj.scale(1.1)
        obj.update(0.16)
    }
    
    // Test generics
    val stringContainer = Container<String>()
    stringContainer.add("Hello")
    stringContainer.add("World")
    stringContainer.add("Kotlin")
    
    val longStrings = stringContainer.filter { it.length > 5 }
    println("Long strings: $longStrings")
    
    val upperCased = stringContainer.map { it.uppercase() }
    println("Uppercase: $upperCased")
    
    // Test user management
    val userManager = UserManager()
    val user1 = User(1, "Alice", "alice@example.com", 25)
    val user2 = User(2, "Bob", "bob@example.com", 30)
    
    when (userManager.addUser(user1)) {
        is Result.Success -> println("User added successfully")
        is Result.Error -> println("Error adding user: ${user1}")
    }
    
    userManager.addUser(user2)
    
    println("All users: ${userManager.getAllUsers()}")
    
    // Test extension functions
    val email = "test@example.com"
    println("Is valid email: ${email.isValidEmail()}")
    
    val number = 5
    println("$number! = ${number.factorial()}")
    
    val text = "Hello world Kotlin programming"
    println("Word count: ${text.wordCount}")
    
    // Test utilities
    println("GCD(48, 18) = ${MathUtils.gcd(48, 18)}")
    println("Is 17 prime: ${MathUtils.isPrime(17)}")
    println("Fibonacci(10) = ${MathUtils.fibonacci(10)}")
    
    println("Is 'racecar' a palindrome: ${StringUtils.isPalindrome("racecar")}")
    
    // Test higher-order functions
    val (result, time) = measureTime {
        (1..1000).map { it * it }.sum()
    }
    println("Sum of squares 1-1000: $result (took ${time}ms)")
    
    // Test lambdas
    val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    val evenNumbers = numbers.filter(isEven)
    println("Even numbers: $evenNumbers")
    
    val sum2 = numbers.fold(0, add)
    println("Sum using fold: $sum2")
    
    // Test Result monad
    val divisionResult = Result.Success(10.0)
        .flatMap { if (it != 0.0) Result.Success(100.0 / it) else Result.Error("Division by zero") }
        .map { "Result: $it" }
    
    when (divisionResult) {
        is Result.Success -> println(divisionResult.value)
        is Result.Error -> println("Error: ${divisionResult.error}")
    }
    
    println("$APP_NAME completed successfully!")
}
