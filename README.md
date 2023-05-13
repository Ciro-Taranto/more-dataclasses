A tiny (currently two pieces) collection of utilities for dataclasses. 
Documentation and testing are work in progress (and knowing the author will never be completed). 

`from_nested_dict` ia s function to instantiate a nested dataclass from a nested dictionary, it is 
more or less the invert of `datalasses.asdict()` applied to a nested dataclass. 

`nested_replace` allow to replace a nested field in a nested dataclass with a similar interface to
`dataclasses.replace`. 