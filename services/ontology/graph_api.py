"""Actual ontology GraphQL service; graph_api/graph_api.py is its tracked alias."""

import hmac
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from graphql import graphql_sync, parse, OperationType, GraphQLError
from starlette.concurrency import run_in_threadpool
from services.graph_api.schema import schema
from services.graph_api.resolvers import configured_store
from services.graph_api.store import GraphStore


class OntologyService(GraphStore):
    """Durable ontology operations shared with the executable GraphQL schema."""


def create_app(store=None, token=None):
    app = FastAPI(title="Blockchain ontology graph")
    app.state.store = store
    app.state.token = token if token is not None else os.getenv("GRAPH_API_TOKEN")

    @app.post("/graphql")
    async def execute(request: Request):
        raw = await request.body()
        if len(raw) > 65536:
            return JSONResponse(
                {"errors": [{"message": "request exceeds 64 KiB"}]}, status_code=413
            )
        try:
            data = await request.json()
            if not isinstance(data, dict) or not isinstance(data.get("query"), str):
                raise ValueError("a GraphQL query string is required")
            document = parse(data["query"])
        except (ValueError, TypeError, GraphQLError) as error:
            return JSONResponse({"errors": [{"message": str(error)}]}, status_code=400)
        try:
            backend = app.state.store or configured_store()
        except Exception:
            return JSONResponse(
                {"errors": [{"message": "graph storage unavailable"}]}, status_code=503
            )
        mutation = any(
            getattr(item, "operation", None) == OperationType.MUTATION
            for item in document.definitions
        )
        if mutation:
            expected = app.state.token
            actual = request.headers.get("Authorization", "").removeprefix("Bearer ")
            local = request.client and request.client.host in {
                "127.0.0.1",
                "::1",
                "localhost",
                "testclient",
                "testserver",
            }
            if (expected and not hmac.compare_digest(actual, expected)) or (
                not expected and (backend.mode != "sqlite" or not local)
            ):
                return JSONResponse(
                    {"errors": [{"message": "authorized write token required"}]},
                    status_code=403,
                )
        result = await run_in_threadpool(
            graphql_sync,
            schema,
            data["query"],
            context_value={"store": backend},
            variable_values=data.get("variables"),
            operation_name=data.get("operationName"),
        )
        body = {"data": result.data}
        if result.errors:
            body["errors"] = [{"message": error.message} for error in result.errors]
        return JSONResponse(body)

    @app.get("/health")
    def health():
        try:
            backend = app.state.store or configured_store()
            if backend.driver:
                backend.driver.verify_connectivity()
            return {"status": "healthy", "service": "ontology", "storage": backend.mode}
        except Exception:
            return JSONResponse(
                {"status": "unavailable", "service": "ontology"}, status_code=503
            )

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
