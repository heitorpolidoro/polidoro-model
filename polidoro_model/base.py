import re
from functools import lru_cache

from polidoro_question.question import Question

try:
    import i18n
    import locale

    @lru_cache
    def _(text):
        return i18n.t(text)
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
from sqlalchemy.orm import declarative_base, DeclarativeMeta, sessionmaker, Query, RelationshipProperty, ColumnProperty
from string import Template


class BaseType(DeclarativeMeta):
    session = None
    """ Store the session """

    __str_attributes__ = None
    __custom_str__ = None
    __translate_values__ = False
    __print_as_table__ = False
    __default_filter_attribute__ = None
    __all__ = []

    def __init__(cls, class_name, *args, **kwargs):
        super(BaseType, cls).__init__(class_name, *args, **kwargs)

    def attributes(cls, ignore_relationship=False):
        """Return a list(str) of the attributes"""
        attributes = []
        for a in inspect(cls).attrs:
            if ignore_relationship and isinstance(a, RelationshipProperty):
                continue
            attributes.append(a.key)
        return attributes

    def create(cls, ask_for_none_values=True, **attributes):
        """Create an instance of Model with initial attributes"""
        instance = cls(**attributes)
        if ask_for_none_values:
            for attr in cls.attributes():
                if not attr.endswith('id') and getattr(instance, attr) is None:
                    instance.ask_attribute(attr)
        return instance

    def filter(cls, *args, **kwargs):
        """A combination of SQLAlchemy Query.filter and Query.filter_by"""
        query = BaseType.session.query(cls)

        for arg in args:
            query = query.filter(arg)

        for attr, value in kwargs.items():
            column = getattr(cls, attr)
            if value == 'None':
                value = None
            if value is not None and not isinstance(value, Base) and isinstance(column.property, RelationshipProperty):
                clazz = column.property.entity.class_
                default_attribute = getattr(clazz, '__default_filter_attribute__', None)
                value = clazz.filter(**{default_attribute: value}).first()
            if isinstance(value, str) and '%' in value:
                query = query.filter(column.like(value))
            elif isinstance(value, tuple):
                query = query.filter(column.between(*value))
            else:
                query = query.filter(column == value)
        return query

    def print(cls, *args, attributes=None, **kwargs):
        """Prints a list of instances filtered"""
        if args and isinstance(args[0], (list, Query)):
            entities = args[0]
        else:
            entities = cls.filter(*args, **kwargs)
        if cls.__print_as_table__:
            from polidoro_table import Table
            t = Table(_(cls.__name__))
            if not attributes:
                if hasattr(cls, '__table_attributes__'):
                    attributes = getattr(cls, '__table_attributes__')
                else:
                    attributes = [a.replace('_id', '') for a in cls.attributes(ignore_relationship=True)]
            t.add_columns([_(a) for a in attributes])

            attributes_to_translate = cls.attributes_to_translate()

            for e in entities:
                row = []
                for a in attributes:
                    value = getattr(e, a, None)
                    if a in attributes_to_translate:
                        if isinstance(value, Base):
                            value = _base___str__(value, template=getattr(value, '__table_str__', None))
                        value = _(str(value))
                    row.append(value)
                t.add_row(row)
            t.print()
        else:
            for e in entities:
                print(e)

    def attributes_to_translate(cls):
        if cls.__translate_values__:
            if isinstance(cls.__translate_values__, list):
                attributes_to_translate = cls.__translate_values__
            else:
                attributes_to_translate = cls.attributes()
        else:
            attributes_to_translate = []
        return attributes_to_translate

    def all(cls):
        if not cls.__all__:
            cls.__all__ = cls.filter()
        return cls.__all__

    @staticmethod
    def init_db():
        engine = create_engine(os.environ.get('DB_URL', ''))
        session = sessionmaker()
        session.configure(bind=engine)
        Base.metadata.create_all(engine)
        BaseType.session = session()

    @staticmethod
    def ask_attribute(instance, attribute, default=None):
        """Ask for an attribute, in terminal, and set in the instance."""
        attribute_property = inspect(instance.__class__).attrs[attribute]
        attributes_options = getattr(instance.__class__, '__attributes_options__', {})
        auto_complete = False
        if isinstance(attribute_property, RelationshipProperty):
            model = get_model(attribute_property.argument)
            options_list = model.all()
            option_str = getattr(model, '__option_str__', None)
            options = {}
            if list(attribute_property.local_columns)[0].nullable:
                options[_('none').capitalize()] = None
            for o in options_list:
                if option_str:
                    options[_base___str__(o, option_str)] = o
                else:
                    options[str(o)] = o
            options[_('create').capitalize()] = 'create'
            attributes_options[attribute] = options
            column_type = model
            auto_complete = True
        elif isinstance(attribute_property, ColumnProperty):
            column = attribute_property.columns[0]
            column_type = column.type.python_type
            if default is None:
                default = getattr(instance, attribute, None)
                if default is None and column.default:
                    default = column.default.arg

        value = Question(f'{_(attribute).capitalize()}',
                         default=default,
                         type=column_type,
                         options=attributes_options.get(attribute, None),
                         auto_complete=auto_complete
                         ).ask()
        if value == 'create':
            value = model.create()
            value.save()
        instance.set_attribute(attribute, value)

    @staticmethod
    def set_attributes(instance, **attributes):
        for attr, value in attributes.items():
            instance.set_attribute(attr, value)

    @staticmethod
    def set_attribute(instance, attribute, value):
        setattr(instance, attribute, value)

    @staticmethod
    def save(instance, commit=True):
        """Add the instance (SQLAlchemy session.add(instance)) and commit (SQLAlchemy session.commit())
        if `commit` is `True."""
        BaseType.session.add(instance)
        if commit:
            BaseType.session.commit()
            BaseType.session.refresh(instance)
        instance.__class__.__all__ = []
        return instance

    @staticmethod
    def edit(instance, set=None):
        """Ask for each instance attribute for a new value, with the old value as default"""
        if set:
            attributes = {}
            for attr_value in set.split(','):
                attr, value = attr_value.split('=')
                attributes[attr] = value
            instance.set_attributes(**attributes)
        else:
            for attr in instance.attributes():
                if not attr.endswith('id'):
                    instance.ask_attribute(attr)
        instance.save()

    def delete(cls, instance=None, commit=True, **kwargs):
        """Delete the instance (SQLAlchemy session.delete(instance)) and commit (SQLAlchemy session.commit())
         if `commit` is `True."""
        if instance is None:
            cls.filter(**kwargs).delete()
        else:
            BaseType.session.delete(instance)

        if commit:
            BaseType.session.commit()
            cls.__all__ = []


Base = declarative_base(metaclass=BaseType)


@lru_cache
def _base___str__(self, template=None):
    if template is None:
        template = self.__custom_str__

    translated_class_name = _(self.__class__.__name__)
    translated_values = {'class': translated_class_name}
    attributes_to_translate = self.attributes_to_translate()
    attributes = self.__str_attributes__ or self.attributes()
    for attribute in attributes:
        if not attribute.startswith('_sa'):
            v = getattr(self, attribute)
            if attribute in attributes_to_translate:
                v = _(str(v))
            if attribute.endswith('_id'):
                attribute_instance = attribute[:-3]
                translated_values[attribute_instance] = getattr(self, attribute_instance)
        translated_values[attribute] = v
    if template:
        instance_info = re.findall(r'\$\(.*?\)', template)
        for ii in instance_info:
            key = ii[2:-1]
            value = self
            for k in key.split('.'):
                value = getattr(value, k)
                if value is None:
                    break
            template = template.replace(ii, str(value))
        substitute = Template(template).substitute(**translated_values)
        return substitute
    else:
        attributes_values = []
        for attr in attributes:
            value = translated_values.get(attr, None)
            if value is not None:
                attributes_values.append(f'{_(attr).upper()}: {value}')
        return f'<{translated_class_name}({", ".join(attributes_values)})>'


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
        if model_name.lower() == sub_class.__name__.lower():
            return sub_class
    raise Exception(f'Model "{model_name}" not found!')


_set_base_methods({name: method for name, method in locals().items() if name.startswith('_base_')})
