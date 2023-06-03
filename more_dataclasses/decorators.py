from types import new_class
from typing import Type, TypeVar
from dataclasses import dataclass, fields, is_dataclass
from functools import partial
from functools import lru_cache


class NotADataclass(Exception):
    def __init__(self, cls_obj):
        super().__init__(f"{cls_obj.__name__} is not an instance of dataclass.")


class NestedDataclassMeta(type):
    def __new__(cls_obj, *args, **kwargs):
        instance = super().__new__(cls_obj, *args, **kwargs)
        NestedDataclassMeta._make_init(instance)
        NestedDataclassMeta._make_properties(instance)
        NestedDataclassMeta._make_to_flat_fields(instance)
        return instance

    @staticmethod
    def _make_properties(instance):
        all_fields, _ = NestedDataclassMeta.all_fields(instance)
        own_fields = set(field.name for field in fields(instance))
        for field_name, field_source in all_fields.items():
            if field_name not in own_fields:
                prop = property(
                    fget=partial(
                        NestedDataclassMeta._nested_prop_,
                        field_name=field_name,
                        field_source=field_source,
                    )
                )
                setattr(instance, field_name, prop)

    @staticmethod
    def _nested_prop_(instance, field_source, field_name):
        source = getattr(instance, field_source)
        value = getattr(source, field_name)
        return value

    @staticmethod
    def _make_init(cls_obj):
        """
        Creates the __init__ of the dataclass.

        Note: to be compliant with the frozen dataclasses the __init__ directly writes into the
        __dict__ of the instance, rather than using the setattr, which might be frozen.
        """
        if not is_dataclass(cls_obj):
            raise NotADataclass(cls_obj)

        _, init_fields = NestedDataclassMeta.all_fields(cls_obj)

        def _init(instance, /, **kwargs):
            instance_kwargs = {}
            for field_name, (field_type, nested_field_names) in init_fields.items():
                if is_dataclass(field_type):
                    instance_kwargs[field_name] = field_type(
                        **{
                            name: kwargs[name]
                            for name in nested_field_names
                            if name in kwargs
                        }
                    )
                else:
                    args = list(
                        kwargs[name] for name in nested_field_names if name in kwargs
                    )
                    if args:
                        instance_kwargs[field_name] = field_type(*args)
                if field_name in instance_kwargs:
                    instance.__dict__[field_name] = instance_kwargs[field_name]

        setattr(cls_obj, "__init__", _init)

    @staticmethod
    def _make_to_flat_fields(cls_obj):
        all_fields, _ = NestedDataclassMeta.all_fields(cls_obj)

        def to_flat_dict(cls_obj):
            flat_dict = {name: getattr(cls_obj, name) for name in all_fields}
            return flat_dict

        setattr(cls_obj, "to_flat_dict", to_flat_dict)

    @lru_cache
    @staticmethod
    def all_fields(cls_obj) -> tuple[dict[str, str], dict[str, tuple[type, list]]]:
        """
        Convenience method to get all the fields in a nested dataclass.
        This method iterates through the own dataclass fields and the children dataclass fields.
        The method returns two dictionaries:
        flat_fields: each key is a field of the nested dataclass whose corresponding value is the
            name of the `flat` attribute of the instance which is storing (somewhere deeper) the
            value of the field.
        init_fields: a dictionary which shall be used to create the __init__ method.
            The keys in the dictionary are the `flat` fields of the dataclass and the values are
            tuples, whose first entry is the type of the object, and the second entry are all the
            names that the __init__ of the nested object requires.
        """
        if not is_dataclass(cls_obj):
            raise NotADataclass(cls_obj)
        init_fields = dict()
        flat_fields = dict()
        nested_fields = fields(cls_obj)
        for field in nested_fields:
            if is_dataclass(field.type):
                new_fields = {
                    nested_field_name: field.name
                    for nested_field_name in NestedDataclassMeta.all_fields(field.type)[
                        0
                    ]
                }
                init_fields[field.name] = (field.type, list(new_fields))
            else:
                new_fields = {field.name: field.name}
                init_fields[field.name] = (field.type, [field.name])
            if duplicated := set(flat_fields).intersection(new_fields):
                raise AttributeError(f"Duplicated fields: {duplicated}")
            flat_fields.update(new_fields)
        return flat_fields, init_fields


T = TypeVar("T")


def nest_dataclass(standard_dataclass: Type[T]) -> Type[T]:
    """
    A decorator to transform a standard dataclass into a nested dataclass.

    The nested dataclass will have an automatically created __init__, and will have all the nested
    fields as properties directly accessible at the top level.

    The nested dataclass will also have a `to_flat_dict` method which will return a "flat"
        dictionary of nested field names and values.
    """
    nested_dataclass = new_class(
        standard_dataclass.__name__,
        bases=(standard_dataclass,),
        kwds=dict(metaclass=NestedDataclassMeta),
    )
    return nested_dataclass
