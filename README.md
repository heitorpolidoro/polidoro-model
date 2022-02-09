# Polidoro Model
[![Tests](https://github.com/heitorpolidoro/polidoro-model/actions/workflows/test.yml/badge.svg)](https://github.com/heitorpolidoro/polidoro-model/actions/workflows/test.yml)
[![Upload Python Package](https://github.com/heitorpolidoro/polidoro-model/actions/workflows/python-publish.yml/badge.svg)](https://github.com/heitorpolidoro/polidoro-model/actions/workflows/python-publish.yml)
[![Lint with comments](https://github.com/heitorpolidoro/polidoro-model/actions/workflows/python-lint.yml/badge.svg)](https://github.com/heitorpolidoro/polidoro-model/actions/workflows/python-lint.yml)
![GitHub last commit](https://img.shields.io/github/last-commit/heitorpolidoro/polidoro-model)
[![Coverage Status](https://coveralls.io/repos/github/heitorpolidoro/polidoro-model/badge.svg?branch=master)](https://coveralls.io/github/heitorpolidoro/polidoro-model?branch=master)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=heitorpolidoro_polidoro-model&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=heitorpolidoro_polidoro-model)

[![Latest](https://img.shields.io/github/release/heitorpolidoro/polidoro-model.svg?label=latest)](https://github.com/heitorpolidoro/polidoro-model/releases/latest)
![GitHub Release Date](https://img.shields.io/github/release-date/heitorpolidoro/polidoro-model)

![PyPI - Downloads](https://img.shields.io/pypi/dm/polidoro-model?label=PyPi%20Downloads)

![GitHub](https://img.shields.io/github/license/heitorpolidoro/polidoro-model)
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
