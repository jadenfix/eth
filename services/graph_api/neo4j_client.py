"""Async orchestration over the actual persistent graph adapter."""

import asyncio
from .store import GraphStore


class Neo4jClient:
    def __init__(self, **configuration):
        self.store = GraphStore(**configuration)
        self.driver = self.store.driver

    async def create_entity(self, entity_data):
        return await asyncio.to_thread(self.store.create_entity, entity_data)

    async def create_relationship(self, relationship):
        return await asyncio.to_thread(self.store.create_relationship, relationship)

    async def get_entity(self, entity_id):
        return await asyncio.to_thread(self.store.get_entity, entity_id)

    async def get_entities(self, filters=None, limit=100):
        return await asyncio.to_thread(self.store.get_entities, filters, limit)

    def close(self):
        self.store.close()
