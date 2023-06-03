from dataclasses import dataclass
from more_dataclasses import nest_dataclass, NotADataclass, NestedDataclassMeta
import pytest


def test_error_if_not_dataclass():
    with pytest.raises(NotADataclass):

        @nest_dataclass
        class Foo:
            ...

    with pytest.raises(NotADataclass):
        NestedDataclassMeta.all_fields(str)


def test_metaclass_basics():
    @dataclass
    class Foo:
        foo: str = "foo"

    @nest_dataclass
    @dataclass
    class Bar:
        fooh: Foo
        bar: str = "bar"

    bar = Bar(foo="fu", bar="bo")
    assert bar.foo == "fu"

    assert bar.to_flat_dict() == {"foo": "fu", "bar": "bo"}


def test_duplicated_fields():
    @dataclass
    class Foo:
        foo: str = "foo"

    with pytest.raises(AttributeError):

        @nest_dataclass
        @dataclass
        class Bar:
            foo: str
            mur: Foo = Foo
