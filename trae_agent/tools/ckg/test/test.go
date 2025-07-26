// Go test file with all supported structural elements
package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"reflect"
	"sync"
	"time"
)

// Type aliases
type UserID int
type Username string
type EmailAddress string

// Constants
const (
	AppName       = "TestApp"
	Version       = "1.0.0"
	DefaultPort   = 8080
	MaxRetries    = 3
	TimeoutPeriod = 30 * time.Second
)

// Enums using iota
type Priority int

const (
	Low Priority = iota
	Medium
	High
	Critical
)

type Status int

const (
	StatusPending Status = iota
	StatusRunning
	StatusCompleted
	StatusFailed
)

// Struct types
type User struct {
	ID       UserID       `json:"id"`
	Name     Username     `json:"name"`
	Email    EmailAddress `json:"email"`
	Age      int          `json:"age"`
	IsActive bool         `json:"is_active"`
}

type Point struct {
	X, Y float64
}

type Circle struct {
	Center Point
	Radius float64
	Color  string
}

type Rectangle struct {
	TopLeft     Point
	BottomRight Point
	Color       string
}

// Embedded struct
type Shape struct {
	ID       int
	Name     string
	Created  time.Time
	Metadata map[string]interface{}
}

type ColoredCircle struct {
	Shape  // Embedded struct
	Circle // Embedded struct
}

// Interface definitions
type Drawable interface {
	Draw() string
	Area() float64
}

type Moveable interface {
	Move(dx, dy float64)
	GetPosition() Point
}

// Combined interface
type GraphicsObject interface {
	Drawable
	Moveable
	GetColor() string
	SetColor(color string)
}

// Interface with type constraints (Go 1.18+)
type Numeric interface {
	int | int32 | int64 | float32 | float64
}

// Generic types
type Container[T any] struct {
	items []T
	mu    sync.RWMutex
}

type Result[T any, E error] struct {
	value T
	err   E
}

type Pair[T, U any] struct {
	First  T
	Second U
}

// Methods on structs
func (u *User) String() string {
	return fmt.Sprintf("User{ID: %d, Name: %s, Email: %s, Age: %d}", u.ID, u.Name, u.Email, u.Age)
}

func (u *User) IsAdult() bool {
	return u.Age >= 18
}

func (u *User) UpdateEmail(email EmailAddress) {
	u.Email = email
}

func (u *User) Validate() error {
	if u.Name == "" {
		return errors.New("name cannot be empty")
	}
	if u.Age < 0 {
		return errors.New("age cannot be negative")
	}
	return nil
}

// Point methods
func (p Point) String() string {
	return fmt.Sprintf("Point(%.2f, %.2f)", p.X, p.Y)
}

func (p Point) Distance(other Point) float64 {
	dx := p.X - other.X
	dy := p.Y - other.Y
	return dx*dx + dy*dy // Simplified distance calculation
}

func (p *Point) Move(dx, dy float64) {
	p.X += dx
	p.Y += dy
}

// Circle methods implementing interfaces
func (c Circle) Draw() string {
	return fmt.Sprintf("Drawing %s circle at %v with radius %.2f", c.Color, c.Center, c.Radius)
}

func (c Circle) Area() float64 {
	return 3.14159 * c.Radius * c.Radius
}

func (c *Circle) Move(dx, dy float64) {
	c.Center.Move(dx, dy)
}

func (c Circle) GetPosition() Point {
	return c.Center
}

func (c Circle) GetColor() string {
	return c.Color
}

func (c *Circle) SetColor(color string) {
	c.Color = color
}

// Rectangle methods implementing interfaces
func (r Rectangle) Draw() string {
	return fmt.Sprintf("Drawing %s rectangle from %v to %v", r.Color, r.TopLeft, r.BottomRight)
}

func (r Rectangle) Area() float64 {
	width := r.BottomRight.X - r.TopLeft.X
	height := r.TopLeft.Y - r.BottomRight.Y
	return width * height
}

func (r *Rectangle) Move(dx, dy float64) {
	r.TopLeft.Move(dx, dy)
	r.BottomRight.Move(dx, dy)
}

func (r Rectangle) GetPosition() Point {
	return r.TopLeft
}

func (r Rectangle) GetColor() string {
	return r.Color
}

func (r *Rectangle) SetColor(color string) {
	r.Color = color
}

// Generic container methods
func NewContainer[T any]() *Container[T] {
	return &Container[T]{
		items: make([]T, 0),
	}
}

func (c *Container[T]) Add(item T) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.items = append(c.items, item)
}

func (c *Container[T]) Get(index int) (T, error) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	
	var zero T
	if index < 0 || index >= len(c.items) {
		return zero, errors.New("index out of range")
	}
	return c.items[index], nil
}

func (c *Container[T]) Size() int {
	c.mu.RLock()
	defer c.mu.RUnlock()
	return len(c.items)
}

func (c *Container[T]) Filter(predicate func(T) bool) []T {
	c.mu.RLock()
	defer c.mu.RUnlock()
	
	var result []T
	for _, item := range c.items {
		if predicate(item) {
			result = append(result, item)
		}
	}
	return result
}

// Generic functions
func Max[T Numeric](a, b T) T {
	if a > b {
		return a
	}
	return b
}

func Min[T Numeric](a, b T) T {
	if a < b {
		return a
	}
	return b
}

func Map[T, U any](slice []T, mapper func(T) U) []U {
	result := make([]U, len(slice))
	for i, v := range slice {
		result[i] = mapper(v)
	}
	return result
}

func Filter[T any](slice []T, predicate func(T) bool) []T {
	var result []T
	for _, v := range slice {
		if predicate(v) {
			result = append(result, v)
		}
	}
	return result
}

func Reduce[T, U any](slice []T, initial U, reducer func(U, T) U) U {
	result := initial
	for _, v := range slice {
		result = reducer(result, v)
	}
	return result
}

// Regular functions
func CreateUser(id UserID, name Username, email EmailAddress, age int) *User {
	return &User{
		ID:       id,
		Name:     name,
		Email:    email,
		Age:      age,
		IsActive: true,
	}
}

func ValidateUsers(users []*User) (valid, invalid []*User) {
	for _, user := range users {
		if err := user.Validate(); err == nil {
			valid = append(valid, user)
		} else {
			invalid = append(invalid, user)
		}
	}
	return
}

// Function with variadic parameters
func LogMessage(level string, format string, args ...interface{}) {
	timestamp := time.Now().Format("2006-01-02 15:04:05")
	message := fmt.Sprintf(format, args...)
	fmt.Printf("[%s] %s: %s\n", timestamp, level, message)
}

// Function with multiple return values
func Divide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, errors.New("division by zero")
	}
	return a / b, nil
}

func ProcessData(data []int) (sum, avg float64, count int) {
	count = len(data)
	if count == 0 {
		return
	}
	
	for _, v := range data {
		sum += float64(v)
	}
	avg = sum / float64(count)
	return
}

// Closure functions
func Counter() func() int {
	count := 0
	return func() int {
		count++
		return count
	}
}

func Multiplier(factor int) func(int) int {
	return func(x int) int {
		return x * factor
	}
}

// Channel and goroutine functions
func Worker(jobs <-chan int, results chan<- int) {
	for job := range jobs {
		// Simulate work
		time.Sleep(time.Millisecond * 100)
		results <- job * 2
	}
}

func ProcessConcurrently(data []int, workers int) []int {
	jobs := make(chan int, len(data))
	results := make(chan int, len(data))
	
	// Start workers
	for w := 0; w < workers; w++ {
		go Worker(jobs, results)
	}
	
	// Send jobs
	for _, value := range data {
		jobs <- value
	}
	close(jobs)
	
	// Collect results
	var processed []int
	for i := 0; i < len(data); i++ {
		processed = append(processed, <-results)
	}
	
	return processed
}

// Context-aware function
func ProcessWithTimeout(ctx context.Context, data []int) ([]int, error) {
	resultChan := make(chan []int, 1)
	errorChan := make(chan error, 1)
	
	go func() {
		// Simulate processing
		time.Sleep(time.Second * 2)
		result := make([]int, len(data))
		for i, v := range data {
			result[i] = v * 2
		}
		resultChan <- result
	}()
	
	select {
	case result := <-resultChan:
		return result, nil
	case err := <-errorChan:
		return nil, err
	case <-ctx.Done():
		return nil, ctx.Err()
	}
}

// HTTP handler functions
func HealthCheckHandler(w http.ResponseWriter, r *http.Request) {
	response := map[string]interface{}{
		"status":    "ok",
		"timestamp": time.Now(),
		"version":   Version,
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func UserHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		getUserHandler(w, r)
	case http.MethodPost:
		createUserHandler(w, r)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func getUserHandler(w http.ResponseWriter, r *http.Request) {
	user := CreateUser(1, "Alice", "alice@example.com", 25)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
	var user User
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}
	
	if err := user.Validate(); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(user)
}

// Reflection function
func InspectType(v interface{}) {
	t := reflect.TypeOf(v)
	value := reflect.ValueOf(v)
	
	fmt.Printf("Type: %s\n", t.Name())
	fmt.Printf("Kind: %s\n", t.Kind())
	fmt.Printf("Value: %v\n", value)
	
	if t.Kind() == reflect.Struct {
		fmt.Printf("Fields:\n")
		for i := 0; i < t.NumField(); i++ {
			field := t.Field(i)
			fieldValue := value.Field(i)
			fmt.Printf("  %s: %v (type: %s)\n", field.Name, fieldValue, field.Type)
		}
	}
}

// Main function
func main() {
	LogMessage("INFO", "Starting %s version %s", AppName, Version)
	
	// Test basic types and functions
	user := CreateUser(1, "Alice", "alice@example.com", 25)
	fmt.Printf("Created user: %s\n", user)
	fmt.Printf("Is adult: %t\n", user.IsAdult())
	
	// Test points and shapes
	circle := Circle{
		Center: Point{X: 10, Y: 20},
		Radius: 5,
		Color:  "red",
	}
	
	rectangle := Rectangle{
		TopLeft:     Point{X: 0, Y: 10},
		BottomRight: Point{X: 10, Y: 0},
		Color:       "blue",
	}
	
	// Test interfaces
	var shapes []GraphicsObject = []GraphicsObject{&circle, &rectangle}
	
	for _, shape := range shapes {
		fmt.Printf("%s\n", shape.Draw())
		fmt.Printf("Area: %.2f\n", shape.Area())
		fmt.Printf("Color: %s\n", shape.GetColor())
		
		shape.Move(1, 1)
		fmt.Printf("New position: %v\n", shape.GetPosition())
	}
	
	// Test generics
	container := NewContainer[string]()
	container.Add("hello")
	container.Add("world")
	container.Add("go")
	
	fmt.Printf("Container size: %d\n", container.Size())
	
	filtered := container.Filter(func(s string) bool {
		return len(s) > 2
	})
	fmt.Printf("Filtered items: %v\n", filtered)
	
	// Test generic functions
	numbers := []int{1, 2, 3, 4, 5}
	doubled := Map(numbers, func(x int) int { return x * 2 })
	fmt.Printf("Doubled: %v\n", doubled)
	
	even := Filter(numbers, func(x int) bool { return x%2 == 0 })
	fmt.Printf("Even numbers: %v\n", even)
	
	sum := Reduce(numbers, 0, func(acc, x int) int { return acc + x })
	fmt.Printf("Sum: %d\n", sum)
	
	// Test closures
	counter := Counter()
	fmt.Printf("Counter: %d, %d, %d\n", counter(), counter(), counter())
	
	multiply := Multiplier(3)
	fmt.Printf("Multiply by 3: %d\n", multiply(7))
	
	// Test concurrent processing
	data := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
	processed := ProcessConcurrently(data, 3)
	fmt.Printf("Processed concurrently: %v\n", processed)
	
	// Test context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), time.Second*1)
	defer cancel()
	
	result, err := ProcessWithTimeout(ctx, []int{1, 2, 3})
	if err != nil {
		fmt.Printf("Processing error: %v\n", err)
	} else {
		fmt.Printf("Processing result: %v\n", result)
	}
	
	// Test reflection
	fmt.Println("\nType inspection:")
	InspectType(user)
	
	// Test division with error handling
	if result, err := Divide(10, 2); err != nil {
		fmt.Printf("Division error: %v\n", err)
	} else {
		fmt.Printf("10 / 2 = %.2f\n", result)
	}
	
	if _, err := Divide(10, 0); err != nil {
		fmt.Printf("Division error: %v\n", err)
	}
	
	LogMessage("INFO", "Application completed successfully")
}
