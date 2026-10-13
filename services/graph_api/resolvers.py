"""Resolvers execute a configured persistent graph, never canned entity lists."""

from .store import GraphStore

_default_store = None


def configured_store():
    global _default_store
    if _default_store is None:
        _default_store = GraphStore()
    return _default_store


def query_database(limit=100, filter=None, store=None):
    return (store or configured_store()).get_entities(filter, limit)


def query_relationships(entity_id=None, limit=100, store=None):
    return (store or configured_store()).get_relationships(entity_id, limit)


def get_entities(info=None, limit=100, filter=None):
    store = info.context.get("store") if info and info.context else None
    if store is not None:
        return query_database(limit=limit, filter=filter, store=store)
    return query_database(limit=limit, filter=filter)


def get_relationships(info=None, entity_id=None, limit=100):
    store = info.context.get("store") if info and info.context else None
    if store is not None:
        return query_relationships(entity_id=entity_id, limit=limit, store=store)
    return query_relationships(entity_id=entity_id, limit=limit)
