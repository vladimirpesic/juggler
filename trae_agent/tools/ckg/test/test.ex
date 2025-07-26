# Elixir test file with all supported structural elements

# Module with module-level documentation
defmodule TestApp do
  @moduledoc """
  Main application module demonstrating Elixir structural elements.
  """
  
  # Module attributes (constants)
  @app_name "TestApp"
  @version "1.0.0"
  @default_timeout 5000
  
  # Use directives
  use GenServer
  import Enum, only: [map: 2, reduce: 3]
  alias TestApp.Utils
  require Logger
  
  # Module-level function
  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end
  
  # Public function with pattern matching
  def greet(name) when is_binary(name) do
    "Hello, #{name}!"
  end
  
  def greet(_), do: "Hello, stranger!"
  
  # Function with multiple clauses
  def factorial(0), do: 1
  def factorial(n) when n > 0, do: n * factorial(n - 1)
  
  # Private function
  defp format_message(message, prefix \\ "INFO") do
    "[#{prefix}] #{message}"
  end
  
  # Function with guards and pattern matching
  def process_data(data) when is_list(data) and length(data) > 0 do
    data
    |> map(&String.upcase/1)
    |> reduce("", &(&2 <> " " <> &1))
    |> String.trim()
  end
  
  def process_data(_), do: {:error, :invalid_data}
  
  # GenServer callbacks
  @impl true
  def init(opts) do
    state = %{
      name: Keyword.get(opts, :name, @app_name),
      count: 0,
      data: []
    }
    {:ok, state}
  end
  
  @impl true
  def handle_call({:get_count}, _from, state) do
    {:reply, state.count, state}
  end
  
  @impl true
  def handle_call({:increment}, _from, state) do
    new_state = %{state | count: state.count + 1}
    {:reply, new_state.count, new_state}
  end
  
  @impl true
  def handle_cast({:add_data, item}, state) do
    new_data = [item | state.data]
    new_state = %{state | data: new_data}
    {:noreply, new_state}
  end
  
  @impl true
  def handle_info(:timeout, state) do
    Logger.info("Timeout received")
    {:noreply, state}
  end
end

# Protocol definition
defprotocol Drawable do
  @doc "Draws the given shape"
  def draw(shape)
  
  @doc "Gets the area of the shape"
  def area(shape)
end

# Struct definition
defmodule TestApp.Circle do
  @moduledoc "Circle struct and implementation"
  
  defstruct [:radius, :color]
  
  # Constructor function
  def new(radius, color \\ :red) do
    %__MODULE__{radius: radius, color: color}
  end
  
  # Function operating on struct
  def diameter(%__MODULE__{radius: radius}) do
    radius * 2
  end
  
  def circumference(%__MODULE__{radius: radius}) do
    2 * :math.pi() * radius
  end
end

# Protocol implementation
defimpl Drawable, for: TestApp.Circle do
  def draw(%TestApp.Circle{radius: radius, color: color}) do
    "Drawing a #{color} circle with radius #{radius}"
  end
  
  def area(%TestApp.Circle{radius: radius}) do
    :math.pi() * radius * radius
  end
end

# Another struct
defmodule TestApp.Rectangle do
  defstruct [:width, :height, :color]
  
  def new(width, height, color \\ :blue) do
    %__MODULE__{width: width, height: height, color: color}
  end
  
  def perimeter(%__MODULE__{width: w, height: h}) do
    2 * (w + h)
  end
end

# Protocol implementation for Rectangle
defimpl Drawable, for: TestApp.Rectangle do
  def draw(%TestApp.Rectangle{width: w, height: h, color: color}) do
    "Drawing a #{color} rectangle #{w}x#{h}"
  end
  
  def area(%TestApp.Rectangle{width: w, height: h}) do
    w * h
  end
end

# Utility module with various function types
defmodule TestApp.Utils do
  @moduledoc "Utility functions module"
  
  # Function with default parameters
  def create_config(name, timeout \\ 5000, retries \\ 3) do
    %{
      name: name,
      timeout: timeout,
      retries: retries,
      created_at: DateTime.utc_now()
    }
  end
  
  # Higher-order function
  def apply_to_list(list, func) when is_function(func, 1) do
    Enum.map(list, func)
  end
  
  # Function with pattern matching on maps
  def extract_user_info(%{name: name, age: age}) when age >= 18 do
    {:ok, "Adult user: #{name}, age #{age}"}
  end
  
  def extract_user_info(%{name: name, age: age}) do
    {:ok, "Minor user: #{name}, age #{age}"}
  end
  
  def extract_user_info(_) do
    {:error, :invalid_user_data}
  end
  
  # Recursive function
  def sum_list([]), do: 0
  def sum_list([head | tail]), do: head + sum_list(tail)
  
  # Function with case statement
  def categorize_age(age) do
    case age do
      age when age < 13 -> :child
      age when age < 20 -> :teenager
      age when age < 65 -> :adult
      _ -> :senior
    end
  end
  
  # Function using comprehensions
  def generate_squares(n) do
    for x <- 1..n, do: x * x
  end
  
  def filter_and_transform(list) do
    for x <- list, x > 0, do: x * 2
  end
end

# Behaviour definition
defmodule TestApp.Storage do
  @moduledoc "Storage behaviour"
  
  @callback save(key :: String.t(), value :: any()) :: :ok | {:error, term()}
  @callback load(key :: String.t()) :: {:ok, any()} | {:error, :not_found}
  @callback delete(key :: String.t()) :: :ok
end

# Behaviour implementation
defmodule TestApp.MemoryStorage do
  @behaviour TestApp.Storage
  
  use Agent
  
  def start_link(_opts) do
    Agent.start_link(fn -> %{} end, name: __MODULE__)
  end
  
  @impl TestApp.Storage
  def save(key, value) do
    Agent.update(__MODULE__, &Map.put(&1, key, value))
    :ok
  end
  
  @impl TestApp.Storage
  def load(key) do
    case Agent.get(__MODULE__, &Map.get(&1, key)) do
      nil -> {:error, :not_found}
      value -> {:ok, value}
    end
  end
  
  @impl TestApp.Storage
  def delete(key) do
    Agent.update(__MODULE__, &Map.delete(&1, key))
    :ok
  end
end

# GenServer with custom behaviour
defmodule TestApp.Counter do
  use GenServer
  
  # Client API
  def start_link(initial_value \\ 0) do
    GenServer.start_link(__MODULE__, initial_value, name: __MODULE__)
  end
  
  def get do
    GenServer.call(__MODULE__, :get)
  end
  
  def increment(value \\ 1) do
    GenServer.cast(__MODULE__, {:increment, value})
  end
  
  def decrement(value \\ 1) do
    GenServer.cast(__MODULE__, {:decrement, value})
  end
  
  # Server callbacks
  @impl true
  def init(initial_value) do
    {:ok, initial_value}
  end
  
  @impl true
  def handle_call(:get, _from, state) do
    {:reply, state, state}
  end
  
  @impl true
  def handle_cast({:increment, value}, state) do
    {:noreply, state + value}
  end
  
  @impl true
  def handle_cast({:decrement, value}, state) do
    {:noreply, state - value}
  end
end

# Task module with async operations
defmodule TestApp.AsyncOps do
  # Async function using Task
  def fetch_data_async(url) do
    Task.async(fn ->
      # Simulate network delay
      Process.sleep(1000)
      "Data from #{url}"
    end)
  end
  
  def fetch_multiple_urls(urls) do
    urls
    |> Enum.map(&fetch_data_async/1)
    |> Enum.map(&Task.await/1)
  end
  
  # Function using spawn
  def background_work(work_fn) do
    spawn(fn ->
      result = work_fn.()
      IO.puts("Background work completed: #{inspect(result)}")
    end)
  end
end

# Macro-defining module
defmodule TestApp.Macros do
  defmacro debug(expression) do
    quote do
      IO.puts("Debug: #{unquote(Macro.to_string(expression))} = #{inspect(unquote(expression))}")
      unquote(expression)
    end
  end
  
  defmacro unless(condition, do: block) do
    quote do
      if not unquote(condition) do
        unquote(block)
      end
    end
  end
end

# Test module using the macro
defmodule TestApp.MacroUser do
  require TestApp.Macros
  import TestApp.Macros
  
  def test_macros do
    x = 42
    debug(x * 2)
    
    unless x < 0 do
      IO.puts("x is not negative")
    end
  end
end

# Exception module
defmodule TestApp.CustomError do
  defexception [:message, :code]
  
  def exception(opts) do
    message = Keyword.get(opts, :message, "An error occurred")
    code = Keyword.get(opts, :code, :unknown)
    %__MODULE__{message: message, code: code}
  end
end

# Main application supervisor
defmodule TestApp.Supervisor do
  use Supervisor
  
  def start_link(opts) do
    Supervisor.start_link(__MODULE__, opts, name: __MODULE__)
  end
  
  @impl true
  def init(_opts) do
    children = [
      {TestApp, []},
      {TestApp.MemoryStorage, []},
      {TestApp.Counter, [0]}
    ]
    
    Supervisor.init(children, strategy: :one_for_one)
  end
end
