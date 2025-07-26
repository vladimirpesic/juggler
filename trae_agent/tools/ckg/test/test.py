#!/usr/bin/env python3
"""
Comprehensive Python test file containing all supported structural elements.
This file demonstrates functions, classes, and modules.
"""

import os
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass


# Module-level function
def global_function(param1: str, param2: int = 10) -> str:
    """A global function with parameters and return type annotation."""
    def nested_function(x: int) -> int:
        """A function nested within another function."""
        return x * 2
    
    result = nested_function(param2)
    return f"{param1}: {result}"


# Class definition with various elements
class BaseClass:
    """A base class with various structural elements."""
    
    # Class variables
    class_var = "base_class_value"
    _private_var = 42
    
    def __init__(self, name: str, value: int):
        """Constructor method."""
        self.name = name
        self.value = value
        self._protected_attr = None
    
    def public_method(self, arg: str) -> str:
        """A public method."""
        return f"{self.name}: {arg}"
    
    def _protected_method(self) -> int:
        """A protected method (by convention)."""
        return self.value
    
    def __private_method(self) -> None:
        """A private method (by convention)."""
        pass
    
    @staticmethod
    def static_method(x: int, y: int) -> int:
        """A static method."""
        return x + y
    
    @classmethod
    def class_method(cls, param: str) -> "BaseClass":
        """A class method."""
        return cls(param, 0)
    
    @property
    def computed_property(self) -> str:
        """A computed property."""
        return f"computed_{self.name}"
    
    @computed_property.setter
    def computed_property(self, value: str) -> None:
        """Property setter."""
        self.name = value.replace("computed_", "")


class DerivedClass(BaseClass):
    """A derived class demonstrating inheritance."""
    
    def __init__(self, name: str, value: int, extra: str):
        super().__init__(name, value)
        self.extra_attr = extra
    
    def public_method(self, arg: str) -> str:
        """Overridden method."""
        return f"Derived {super().public_method(arg)}"
    
    def derived_only_method(self) -> str:
        """Method specific to derived class."""
        return self.extra_attr


# Generic class (demonstrated through typing)
@dataclass
class GenericContainer:
    """A generic-like container using dataclass."""
    items: List[str]
    metadata: Dict[str, int]
    optional_data: Optional[str] = None
    
    def add_item(self, item: str) -> None:
        """Add an item to the container."""
        self.items.append(item)
    
    def get_count(self) -> int:
        """Get the count of items."""
        return len(self.items)


# Abstract-like class (Python doesn't have true abstract classes without ABC)
class AbstractLikeClass:
    """Abstract-like class with methods meant to be overridden."""
    
    def template_method(self) -> str:
        """Template method calling abstract methods."""
        return f"{self.abstract_method()}: {self.another_abstract_method()}"
    
    def abstract_method(self) -> str:
        """Method meant to be overridden in subclasses."""
        raise NotImplementedError("Subclasses must implement this method")
    
    def another_abstract_method(self) -> str:
        """Another method meant to be overridden."""
        raise NotImplementedError("Subclasses must implement this method")


# Nested class
class OuterClass:
    """Class containing nested classes."""
    
    class NestedClass:
        """A nested class."""
        
        def __init__(self, data: str):
            self.data = data
        
        def nested_method(self) -> str:
            """Method in nested class."""
            return f"nested: {self.data}"
        
        class DeepNestedClass:
            """Deeply nested class."""
            
            def deep_method(self) -> str:
                """Method in deeply nested class."""
                return "deep nested"
    
    def outer_method(self) -> str:
        """Method in outer class."""
        return "outer method"


# Multiple inheritance
class MixinA:
    """First mixin class."""
    
    def mixin_a_method(self) -> str:
        """Method from mixin A."""
        return "mixin A"


class MixinB:
    """Second mixin class."""
    
    def mixin_b_method(self) -> str:  
        """Method from mixin B."""
        return "mixin B"


class MultipleInheritanceClass(MixinA, MixinB, BaseClass):
    """Class demonstrating multiple inheritance."""
    
    def __init__(self, name: str):
        BaseClass.__init__(self, name, 100)
    
    def combined_method(self) -> str:
        """Method using multiple inheritance."""
        return f"{self.mixin_a_method()} + {self.mixin_b_method()} + {self.public_method('test')}"


# Decorator examples
def decorator_function(func):
    """A decorator function."""
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


@decorator_function
def decorated_function(x: int) -> int:
    """A function with a decorator."""
    return x * x


# Lambda and higher-order functions
filter_even = lambda x: x % 2 == 0
map_square = lambda x: x * x

def higher_order_function(func, data: List[int]) -> List[int]:
    """Function that takes another function as parameter."""
    return list(map(func, data))


# Generator function
def fibonacci_generator(n: int):
    """Generator function for Fibonacci sequence."""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


# Async function (modern Python feature)
async def async_function(delay: float) -> str:
    """An async function."""
    import asyncio
    await asyncio.sleep(delay)
    return "async result"


# Context manager class
class CustomContextManager:
    """Custom context manager."""
    
    def __init__(self, resource_name: str):
        self.resource_name = resource_name
    
    def __enter__(self):
        """Enter context."""
        print(f"Acquiring {self.resource_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        print(f"Releasing {self.resource_name}")
        return False


# Main execution block
if __name__ == "__main__":
    # Test code execution
    print(global_function("test", 5))
    
    base = BaseClass("base", 10)
    print(base.public_method("hello"))
    
    derived = DerivedClass("derived", 20, "extra")
    print(derived.derived_only_method())
    
    container = GenericContainer(["item1", "item2"], {"count": 2})
    container.add_item("item3")
    print(f"Container has {container.get_count()} items")
    
    # Test generator
    fib = list(fibonacci_generator(5))
    print(f"Fibonacci: {fib}")
    
    # Test decorator
    result = decorated_function(5)
    print(f"Decorated result: {result}")
    
    # Test context manager
    with CustomContextManager("test_resource") as cm:
        print("Inside context")
