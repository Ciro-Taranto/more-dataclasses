from more_dataclasses.decorators import nest_dataclass
from dataclasses import dataclass


from typing import Optional


@dataclass(frozen=True)
class Person:
    name: str
    surname: str
    age: Optional[int] = None


@nest_dataclass
@dataclass(frozen=True)
class Employee:
    person: Person
    department: str


@nest_dataclass
@dataclass(frozen=True)
class Customer:
    person: Person
    company: str


@nest_dataclass
@dataclass(frozen=True)
class CustomerWithDiscount:
    customer: Customer
    discount_id: str


very_good_worker = Employee(name="John", surname="Doe", age=35, department="analytics")
very_special_customer = CustomerWithDiscount(
    name="Jane", surname="Doe", company="a very nice one", discount_id="Fj2LK1"
)

print(very_good_worker.to_flat_dict())
print(very_special_customer.to_flat_dict())
