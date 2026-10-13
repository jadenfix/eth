"""Actual isolated worker failure and HTTP graph-container persistence proof."""

import json
import subprocess
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import uuid


def docker(*arguments, check=True):
    return subprocess.run(
        ["docker", *arguments], check=check, text=True, capture_output=True
    )


def http(path, payload=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request(
        "http://127.0.0.1:18880" + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers=headers,
    )
    try:
        with urlopen(request, timeout=3) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def wait_ready():
    for _ in range(60):
        try:
            code, body = http("/health")
            if code == 200 and body.get("storage") == "sqlite":
                return
        except OSError:
            pass
        time.sleep(0.5)
    raise RuntimeError("Actual ontology container did not become ready")


def main():
    for worker in ["ingestion", "agents-mev-watch"]:
        result = docker(
            "run", "--rm", "--network", "none", "eth-proof-" + worker, check=False
        )
        assert result.returncode != 0, "Unconfigured cloud worker falsely started"
        assert "GOOGLE_CLOUD_PROJECT" in result.stderr, result.stderr

    suffix = uuid.uuid4().hex
    container, volume = "eth-graph-proof-" + suffix, "eth-graph-data-" + suffix
    token = "isolated-container-test-token"
    docker("volume", "create", volume)
    try:
        docker(
            "run",
            "-d",
            "--name",
            container,
            "-p",
            "127.0.0.1:18880:8000",
            "-e",
            "GRAPH_API_TOKEN=" + token,
            "-v",
            volume + ":/data",
            "eth-proof-ontology",
        )
        wait_ready()
        mutation = {
            "query": 'mutation { createEntity(input:{type:"PERSON",name:"Container receipt",addresses:[]}) { id name } }'
        }
        assert http("/graphql", mutation)[0] == 403
        code, body = http("/graphql", mutation, token)
        assert code == 200 and "errors" not in body, body
        entity_id = body["data"]["createEntity"]["id"]
        docker("restart", container)
        wait_ready()
        code, persisted = http(
            "/graphql",
            {
                "query": "query($id:String!){entity(id:$id){id name}}",
                "variables": {"id": entity_id},
            },
        )
        assert (
            code == 200 and persisted["data"]["entity"]["name"] == "Container receipt"
        ), persisted
        print(
            "PASS actual Docker workers fail closed without provider config; GraphQL auth/create/restart/SQLite volume persistence"
        )
    finally:
        print(docker("logs", container, check=False).stdout)
        docker("rm", "-f", container, check=False)
        docker("volume", "rm", volume, check=False)


if __name__ == "__main__":
    main()
