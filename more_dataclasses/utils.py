from typing import Dict, Any, Type, TypeVar
from dataclasses import replace, is_dataclass, fields

T = TypeVar("T")


def nested_replace(dataclass_instance: T, /, **changes) -> T:
    """
    Quasi-drop-in replacement for dataclasses.replace which support also replacing
    on nested instances of dataclass.

    If only "shallow" fields needs to be replaced this function is just using dataclass.replace.
    If "deep" changes are needed this function will instantiate all the nested dataclasses that are
    required to perform the desired change of a nested field.

    For example, if you want to achieve foo.bar.baz = value, then you can call:
    new_foo = nested_replace(foo, **{'bar.baz': value}) which is roughly equivalent to:
    new_foo = replace(foo, bar=replace(foo.bar, baz=value)).

    NOTE: replace instantiates new objects which is slow for dataclasses.
    If latency is an issue or with deep nestings nested_replace (and nested_dataclasses)
    might not be a good idea.
    """
    if not is_dataclass(dataclass_instance):
        raise TypeError("nested_replace() should be called on dataclass instances")
    replaced_fields = dict()
    for key, val in changes.items():
        shallow_field_name, _, deep_field_names = key.partition(".")
        shallow_field = getattr(dataclass_instance, shallow_field_name)
        if not deep_field_names:
            new_shallow_field = val
        else:
            new_shallow_field = nested_replace(
                replaced_fields.get(shallow_field_name, shallow_field),
                **{deep_field_names: val},
            )
        replaced_fields[shallow_field_name] = new_shallow_field
    replaced_dataclass = replace(dataclass_instance, **replaced_fields)
    return replaced_dataclass


def from_nested_dict(input_dictionary: Dict[str, Any], dataclass_type: Type[T]) -> T:
    """
    Instantiate a dataclass from a nested dict.

    dataclasses.asdict() supports serialization of nested dataclasses to nested dictionaries.
    This function allows to support also the inverse operation:
    new_obj = from_nested_dict(dataclasses.asdict(obj), type(obj)).
    """
    if not is_dataclass(dataclass_type):
        raise TypeError("from_nested_dict() should be called on dataclass instances")
    dataclass_fields = {field.name: field.type for field in fields(dataclass_type)}
    new_input_dict = dict()
    for key, val in input_dictionary.items():
        try:
            sub_field_type = dataclass_fields[key]
        except KeyError:
            raise KeyError(f"{key} is not a valid field for {dataclass_type}.")
        if is_dataclass(sub_field_type):
            new_input_dict[key] = from_nested_dict(val, sub_field_type)
        else:
            new_input_dict[key] = val
    return dataclass_type(**new_input_dict)
