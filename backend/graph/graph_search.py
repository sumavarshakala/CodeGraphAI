from backend.graph.neo4j_client import driver


def find_class(class_name: str):

    with driver.session() as session:

        result = session.run(
            """
            MATCH (f:File)-[:DEFINES]->(c:Class)
            WHERE c.name = $class_name
            RETURN f.path
            """,
            class_name=class_name,
        )

        record = result.single()

        if record:
            return record["f.path"]

        return None
    
def find_function(function_name: str):

    with driver.session() as session:

        result = session.run(
            """
            MATCH (f:File)-[:DEFINES]->(fn:Function)
            WHERE fn.name = $function_name
            RETURN f.path
            """,
            function_name=function_name,
        )

        record = result.single()

        if record:
            return record["f.path"]

        return None