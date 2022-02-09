from polidoro_argument import Command

from polidoro_model.base import get_model, BaseType


def _get_entities(kwargs, model):
    if isinstance(model, str):
        model = get_model(model)
    entities = model.filter(**kwargs)
    return entities


def _action_confirmation(instance, action):
    return BaseType._boolean_input(f'{action.capitalize()} this {instance}')


@Command(command_name='list')
def list_model(model, **kwargs):
    model = get_model(model)
    entities = _get_entities(kwargs, model)
    model.print(entities)


@Command
def create(model, **kwargs):
    instance = get_model(model).create(**kwargs)
    instance.save()
    return instance


def _instance_action_with_confirmation(model, action, **kwargs):
    entities = _get_entities(kwargs, model)
    if not entities.count():
        print(f'Nothing to {action}')
    for instance in entities:
        if _action_confirmation(instance, action.capitalize()):
            getattr(instance, action)()


@Command
def edit(model, **kwargs):
    return _instance_action_with_confirmation(model, 'edit', **kwargs)


@Command
def delete(model, **kwargs):
    return _instance_action_with_confirmation(model, 'delete', **kwargs)
