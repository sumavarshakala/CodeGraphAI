from neo4j import GraphDatabase


URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "abcdefghi"


driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD),
)


def test_connection():
    with driver.session() as session:
        result = session.run(
            "RETURN 'Neo4j Connected' AS message"
        )
        return result.single()["message"]