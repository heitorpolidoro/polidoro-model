# Polidoro Model

A [SQLAlchemy](https://www.sqlalchemy.org/) based model utils

### Instalation
```shell
pip install polidoro-model
```

- Automatically creates a session
- Defines some methods to make it easier to use

Methods:
- `Model.attributes()`: Return a list of the model attributes (str).
- `Model.filter(*args, **kwargs)`: A combination of Query.filter and Query.filter_by.
- `Model.create(**attributes)`: Create an instance of Model with initial attributes.
- `Model.print(*args, **kwargs)` Prints a list of instances filtered.
- `instance.ask_attribute(attribute)`: Ask for an attribute, in terminal, and set in the instance.
- `instance.save(commit=True)`: Add the instance (`session.add(instance)`) and commit (`session.commit()`) if `commit` is `True. 
- `instance.delete(commit=True)`: Delete the instance (`session.delete(instance)`) and commit (`session.commit()`) if `commit` is `True. 
- `instance.edit()`: Ask for each instance attribute for a new value, with the old value as default.
- `instence.__str__`: Prints `<Model(ATTR1: VALUE1, ATTR2: VALUE2...)`, printing all attributes.

The `__str__` can be configured using these 2 Model class attributes: 
- `__str_attributes__`: A list for attributes to print.
- `__custom_str__`: Create a custom string using `$attribute` and `$class`. 
