import pytest
from dataclasses import replace

from more_dataclasses import nested_replace
from .conftest import Foo, Bar, Baz


def test_error_if_not_dataclass():
    class Dummy:
        ...

    with pytest.raises(TypeError):
        nested_replace(Dummy(), **{"foo.bar": 11})


def test_shallow_level(baz: Baz):
    replaced_baz = nested_replace(baz, baz=12)
    expected_baz = replace(baz, baz=12)
    assert replaced_baz == expected_baz


def test_shallow_level_with_dataclass(baz: Baz):
    replaced_baz = nested_replace(baz, bar=Bar(foo=Foo(12)))
    expected_baz = replace(baz, bar=Bar(foo=Foo(12)))
    assert replaced_baz == expected_baz


def test_level_one_nesting_with_one_change(baz: Baz):
    new_bar = replace(baz.bar, bar=66)
    replaced_baz = nested_replace(baz, **{"bar.bar": 66})
    expected_baz = replace(baz, bar=new_bar)
    assert replaced_baz == expected_baz


def test_level_one_nesting_with_two_changes(baz: Baz):
    new_bar = replace(baz.bar, bar=66)
    new_foo = Foo(72)
    replaced_baz = nested_replace(baz, foo=new_foo, **{"bar.bar": 66})
    expected_baz = replace(baz, bar=new_bar, foo=new_foo)
    assert replaced_baz == expected_baz


def test_level_two_nesting(baz: Baz):
    replaced_baz = nested_replace(baz, **{"bar.foo.foo": 67})
    expected_baz = replace(
        baz,
        bar=replace(baz.bar, foo=Foo(67)),
    )
    assert replaced_baz == expected_baz
