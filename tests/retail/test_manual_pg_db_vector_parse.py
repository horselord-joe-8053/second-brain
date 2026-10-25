"""pgvector string parsing from psycopg2 (live PG returns bracket literals)."""

from retail_brain.manual_pg_db import _parse_pgvector


def test_parse_pgvector_bracket_string() -> None:
    assert _parse_pgvector("[0.5,1.0,-2.0]") == [0.5, 1.0, -2.0]


def test_parse_pgvector_list_passthrough() -> None:
    assert _parse_pgvector([0.1, 0.2]) == [0.1, 0.2]
