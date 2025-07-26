/**
 * Swift Language Test File
 * Tests all structural elements supported by the Swift parser
 */

// Import statements
import Foundation
import UIKit
import SwiftUI
import Combine
import CoreData

// MARK: - Global Constants and Variables
let globalConstant = "Global constant value"
var globalVariable = 42
private let privateGlobalConstant = 3.14159

// MARK: - Type Aliases
typealias UserID = UUID
typealias Coordinate = (x: Double, y: Double)
typealias CompletionHandler = (Bool, Error?) -> Void
typealias GenericHandler<T> = (T) -> Void

// MARK: - Enums

// Simple enum
enum Direction {
    case north, south, east, west
}

// Enum with associated values
enum Result<T, E: Error> {
    case success(T)
    case failure(E)
    case pending(progress: Double)
    
    var isSuccess: Bool {
        switch self {
        case .success:
            return true
        default:
            return false
        }
    }
}

// Enum with raw values
enum HTTPStatusCode: Int, CaseIterable {
    case ok = 200
    case created = 201
    case badRequest = 400
    case unauthorized = 401
    case notFound = 404
    case internalServerError = 500
    
    var description: String {
        switch self {
        case .ok:
            return "OK"
        case .created:
            return "Created"
        case .badRequest:
            return "Bad Request"
        case .unauthorized:
            return "Unauthorized"
        case .notFound:
            return "Not Found"
        case .internalServerError:
            return "Internal Server Error"
        }
    }
}

// MARK: - Structs

// Basic struct
struct Point {
    let x: Double
    let y: Double
    
    // Computed property
    var magnitude: Double {
        return sqrt(x * x + y * y)
    }
    
    // Mutating method
    mutating func moveBy(dx: Double, dy: Double) {
        self = Point(x: x + dx, y: y + dy)
    }
    
    // Static method
    static func distance(from point1: Point, to point2: Point) -> Double {
        let dx = point1.x - point2.x
        let dy = point1.y - point2.y
        return sqrt(dx * dx + dy * dy)
    }
}

// Generic struct
struct Stack<Element> {
    private var items: [Element] = []
    
    var count: Int {
        return items.count
    }
    
    var isEmpty: Bool {
        return items.isEmpty
    }
    
    mutating func push(_ item: Element) {
        items.append(item)
    }
    
    mutating func pop() -> Element? {
        return isEmpty ? nil : items.removeLast()
    }
    
    func peek() -> Element? {
        return items.last
    }
}

// Struct with property wrappers
struct UserSettings {
    @Published var username: String = ""
    @Published var isNotificationsEnabled: Bool = true
    
    private var _theme: String = "default"
    var theme: String {
        get { _theme }
        set { _theme = newValue }
    }
}

// MARK: - Protocols

// Basic protocol
protocol Drawable {
    var area: Double { get }
    func draw()
    func draw(with color: UIColor)
}

// Protocol with associated types
protocol Container {
    associatedtype Item
    var count: Int { get }
    mutating func append(_ item: Item)
    subscript(index: Int) -> Item { get }
}

// Protocol inheritance
protocol ColoredDrawable: Drawable {
    var color: UIColor { get set }
}

// Protocol with default implementation
extension Drawable {
    func draw() {
        print("Drawing shape with area: \(area)")
    }
}

// MARK: - Classes

// Base class
class Shape: Drawable {
    var name: String
    private(set) var area: Double = 0.0
    
    init(name: String) {
        self.name = name
    }
    
    func draw() {
        print("Drawing \(name)")
    }
    
    func draw(with color: UIColor) {
        print("Drawing \(name) with color: \(color)")
    }
    
    // Class method
    class func defaultShape() -> Shape {
        return Shape(name: "Unknown")
    }
}

// Inheritance
class Rectangle: Shape, ColoredDrawable {
    let width: Double
    let height: Double
    var color: UIColor = .black
    
    init(name: String, width: Double, height: Double) {
        self.width = width
        self.height = height
        super.init(name: name)
        self.area = width * height
    }
    
    override func draw() {
        super.draw()
        print("Rectangle: \(width) x \(height)")
    }
    
    // Convenience initializer
    convenience init(side: Double) {
        self.init(name: "Square", width: side, height: side)
    }
}

// Generic class
class Repository<T: Codable> {
    private var items: [T] = []
    
    func add(_ item: T) {
        items.append(item)
    }
    
    func getAll() -> [T] {
        return items
    }
    
    func get(at index: Int) -> T? {
        guard index >= 0 && index < items.count else { return nil }
        return items[index]
    }
    
    func remove(at index: Int) -> T? {
        guard index >= 0 && index < items.count else { return nil }
        return items.remove(at: index)
    }
}

// MARK: - Actor (Swift 5.5+)
actor Counter {
    private var value = 0
    
    func increment() -> Int {
        value += 1
        return value
    }
    
    func decrement() -> Int {
        value -= 1
        return value
    }
    
    func reset() {
        value = 0
    }
    
    nonisolated func getCurrentValue() -> Int {
        return value
    }
}

// MARK: - Extensions

extension String {
    var isValidEmail: Bool {
        let emailRegex = #"^[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"#
        return range(of: emailRegex, options: .regularExpression) != nil
    }
    
    func truncated(to length: Int) -> String {
        if self.count > length {
            return String(self.prefix(length)) + "..."
        }
        return self
    }
    
    subscript(offset: Int) -> Character? {
        guard offset >= 0 && offset < count else { return nil }
        return self[index(startIndex, offsetBy: offset)]
    }
}

extension Array where Element: Equatable {
    mutating func removeFirst(occurence element: Element) {
        if let index = firstIndex(of: element) {
            remove(at: index)
        }
    }
    
    func chunked(into size: Int) -> [[Element]] {
        return stride(from: 0, to: count, by: size).map {
            Array(self[$0..<Swift.min($0 + size, count)])
        }
    }
}

// Extension with computed properties
extension Rectangle {
    var diagonal: Double {
        return sqrt(width * width + height * height)
    }
    
    var perimeter: Double {
        return 2 * (width + height)
    }
}

// MARK: - Property Wrappers

@propertyWrapper
struct Clamped<T: Comparable> {
    private var value: T
    private let range: ClosedRange<T>
    
    init(initialValue: T, _ range: ClosedRange<T>) {
        self.range = range
        self.value = Swift.min(Swift.max(initialValue, range.lowerBound), range.upperBound)
    }
    
    var wrappedValue: T {
        get { value }
        set { value = Swift.min(Swift.max(newValue, range.lowerBound), range.upperBound) }
    }
}

@propertyWrapper
struct UserDefault<T> {
    let key: String
    let defaultValue: T
    
    var wrappedValue: T {
        get {
            return UserDefaults.standard.object(forKey: key) as? T ?? defaultValue
        }
        set {
            UserDefaults.standard.set(newValue, forKey: key)
        }
    }
}

// MARK: - Function Builders / Result Builders

@resultBuilder
struct HTMLBuilder {
    static func buildBlock(_ components: String...) -> String {
        components.joined()
    }
    
    static func buildIf(_ component: String?) -> String {
        return component ?? ""
    }
    
    static func buildEither(first component: String) -> String {
        return component
    }
    
    static func buildEither(second component: String) -> String {
        return component
    }
}

// MARK: - Functions

// Global functions
func greet(name: String) -> String {
    return "Hello, \(name)!"
}

func greet(name: String, from hometown: String) -> String {
    return "Hello, \(name) from \(hometown)!"
}

// Function with default parameters
func connect(to server: String, port: Int = 80, timeout: TimeInterval = 30.0) -> Bool {
    print("Connecting to \(server):\(port) with timeout \(timeout)s")
    return true
}

// Generic function
func swap<T>(_ a: inout T, _ b: inout T) {
    let temp = a
    a = b
    b = temp
}

// Function with multiple generic constraints
func findCommonElements<T: Sequence, U: Sequence>(_ lhs: T, _ rhs: U) -> [T.Element]
    where T.Element: Equatable, T.Element == U.Element {
    var common: [T.Element] = []
    for lhsItem in lhs {
        for rhsItem in rhs {
            if lhsItem == rhsItem {
                common.append(lhsItem)
            }
        }
    }
    return common
}

// Higher-order function
func performOperation<T>(_ operation: (T, T) -> T, on a: T, and b: T) -> T {
    return operation(a, b)
}

// Function with escaping closure
func fetchData(completion: @escaping (Result<Data, Error>) -> Void) {
    DispatchQueue.global().async {
        // Simulate network request
        Thread.sleep(forTimeInterval: 1.0)
        
        let success = Bool.random()
        if success {
            let data = "Sample data".data(using: .utf8)!
            completion(.success(data))
        } else {
            completion(.failure(NSError(domain: "NetworkError", code: 404, userInfo: nil)))
        }
    }
}

// Async/await function
@available(iOS 15.0, *)
func fetchUserData(userID: UserID) async throws -> UserData {
    let url = URL(string: "https://api.example.com/users/\(userID)")!
    let (data, response) = try await URLSession.shared.data(from: url)
    
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NetworkError.invalidResponse
    }
    
    return try JSONDecoder().decode(UserData.self, from: data)
}

// MARK: - Closures and Higher-Order Functions

let numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

// Closure examples
let evenNumbers = numbers.filter { $0 % 2 == 0 }
let doubledNumbers = numbers.map { $0 * 2 }
let sum = numbers.reduce(0) { $0 + $1 }

// Trailing closure syntax
func processArray<T>(_ array: [T], using processor: (T) -> T) -> [T] {
    return array.map(processor)
}

let processedNumbers = processArray(numbers) { number in
    return number * number
}

// MARK: - Error Handling

enum NetworkError: Error, LocalizedError {
    case noConnection
    case timeout
    case invalidResponse
    case serverError(code: Int)
    
    var errorDescription: String? {
        switch self {
        case .noConnection:
            return "No internet connection"
        case .timeout:
            return "Request timed out"
        case .invalidResponse:
            return "Invalid response from server"
        case .serverError(let code):
            return "Server error with code: \(code)"
        }
    }
}

func performNetworkRequest() throws -> String {
    let success = Bool.random()
    
    guard success else {
        throw NetworkError.noConnection
    }
    
    return "Network request successful"
}

// MARK: - Model Classes

class UserData: Codable, ObservableObject {
    @Published var id: UserID
    @Published var name: String
    @Published var email: String
    @Published var age: Int
    @UserDefault(key: "user_theme", defaultValue: "light") var theme: String
    @Clamped(0, 0...150) var validatedAge: Int
    
    private enum CodingKeys: String, CodingKey {
        case id, name, email, age
    }
    
    init(id: UserID = UUID(), name: String, email: String, age: Int) {
        self.id = id
        self.name = name
        self.email = email
        self.age = age
        self.validatedAge = age
    }
    
    required init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.id = try container.decode(UserID.self, forKey: .id)
        self.name = try container.decode(String.self, forKey: .name)
        self.email = try container.decode(String.self, forKey: .email)
        self.age = try container.decode(Int.self, forKey: .age)
        self.validatedAge = age
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encode(name, forKey: .name)
        try container.encode(email, forKey: .email)  
        try container.encode(age, forKey: .age)
    }
}

// MARK: - SwiftUI Views
@available(iOS 13.0, *)
struct ContentView: View {
    @StateObject private var userData = UserData(name: "John", email: "john@example.com", age: 30)
    @State private var isPresented = false
    @State private var selectedTab = 0
    
    var body: some View {
        NavigationView {
            TabView(selection: $selectedTab) {
                userListView
                    .tabItem {
                        Image(systemName: "person.3")
                        Text("Users")
                    }
                    .tag(0)
                
                settingsView
                    .tabItem {
                        Image(systemName: "gear")
                        Text("Settings")
                    }
                    .tag(1)
            }
            .navigationTitle("Test App")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Add") {
                        isPresented = true
                    }
                }
            }
            .sheet(isPresented: $isPresented) {
                AddUserView()
            }
        }
    }
    
    private var userListView: some View {
        List {
            ForEach(0..<10, id: \.self) { index in
                UserRowView(user: userData)
            }
        }
    }
    
    private var settingsView: some View {
        Form {
            Section("User Settings") {
                TextField("Name", text: $userData.name)
                TextField("Email", text: $userData.email)
                Stepper("Age: \(userData.age)", value: $userData.age, in: 0...150)
            }
            
            Section("App Settings") {
                Picker("Theme", selection: $userData.theme) {
                    Text("Light").tag("light")
                    Text("Dark").tag("dark")
                    Text("Auto").tag("auto")
                }
                .pickerStyle(SegmentedPickerStyle())
            }
        }
    }
}

@available(iOS 13.0, *)
struct UserRowView: View {
    let user: UserData
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(user.name)
                .font(.headline)
            Text(user.email)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 2)
    }
}

@available(iOS 13.0, *)
struct AddUserView: View {
    @Environment(\.presentationMode) var presentationMode
    @State private var name = ""
    @State private var email = ""
    @State private var age = 18
    
    var body: some View {
        NavigationView {
            Form {
                TextField("Name", text: $name)
                TextField("Email", text: $email)
                    .keyboardType(.emailAddress)
                Stepper("Age: \(age)", value: $age, in: 0...150)
            }
            .navigationTitle("Add User")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        presentationMode.wrappedValue.dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        // Save logic here
                        presentationMode.wrappedValue.dismiss()
                    }
                    .disabled(name.isEmpty || email.isEmpty)
                }
            }
        }
    }
}

// MARK: - Main Function and Usage Examples

@main
struct TestApp: App {
    var body: some Scene {
        WindowGroup {
            if #available(iOS 13.0, *) {
                ContentView()
            } else {
                Text("iOS 13.0 or later required")
            }
        }
    }
}

// Example usage
func exampleUsage() {
    // Using structs and classes
    var point = Point(x: 3.0, y: 4.0)
    print("Point magnitude: \(point.magnitude)")
    
    point.moveBy(dx: 1.0, dy: 1.0)
    print("New point: (\(point.x), \(point.y))")
    
    let rectangle = Rectangle(name: "My Rectangle", width: 10.0, height: 5.0)
    rectangle.draw()
    
    // Using generic stack
    var intStack = Stack<Int>()
    intStack.push(1)
    intStack.push(2)
    intStack.push(3)
    
    while !intStack.isEmpty {
        if let item = intStack.pop() {
            print("Popped: \(item)")
        }
    }
    
    // Error handling
    do {
        let result = try performNetworkRequest()
        print("Success: \(result)")
    } catch let error as NetworkError {
        print("Network error: \(error.localizedDescription)")
    } catch {
        print("Unknown error: \(error)")
    }
    
    // Async operations
    fetchData { result in
        switch result {
        case .success(let data):
            print("Received data: \(data)")
        case .failure(let error):
            print("Error: \(error)")
        }
    }
    
    // Using higher-order functions
    let result = performOperation(+, on: 5, and: 3)
    print("Addition result: \(result)")
    
    // Array operations
    let filtered = numbers.filter { $0 > 5 }
    let mapped = filtered.map { $0 * 2 }
    print("Processed numbers: \(mapped)")
}
