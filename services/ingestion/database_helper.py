"""Parameterized BigQuery adapter; errors never become successful empty queries."""

import os
import re
from google.cloud import bigquery
from services.ingestion.ethereum_ingester import field


class BigQueryHelper:
    def __init__(self, client=None, project=None):
        self.client = client
        self.project = project or os.getenv("GOOGLE_CLOUD_PROJECT")
        if not self.project or not re.fullmatch(r"[A-Za-z0-9_-]+", self.project):
            raise ValueError("A valid GOOGLE_CLOUD_PROJECT is required")

    def query_recent_blocks(self, limit=50):
        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or not 1 <= limit <= 1000
        ):
            raise ValueError("limit must be between1 and1000")
        if self.client is None:
            raise RuntimeError(
                "An explicitly authenticated BigQuery client is required"
            )
        query = f"SELECT block_number,COUNT(*) AS tx_count FROM `{self.project}.onchain_data.curated_events` GROUP BY block_number ORDER BY block_number DESC LIMIT @limit"
        rows = self.client.query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("limit", "INT64", limit)
                ]
            ),
        ).result(timeout=30)
        return [
            {
                "block_number": int(field(row, "block_number")),
                "tx_count": int(field(row, "tx_count")),
            }
            for row in rows
        ]
