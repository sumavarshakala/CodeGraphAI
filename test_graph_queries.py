from backend.graph.neo4j_client import driver


with driver.session() as session:

    result = session.run(
        """
        MATCH (f:File)-[:DEFINES]->(c:Class)
        WHERE c.name = $class_name
        RETURN f.path
        """,
        class_name="HTTPDigestAuth",
    )

    for row in result:
        print(row["f.path"])