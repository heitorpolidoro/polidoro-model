from functools import lru_cache

from polidoro_argument import Command
from polidoro_question.question import Question

from polidoro_model.base import get_model

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


def _get_entities(kwargs, model):
    if isinstance(model, str):
        model = get_model(model)
    entities = model.filter(**kwargs)
    return entities


def _action_confirmation(instance, action):
    return Question(f'{_(action).capitalize()} {instance}', type=bool, default=True).ask()


def _instance_action_with_confirmation(model, action, set=None, **kwargs):
    entities = _get_entities(kwargs, model)
    if not entities.count():
        print(f'{_("Nothing to")} {_(action)}')
    for instance in list(entities):
        if _action_confirmation(instance, action):
            getattr(instance, action)(set=set)


@Command(
    command_name='list',
    help='List instances. "--attr=value" to filter',
)
def list_model(model, **kwargs):
    model = get_model(model)
    columns = kwargs.pop('columns', None)
    if columns:
        columns = columns.split(',')
    entities = _get_entities(kwargs, model)
    model.print(entities, attributes=columns)


@Command(help='Creates an instance asking for values. "--attr=value" for initial set.')
def create(model, **kwargs):
    instance = get_model(model).create(**kwargs)
    instance.save()
    return instance


@Command(help='Edit an instance asking for values. "--attr=value" to filter. ". '
              '--set=attr=value" to set values without asking.')
def edit(model, **kwargs):
    return _instance_action_with_confirmation(model, 'edit', **kwargs)


@Command(help='Delete an instance. "--attr=value" to filter.')
def delete(model, **kwargs):
    return _instance_action_with_confirmation(model, 'delete', **kwargs)
