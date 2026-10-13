from graphql import build_schema
from . import resolvers

schema = build_schema("""
scalar JSON
type Address { address: String!, balance: String }
type Transaction { hash: String!, fromAddress: String, toAddress: String, value: String }
type Entity { id: String!, type: String!, address: String, addresses: [String!]!, confidence: Float!, name: String, labels: [String!]!, properties: JSON, riskScore: Float, createdAt: String!, updatedAt: String! }
type Relationship { id: String!, from_entity: String!, to_entity: String!, relationship_type: String!, strength: Float, weight: Float, properties: JSON, createdAt: String! }
type EntityNetwork { center: Entity!, nodes: [Entity!]!, edges: [Relationship!]!, depth: Int! }
input EntityFilter { type: String, labels: [String!], hasAddress: Boolean, riskScoreMin: Float, riskScoreMax: Float }
input EntityInput { id: String, type: String!, address: String, addresses: [String!], confidence: Float, name: String, labels: [String!], properties: JSON, riskScore: Float }
input EntityUpdateInput { addresses: [String!], confidence: Float, name: String, labels: [String!], properties: JSON, riskScore: Float }
input RelationshipInput { id: String, type: String!, fromEntityId: String!, toEntityId: String!, properties: JSON, weight: Float, strength: Float }
type Query { entity(id: String!): Entity, entities(limit: Int = 100, filter: EntityFilter): [Entity!]!, relationships(entity_id: String, limit: Int = 100): [Relationship!]!, getEntityNetwork(id: String!, depth: Int = 2): EntityNetwork! }
type Mutation { createEntity(input: EntityInput!): Entity!, updateEntity(id: String!, input: EntityUpdateInput!): Entity!, createRelationship(input: RelationshipInput!): Relationship! }
""")
json_type = schema.get_type("JSON")
json_type.serialize = lambda value: value
json_type.parse_value = lambda value: value
from graphql.utilities import value_from_ast_untyped

json_type.parse_literal = lambda node, variables=None: value_from_ast_untyped(
    node, variables
)
schema.query_type.fields["entities"].resolve = (
    lambda root, info, **args: resolvers.get_entities(info, **args)
)
schema.query_type.fields["relationships"].resolve = (
    lambda root, info, **args: resolvers.get_relationships(info, **args)
)
schema.query_type.fields["entity"].resolve = lambda root, info, id: info.context[
    "store"
].get_entity(id)
schema.query_type.fields["getEntityNetwork"].resolve = (
    lambda root, info, id, depth=2: info.context["store"].get_entity_network(id, depth)
)
schema.mutation_type.fields["createEntity"].resolve = (
    lambda root, info, input: info.context["store"].create_entity(
        {k: v for k, v in input.items() if v is not None}
    )
)
schema.mutation_type.fields["updateEntity"].resolve = (
    lambda root, info, id, input: info.context["store"].update_entity(id, input)
)
schema.mutation_type.fields["createRelationship"].resolve = (
    lambda root, info, input: info.context["store"].create_relationship(input)
)
