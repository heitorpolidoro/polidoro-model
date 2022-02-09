try:
    import i18n
    import locale

    _ = i18n.t
    lc, encoding = locale.getdefaultlocale()

    i18n.set('locale', lc)
    i18n.set('filename_format', '{locale}.{format}')
    i18n.load_path.append('locale')
except ImportError:
    _ = str
    i18n = None
    locale = None

import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import declarative_base, DeclarativeMeta, sessionmaker, Query
from string import Template


class BaseType(DeclarativeMeta):
    session = None
    """ Store the session """

    __str_attributes__ = None
    __custom_str__ = None

    def __init__(cls, class_name, *args, **kwargs):
        super(BaseType, cls).__init__(class_name, *args, **kwargs)
        if class_name != 'Base':
            if BaseType.session is None:
                engine = create_engine(os.environ.get('DB_URL', ''))
                session = sessionmaker()
                session.configure(bind=engine)
                Base.metadata.create_all(engine)
                BaseType.session = session()

    def attributes(cls):
        """Return a list(str) of the attributes"""
        return [a.key for a in inspect(cls).attrs]

    def create(cls, **attributes):
        """Create an instance of Model with initial attributes"""
        instance = cls(**attributes)
        for attr in cls.attributes():
            if attr != 'id' and getattr(instance, attr) is None:
                instance.ask_attribute(attr)
        return instance

    def filter(cls, *args, **kwargs):
        """A combination of SQLAlchemy Query.filter and Query.filter_by"""
        query = BaseType.session.query(cls)

        for arg in args:
            query = query.filter(arg)

        for attr, value in kwargs.items():
            column = getattr(cls, attr)
            if '%' in value:
                query = query.filter(column.like(value))
            else:
                query = query.filter(column == value)
        return query

    def print(cls, *args, **kwargs):
        """Prints a list of instances filtered"""
        if args and isinstance(args[0], (list, Query)):
            entities = args[0]
        else:
            entities = cls.filter(*args, **kwargs)
        for e in entities:
            print(e)

    @staticmethod
    def ask_attribute(instance, attribute):
        """Ask for an attribute, in terminal, and set in the instance."""
        default = getattr(instance, attribute, None)
        default_str = '' if default is None else f'({default})'
        value = BaseType._input(f'{attribute}{default_str}: ')
        if value == '':
            value = default
        setattr(instance, attribute, value)

    @staticmethod
    def save(instance, commit=True):
        """Add the instance (SQLAlchemy session.add(instance)) and commit (SQLAlchemy session.commit())
        if `commit` is `True."""
        BaseType.session.add(instance)
        if commit:
            BaseType.session.commit()

    @staticmethod
    def edit(instance):
        """Ask for each instance attribute for a new value, with the old value as default"""
        for attr in instance.attributes():
            if attr != 'id':
                instance.ask_attribute(attr)
        instance.save()

    @staticmethod
    def delete(instance, commit=True):
        """Delete the instance (SQLAlchemy session.delete(instance)) and commit (SQLAlchemy session.commit())
         if `commit` is `True."""
        BaseType.session.delete(instance)

        if commit:
            BaseType.session.commit()

    @staticmethod
    def _input(prompt=None):
        return input(prompt)

    @staticmethod
    def _boolean_input(message, default=True):
        options = 'Y/n' if default else 'y/N'
        resp = input(f'{message} [{options}]: ')
        if not resp:
            return default
        return resp.lower() == 'y'


Base = declarative_base(metaclass=BaseType)


def _base___str__(self):
    if self.__custom_str__:
        template_values = {'class': _(self.__class__.__name__)}
        template_values.update(self.__dict__)
        template_values = {k: v for k, v in template_values.items() if not k.startswith('_sa')}
        return Template(self.__custom_str__).substitute(**template_values)
    else:
        attributes = self.__str_attributes__ or self.attributes()
        attributes_values = ', '.join(
            f'{_(attr).upper()}: {getattr(self, attr)}' for attr in attributes
        )

        return f'<{_(self.__class__.__name__)}({attributes_values})>'


def _base___repr__(self):
    return f'<{self.__class__.__name__}(ID: {self.id})>'


def _base___getattr__(self, item):
    item = getattr(self.__class__, item)
    import inspect
    if item and \
            (inspect.signature(item).parameters and list(inspect.signature(item).parameters)[0] == 'instance'):
        def instance_wrapper(*args, **kwargs):
            return item(self, *args, **kwargs)

        return instance_wrapper

    return item


def _set_base_methods(methods):
    for name, method in methods.items():
        setattr(Base, name.replace('_base_', ''), method)


def get_model(model_name: str):
    """Search for all Base subclasses than return the model with model_name

    Args:
         model_name: The name of the model

    Returns:
        The model with model_name

    """
    for sub_class in Base.__subclasses__():
        if model_name == sub_class.__name__.lower():
            return sub_class
    raise Exception(f'Model "{model_name}" not found!')


_set_base_methods({name: method for name, method in locals().items() if name.startswith('_base_')})
