import pytest
from dataclasses import dataclass


@dataclass
class Foo:
    foo: int = 1


@dataclass(frozen=True)
class Bar:
    foo: Foo
    bar: int = 12


@dataclass(frozen=True)
class Baz:
    bar: Bar
    foo: Foo
    baz: int = 123


@pytest.fixture
def baz() -> Baz:
    return Baz(bar=Bar(foo=Foo()), foo=Foo())
