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

Uses:
```python
from sqlalchemy import Column, Integer, String

from polidoro_model import Base


class Account(Base):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
```

Methods:
- `Model.attributes()`: Return a list of the model attributes (str).
- `Model.filter(*args, **kwargs)`: A combination of Query.filter and Query.filter_by.
- `Model.create(**attributes)`: Create an instance of Model with initial attributes.
- `Model.print(*args, **kwargs)` Prints a list of instances filtered.
- `instance.set_attribute(attribute)`: Set a value in an instance.
- `instance.ask_attribute(attribute)`: Ask for an attribute, in terminal, and set in the instance.
- `instance.save(commit=True)`: Add the instance (`session.add(instance)`) and commit (`session.commit()`) if `commit` is `True. 
- `instance.delete(commit=True)`: Delete the instance (`session.delete(instance)`) and commit (`session.commit()`) if `commit` is `True. 
- `instance.edit()`: Ask for each instance attribute for a new value, with the old value as default.
- `instence.__str__`: Prints `<Model(ATTR1: VALUE1, ATTR2: VALUE2...)`, printing all attributes.

The `__str__` can be configured using these 2 Model class attributes: 
- `__str_attributes__`: A list for attributes to print.
- `__custom_str__`: Create a custom string using `$attribute` and `$class`. 

### Integrations
#### [Polidoro Argument](https://github.com/heitorpolidoro/polidoro-argument)
If the `polidoro-argument` library is installed you cas use some terminal commands to manipulate your models.
```python
from polidoro_argument import PolidoroArgumentParser
import polidoro_model.commands

if __name__ == '__main__':
    try:
        PolidoroArgumentParser().parse_args()
    except KeyboardInterrupt:
        pass
```

This will create a CLI for your script: `./myscript COMMAND MODEL`
The commands are:
- `create`: Creates and save a models instance.
- `delete`: Delete a models instance.
- `edit`: Edit a models instance.
- `list`: List instances.

All commands accepts the model attributes as parameters. In `create` will set these attributes, in 
`delete`, `edit` and `list` will filter the result. The filter accepts `%` in string attributes and will use 
the `like` comparison.

```shell
$ ./script.py create account --name="Account Name"
<Account(ID: 1, NAME: Account Name)>

$ ./script.py list account --name="Account%"
<Account(ID: 1, NAME: Account Name)>
```
#### [Python i18n](https://github.com/danhper/python-i18n)
The `polidoro-model` library sets, as default configuration for the `python-i18n` library, the file name format 
as `'{locale}.{format}'` and the path as `./locale`.
The `polidoro-model` library will attempt to translate the model name and the attributes.

`./locale/pt_BR.yml`
```yaml
pt_BR:
  name: nome
  Account: Conta
```

```shell
$ ./script.py list account
<Conta(ID: 1, NOME: a)>
```
