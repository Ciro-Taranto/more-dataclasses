import pytest
from dataclasses import asdict
from .conftest import Baz
from more_dataclasses import from_nested_dict


def test_from_nested_dict(baz: Baz):
    nested_dict = asdict(baz)
    new_baz = from_nested_dict(nested_dict, type(baz))
    assert new_baz == baz


def test_error_on_wrong_field(baz: Baz):
    nested_dict = asdict(baz)
    nested_dict["something in the air"] = "it is pollen"
    with pytest.raises(KeyError):
        from_nested_dict(nested_dict, type(baz))


def test_error_on_not_dataclass():
    class Dummy:
        ...

    with pytest.raises(TypeError):
        from_nested_dict({}, Dummy)
