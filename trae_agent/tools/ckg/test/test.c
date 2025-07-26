/*
 * C Language Test File
 * Tests all structural elements supported by the C parser
 */

#include <stdio.h>
#include <stdlib.h>

// Global variable
int global_counter = 0;

// Macro definition
#define MAX_SIZE 100
#define MULTIPLY(a, b) ((a) * (b))

// Enum definition
enum Status {
    SUCCESS = 0,
    ERROR = 1,
    PENDING = 2
};

// Struct definition
struct Point {
    int x;
    int y;
};

// Union definition
union Data {
    int integer_value;
    float float_value;
    char string_value[MAX_SIZE];
};

// Typedef
typedef struct Point Point_t;
typedef enum Status Status_t;

// Function prototype
int calculate_distance(Point_t p1, Point_t p2);

// Global function
int add_numbers(int a, int b) {
    return a + b;
}

// Function with nested function calls
int complex_calculation(int x, int y) {
    int temp = add_numbers(x, y);
    
    // Nested function (inner function)
    int multiply_by_two(int value) {
        return value * 2;
    }
    
    return multiply_by_two(temp);
}

// Function using struct
Point_t create_point(int x, int y) {
    Point_t point;
    point.x = x;
    point.y = y;
    return point;
}

// Function using enum
Status_t process_data(int data) {
    if (data < 0) {
        return ERROR;
    } else if (data == 0) {
        return PENDING;
    } else {
        return SUCCESS;
    }
}

// Function using union
void print_data(union Data data, char type) {
    switch (type) {
        case 'i':
            printf("Integer: %d\n", data.integer_value);
            break;
        case 'f':
            printf("Float: %.2f\n", data.float_value);
            break;
        case 's':
            printf("String: %s\n", data.string_value);
            break;
        default:
            printf("Unknown type\n");
    }
}

// Recursive function
int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

// Function with pointer parameters
void swap_integers(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

// Main function
int main(void) {
    Point_t p1 = create_point(3, 4);
    Point_t p2 = create_point(6, 8);
    
    int distance = calculate_distance(p1, p2);
    printf("Distance: %d\n", distance);
    
    Status_t status = process_data(10);
    printf("Status: %d\n", status);
    
    union Data test_data;
    test_data.integer_value = 42;
    print_data(test_data, 'i');
    
    int fact = factorial(5);
    printf("Factorial of 5: %d\n", fact);
    
    int x = 10, y = 20;
    swap_integers(&x, &y);
    printf("Swapped values: x=%d, y=%d\n", x, y);
    
    return 0;
}

// Function implementation after main (allowed in C)
int calculate_distance(Point_t p1, Point_t p2) {
    int dx = p2.x - p1.x;
    int dy = p2.y - p1.y;
    // Simplified distance calculation (not actual Euclidean distance)
    return dx + dy;
}
