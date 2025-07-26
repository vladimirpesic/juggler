//! Zig Language Test File  
//! Tests all structural elements supported by the Zig parser

const std = @import("std");
const print = std.debug.print;
const assert = std.debug.assert;
const ArrayList = std.ArrayList;
const HashMap = std.HashMap;
const Allocator = std.mem.Allocator;
const testing = std.testing;

// =============================================================================
// Global Constants and Variables
// =============================================================================

const PI: f64 = 3.14159265359;
const MAX_BUFFER_SIZE: usize = 1024;
const VERSION: []const u8 = "1.0.0";

var global_counter: u32 = 0;
var global_allocator: Allocator = undefined;

// =============================================================================
// Type Definitions and Aliases
// =============================================================================

// Type aliases
const UserId = u64;
const Timestamp = i64;
const ErrorCode = u8;

// =============================================================================
// Enums
// =============================================================================

// Simple enum
const Direction = enum {
    north,
    south,
    east,
    west,
    
    pub fn opposite(self: Direction) Direction {
        return switch (self) {
            .north => .south,
            .south => .north,
            .east => .west,
            .west => .east,
        };
    }
    
    pub fn isVertical(self: Direction) bool {
        return self == .north or self == .south;
    }
};

// Enum with explicit values
const HttpStatusCode = enum(u16) {
    ok = 200,
    created = 201,
    bad_request = 400,
    unauthorized = 401,
    forbidden = 403,
    not_found = 404,
    internal_server_error = 500,
    
    pub fn isSuccess(self: HttpStatusCode) bool {
        return @intFromEnum(self) >= 200 and @intFromEnum(self) < 300;
    }
    
    pub fn isClientError(self: HttpStatusCode) bool {
        return @intFromEnum(self) >= 400 and @intFromEnum(self) < 500;
    }
    
    pub fn isServerError(self: HttpStatusCode) bool {
        return @intFromEnum(self) >= 500;
    }
};

// Enum with payload (tagged union)
const Result = union(enum) {
    success: []const u8,
    error: ErrorInfo,
    pending: f32, // progress percentage
    
    const ErrorInfo = struct {
        code: ErrorCode,
        message: []const u8,
        details: ?[]const u8 = null,
    };
    
    pub fn isOk(self: Result) bool {
        return switch (self) {
            .success => true,
            else => false,
        };
    }
    
    pub fn unwrap(self: Result) []const u8 {
        return switch (self) {
            .success => |value| value,
            .error => |err| @panic(err.message),
            .pending => @panic("Result is still pending"),
        };
    }
};

// Complex enum with methods
const JsonValue = union(enum) {
    null_value,
    boolean: bool,
    integer: i64,
    float: f64,
    string: []const u8,
    array: []JsonValue,
    object: HashMap([]const u8, JsonValue),
    
    pub fn getType(self: JsonValue) JsonType {
        return switch (self) {
            .null_value => .null_value,
            .boolean => .boolean,
            .integer => .integer,
            .float => .float,
            .string => .string,
            .array => .array,
            .object => .object,
        };
    }
    
    pub fn asString(self: JsonValue) ?[]const u8 {
        return switch (self) {
            .string => |s| s,
            else => null,
        };
    }
    
    pub fn asInteger(self: JsonValue) ?i64 {
        return switch (self) {
            .integer => |i| i,
            else => null,
        };
    }
};

const JsonType = enum {
    null_value,
    boolean,
    integer,
    float,
    string,
    array,
    object,
};

// =============================================================================
// Structs
// =============================================================================

// Basic struct
const Point2D = struct {
    x: f64,
    y: f64,
    
    const Self = @This();
    
    pub fn init(x: f64, y: f64) Self {
        return Self{
            .x = x,
            .y = y,
        };
    }
    
    pub fn distance(self: Self, other: Self) f64 {
        const dx = self.x - other.x;
        const dy = self.y - other.y;
        return @sqrt(dx * dx + dy * dy);
    }
    
    pub fn add(self: Self, other: Self) Self {
        return Self{
            .x = self.x + other.x,
            .y = self.y + other.y,
        };
    }
    
    pub fn scale(self: Self, factor: f64) Self {
        return Self{
            .x = self.x * factor,
            .y = self.y * factor,
        };
    }
    
    pub fn magnitude(self: Self) f64 {
        return @sqrt(self.x * self.x + self.y * self.y);
    }
    
    pub fn normalize(self: Self) Self {
        const mag = self.magnitude();
        if (mag == 0) return self;
        return self.scale(1.0 / mag);
    }
    
    pub fn format(
        self: Self,
        comptime fmt: []const u8,
        options: std.fmt.FormatOptions,
        writer: anytype,
    ) !void {
        _ = fmt;
        _ = options;
        try writer.print("Point2D({d:.2}, {d:.2})", .{ self.x, self.y });
    }
};

// Struct with optional fields and default values
const User = struct {
    id: UserId,
    name: []const u8,
    email: []const u8,
    age: ?u8 = null,
    is_active: bool = true,
    created_at: Timestamp,
    metadata: ?HashMap([]const u8, []const u8) = null,
    
    const Self = @This();
    
    pub fn init(allocator: Allocator, id: UserId, name: []const u8, email: []const u8) !Self {
        return Self{
            .id = id,
            .name = try allocator.dupe(u8, name),
            .email = try allocator.dupe(u8, email),
            .created_at = std.time.timestamp(),
        };
    }
    
    pub fn deinit(self: *Self, allocator: Allocator) void {
        allocator.free(self.name);
        allocator.free(self.email);
        if (self.metadata) |*meta| {
            meta.deinit();
        }
    }
    
    pub fn setAge(self: *Self, age: u8) void {
        self.age = age;
    }
    
    pub fn activate(self: *Self) void {
        self.is_active = true;
    }
    
    pub fn deactivate(self: *Self) void {
        self.is_active = false;
    }
    
    pub fn addMetadata(self: *Self, allocator: Allocator, key: []const u8, value: []const u8) !void {
        if (self.metadata == null) {
            self.metadata = HashMap([]const u8, []const u8).init(allocator);
        }
        try self.metadata.?.put(key, value);
    }
    
    pub fn getMetadata(self: Self, key: []const u8) ?[]const u8 {
        if (self.metadata) |meta| {
            return meta.get(key);
        }
        return null;
    }
    
    pub fn isAdult(self: Self) bool {
        return if (self.age) |age| age >= 18 else false;
    }
};

// Generic struct
fn Vector(comptime T: type) type {
    return struct {
        items: []T,
        capacity: usize,
        allocator: Allocator,
        
        const Self = @This();
        
        pub fn init(allocator: Allocator) Self {
            return Self{
                .items = &[_]T{},
                .capacity = 0,
                .allocator = allocator,
            };
        }
        
        pub fn initCapacity(allocator: Allocator, capacity: usize) !Self {
            return Self{
                .items = try allocator.alloc(T, 0),
                .capacity = capacity,
                .allocator = allocator,
            };
        }
        
        pub fn deinit(self: *Self) void {
            if (self.capacity > 0) {
                self.allocator.free(self.items.ptr[0..self.capacity]);
            }
        }
        
        pub fn append(self: *Self, item: T) !void {
            if (self.items.len >= self.capacity) {
                try self.grow();
            }
            self.items = self.items.ptr[0..self.items.len + 1];
            self.items[self.items.len - 1] = item;
        }
        
        pub fn get(self: Self, index: usize) ?T {
            if (index >= self.items.len) return null;
            return self.items[index];
        }
        
        pub fn len(self: Self) usize {
            return self.items.len;
        }
        
        pub fn isEmpty(self: Self) bool {
            return self.items.len == 0;
        }
        
        fn grow(self: *Self) !void {
            const new_capacity = if (self.capacity == 0) 8 else self.capacity * 2;
            const new_memory = try self.allocator.alloc(T, new_capacity);
            
            if (self.items.len > 0) {
                @memcpy(new_memory[0..self.items.len], self.items);
            }
            
            if (self.capacity > 0) {
                self.allocator.free(self.items.ptr[0..self.capacity]);
            }
            
            self.items = new_memory[0..self.items.len];
            self.capacity = new_capacity;
        }
        
        pub fn contains(self: Self, item: T) bool {
            for (self.items) |existing_item| {
                if (existing_item == item) return true;
            }
            return false;
        }
        
        pub fn clear(self: *Self) void {
            self.items = self.items.ptr[0..0];
        }
    };
}

// Struct with comptime fields
const Config = struct {
    comptime buffer_size: usize = 1024,
    comptime max_connections: u32 = 100,
    
    host: []const u8,
    port: u16,
    debug_mode: bool = false,
    
    const Self = @This();
    
    pub fn init(host: []const u8, port: u16) Self {
        return Self{
            .host = host,
            .port = port,
        };
    }
    
    pub fn getBufferSize(comptime self: Self) usize {
        return self.buffer_size;
    }
    
    pub fn getMaxConnections(comptime self: Self) u32 {
        return self.max_connections;
    }
};

// =============================================================================
// Unions
// =============================================================================

// Tagged union (discriminated union)
const Value = union(enum) {
    none,
    integer: i64,
    float: f64,
    string: []const u8,
    boolean: bool,
    array: []Value,
    
    pub fn getType(self: Value) @TypeOf(self) {
        return switch (self) {
            .none => .none,
            .integer => .integer,
            .float => .float,
            .string => .string,
            .boolean => .boolean,
            .array => .array,
        };
    }
    
    pub fn toString(self: Value, allocator: Allocator) ![]u8 {
        return switch (self) {
            .none => try std.fmt.allocPrint(allocator, "null", .{}),
            .integer => |i| try std.fmt.allocPrint(allocator, "{d}", .{i}),
            .float => |f| try std.fmt.allocPrint(allocator, "{d}", .{f}),
            .string => |s| try allocator.dupe(u8, s),
            .boolean => |b| try std.fmt.allocPrint(allocator, "{}", .{b}),
            .array => |arr| blk: {
                var result = ArrayList(u8).init(allocator);
                try result.append('[');
                for (arr, 0..) |item, i| {
                    if (i > 0) try result.appendSlice(", ");
                    const item_str = try item.toString(allocator);
                    defer allocator.free(item_str);
                    try result.appendSlice(item_str);
                }
                try result.append(']');
                break :blk try result.toOwnedSlice();
            },
        };
    }
};

// Untagged union (C-style union)
const RawValue = union {
    integer: i64,
    float: f64,
    bytes: [8]u8,
    
    pub fn asInteger(self: RawValue) i64 {
        return self.integer;
    }
    
    pub fn asFloat(self: RawValue) f64 {
        return self.float;
    }
    
    pub fn asBytes(self: RawValue) [8]u8 {
        return self.bytes;
    }
};

// =============================================================================
// Error Sets
// =============================================================================

// Simple error set
const FileError = error{
    FileNotFound,
    PermissionDenied,
    DiskFull,
    InvalidPath,
};

// Complex error set
const NetworkError = error{
    ConnectionFailed,
    Timeout,
    InvalidAddress,
    ProtocolError,
} || FileError; // Error set union

const ValidationError = error{
    InvalidEmail,
    InvalidAge,
    MissingField,
    TooLong,
    TooShort,
};

const ApplicationError = NetworkError || ValidationError;

// =============================================================================
// Functions
// =============================================================================

// Simple function
fn add(a: i32, b: i32) i32 {
    return a + b;
}

// Function with error return
fn divide(a: f64, b: f64) !f64 {
    if (b == 0) {
        return error.DivisionByZero;
    }
    return a / b;
}

// Generic function
fn swap(comptime T: type, a: *T, b: *T) void {
    const temp = a.*;
    a.* = b.*;
    b.* = temp;
}

// Function with optional parameters (using struct)
const ConnectOptions = struct {
    timeout: u32 = 5000,
    retries: u8 = 3,
    use_ssl: bool = false,
};

fn connect(host: []const u8, port: u16, options: ConnectOptions) !void {
    print("Connecting to {s}:{d}\n", .{ host, port });
    print("Timeout: {d}ms, Retries: {d}, SSL: {}\n", .{ options.timeout, options.retries, options.use_ssl });
    
    // Simulate connection logic
    if (port == 0) {
        return error.InvalidAddress;
    }
    
    var attempt: u8 = 0;
    while (attempt < options.retries) : (attempt += 1) {
        print("Connection attempt {d}\n", .{attempt + 1});
        // Simulate connection attempt
        break;
    }
}

// Variadic function (using slice)
fn sum(numbers: []const i32) i32 {
    var total: i32 = 0;
    for (numbers) |num| {
        total += num;
    }
    return total;
}

// Function with comptime parameters
fn createArray(comptime T: type, comptime size: usize, initial_value: T) [size]T {
    var array: [size]T = undefined;
    for (&array) |*item| {
        item.* = initial_value;
    }
    return array;
}

// Higher-order function
fn map(comptime T: type, comptime U: type, items: []const T, mapper: fn (T) U, allocator: Allocator) ![]U {
    var result = try allocator.alloc(U, items.len);
    for (items, 0..) |item, i| {
        result[i] = mapper(item);
    }
    return result;
}

fn filter(comptime T: type, items: []const T, predicate: fn (T) bool, allocator: Allocator) ![]T {
    var result = ArrayList(T).init(allocator);
    defer result.deinit();
    
    for (items) |item| {
        if (predicate(item)) {
            try result.append(item);
        }
    }
    
    return try result.toOwnedSlice();
}

// Async function (using async/await)
fn asyncTask(duration_ms: u64) !void {
    print("Starting async task for {d}ms\n", .{duration_ms});
    std.time.sleep(duration_ms * std.time.ns_per_ms);
    print("Async task completed\n");
}

// Function with closure-like behavior using struct
fn createCounter(initial: i32) type {
    return struct {
        value: i32,
        
        const Self = @This();
        
        pub fn init(start: i32) Self {
            return Self{ .value = start };
        }
        
        pub fn increment(self: *Self) i32 {
            self.value += 1;
            return self.value;
        }
        
        pub fn decrement(self: *Self) i32 {
            self.value -= 1;
            return self.value;
        }
        
        pub fn get(self: Self) i32 {
            return self.value;
        }
        
        pub fn reset(self: *Self, new_value: i32) void {
            self.value = new_value;
        }
    };
}

// =============================================================================
// Interfaces (using anytype and function pointers)
// =============================================================================

// Interface-like behavior using anytype
fn processDrawable(drawable: anytype) void {
    drawable.draw();
    print("Area: {d}\n", .{drawable.area()});
}

// Function pointer type for callbacks
const EventCallback = *const fn (event_type: []const u8, data: ?*anyopaque) void;

const EventSystem = struct {
    callbacks: ArrayList(EventCallback),
    allocator: Allocator,
    
    const Self = @This();
    
    pub fn init(allocator: Allocator) Self {
        return Self{
            .callbacks = ArrayList(EventCallback).init(allocator),
            .allocator = allocator,
        };
    }
    
    pub fn deinit(self: *Self) void {
        self.callbacks.deinit();
    }
    
    pub fn subscribe(self: *Self, callback: EventCallback) !void {
        try self.callbacks.append(callback);
    }
    
    pub fn emit(self: Self, event_type: []const u8, data: ?*anyopaque) void {
        for (self.callbacks.items) |callback| {
            callback(event_type, data);
        }
    }
};

// =============================================================================
// Tests
// =============================================================================

test "Point2D operations" {
    const p1 = Point2D.init(3.0, 4.0);
    const p2 = Point2D.init(1.0, 1.0);
    
    try testing.expectEqual(@as(f64, 5.0), p1.magnitude());
    try testing.expectEqual(@as(f64, @sqrt(13.0)), p1.distance(p2));
    
    const p3 = p1.add(p2);
    try testing.expectEqual(@as(f64, 4.0), p3.x);
    try testing.expectEqual(@as(f64, 5.0), p3.y);
}

test "Vector generic type" {
    var vector = Vector(i32).init(testing.allocator);
    defer vector.deinit();
    
    try vector.append(1);
    try vector.append(2);
    try vector.append(3);
    
    try testing.expectEqual(@as(usize, 3), vector.len());
    try testing.expectEqual(@as(?i32, 2), vector.get(1));
    try testing.expect(vector.contains(3));
    try testing.expect(!vector.contains(5));
}

test "Result union type" {
    const success_result = Result{ .success = "All good!" };
    const error_result = Result{ 
        .error = .{ 
            .code = 404, 
            .message = "Not found",
            .details = "The requested resource was not found",
        }
    };
    
    try testing.expect(success_result.isOk());
    try testing.expect(!error_result.isOk());
    
    const success_value = success_result.unwrap();
    try testing.expectEqualStrings("All good!", success_value);
}

test "User struct with metadata" {
    var user = try User.init(testing.allocator, 123, "John Doe", "john@example.com");
    defer user.deinit(testing.allocator);
    
    user.setAge(25);
    try testing.expect(user.isAdult());
    
    try user.addMetadata(testing.allocator, "department", "Engineering");
    const dept = user.getMetadata("department");
    try testing.expectEqualStrings("Engineering", dept.?);
}

test "Error handling" {
    const result = divide(10.0, 2.0);
    try testing.expectEqual(@as(f64, 5.0), try result);
    
    const error_result = divide(10.0, 0.0);
    try testing.expectError(error.DivisionByZero, error_result);
}

test "Higher-order functions" {
    const numbers = [_]i32{ 1, 2, 3, 4, 5 };
    
    const doubled = try map(i32, i32, &numbers, struct {
        fn double(x: i32) i32 {
            return x * 2;
        }
    }.double, testing.allocator);
    defer testing.allocator.free(doubled);
    
    try testing.expectEqual(@as(i32, 2), doubled[0]);
    try testing.expectEqual(@as(i32, 10), doubled[4]);
    
    const evens = try filter(i32, &numbers, struct {
        fn isEven(x: i32) bool {
            return x % 2 == 0;
        }
    }.isEven, testing.allocator);
    defer testing.allocator.free(evens);
    
    try testing.expectEqual(@as(usize, 2), evens.len);
    try testing.expectEqual(@as(i32, 2), evens[0]);
    try testing.expectEqual(@as(i32, 4), evens[1]);
}

test "Counter factory" {
    const Counter = createCounter(0);
    var counter = Counter.init(10);
    
    try testing.expectEqual(@as(i32, 10), counter.get());
    try testing.expectEqual(@as(i32, 11), counter.increment());
    try testing.expectEqual(@as(i32, 10), counter.decrement());
    
    counter.reset(5);
    try testing.expectEqual(@as(i32, 5), counter.get());
}

// =============================================================================
// Main Function and Usage Examples
// =============================================================================

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    
    print("=== Zig Language Test ===\n\n");
    
    // Basic operations
    print("1. Basic Operations:\n");
    const result = add(5, 3);
    print("   5 + 3 = {d}\n", .{result});
    
    const division_result = divide(10.0, 3.0) catch |err| {
        print("   Division error: {}\n", .{err});
        return;
    };
    print("   10.0 / 3.0 = {d:.2}\n", .{division_result});
    
    // Point operations
    print("\n2. Point Operations:\n");
    const p1 = Point2D.init(3.0, 4.0);
    const p2 = Point2D.init(1.0, 2.0);
    print("   p1 = {}\n", .{p1});
    print("   p2 = {}\n", .{p2});
    print("   Distance: {d:.2}\n", .{p1.distance(p2)});
    print("   Sum: {}\n", .{p1.add(p2)});
    
    // User management
    print("\n3. User Management:\n");
    var user = try User.init(allocator, 1001, "Alice Smith", "alice@example.com");
    defer user.deinit(allocator);
    
    user.setAge(28);
    try user.addMetadata(allocator, "role", "developer");
    try user.addMetadata(allocator, "team", "backend");
    
    print("   User: {s} ({s})\n", .{ user.name, user.email });
    print("   Age: {?d}\n", .{user.age});
    print("   Is Adult: {}\n", .{user.isAdult()});
    print("   Role: {?s}\n", .{user.getMetadata("role")});
    
    // Vector operations
    print("\n4. Vector Operations:\n");
    var int_vector = Vector(i32).init(allocator);
    defer int_vector.deinit();
    
    try int_vector.append(10);
    try int_vector.append(20);
    try int_vector.append(30);
    
    print("   Vector length: {d}\n", .{int_vector.len()});
    print("   Contains 20: {}\n", .{int_vector.contains(20)});
    print("   Item at index 1: {?d}\n", .{int_vector.get(1)});
    
    // Enum operations
    print("\n5. Enum Operations:\n");
    const direction = Direction.north;
    print("   Direction: {}\n", .{direction});
    print("   Opposite: {}\n", .{direction.opposite()});
    print("   Is Vertical: {}\n", .{direction.isVertical()});
    
    const status = HttpStatusCode.ok;
    print("   HTTP Status: {} ({})\n", .{ status, @intFromEnum(status) });
    print("   Is Success: {}\n", .{status.isSuccess()});
    
    // Result handling
    print("\n6. Result Handling:\n");
    const success_result = Result{ .success = "Operation completed successfully" };
    const error_result = Result{ 
        .error = .{ 
            .code = 500, 
            .message = "Internal server error",
            .details = "Database connection failed",
        }
    };
    
    print("   Success result OK: {}\n", .{success_result.isOk()});
    print("   Error result OK: {}\n", .{error_result.isOk()});
    
    if (success_result.isOk()) {
        print("   Success value: {s}\n", .{success_result.unwrap()});
    }
    
    // Value union
    print("\n7. Value Union:\n");
    const values = [_]Value{
        .{ .integer = 42 },
        .{ .float = 3.14 },
        .{ .string = "Hello, Zig!" },
        .{ .boolean = true },
        .none,
    };
    
    for (values, 0..) |value, i| {
        const str = try value.toString(allocator);
        defer allocator.free(str);
        print("   Value {d}: {s}\n", .{ i, str });
    }
    
    // Function pointers and callbacks
    print("\n8. Event System:\n");
    var event_system = EventSystem.init(allocator);
    defer event_system.deinit();
    
    const callback = struct {
        fn handleEvent(event_type: []const u8, data: ?*anyopaque) void {
            _ = data;
            print("   Event received: {s}\n", .{event_type});
        }
    }.handleEvent;
    
    try event_system.subscribe(callback);
    event_system.emit("user.login", null);
    event_system.emit("user.logout", null);
    
    // Counter factory pattern
    print("\n9. Counter Factory:\n");
    const Counter = createCounter(0);
    var counter = Counter.init(0);
    
    print("   Initial: {d}\n", .{counter.get()});
    print("   After increment: {d}\n", .{counter.increment()});
    print("   After increment: {d}\n", .{counter.increment()});
    print("   After decrement: {d}\n", .{counter.decrement()});
    
    // Array creation with comptime
    print("\n10. Comptime Array Creation:\n");
    const int_array = createArray(i32, 5, 42);
    print("   Array: ");
    for (int_array, 0..) |item, i| {
        if (i > 0) print(", ");
        print("{d}", .{item});
    }
    print("\n");
    
    // Configuration
    print("\n11. Configuration:\n");
    const config = Config.init("localhost", 8080);
    print("   Host: {s}:{d}\n", .{ config.host, config.port });
    print("   Buffer size: {d}\n", .{config.getBufferSize()});
    print("   Max connections: {d}\n", .{config.getMaxConnections()});
    
    // Connection with options
    print("\n12. Connection Test:\n");
    try connect("example.com", 443, .{ 
        .timeout = 10000, 
        .retries = 5, 
        .use_ssl = true 
    });
    
    print("\n=== Test completed successfully! ===\n");
}
