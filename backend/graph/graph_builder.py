from backend.graph.neo4j_client import driver


def add_file_graph(
    repo_name: str,
    file_path: str,
    symbols: dict,
):
    with driver.session() as session:

        session.run(
            """
            MERGE (r:Repository {name:$repo})
            MERGE (f:File {path:$file})

            MERGE (r)-[:HAS_FILE]->(f)
            """,
            repo=repo_name,
            file=file_path,
        )

        for cls in symbols["classes"]:
            session.run(
                """
                MERGE (c:Class {name:$name})
                MERGE (f:File {path:$file})

                MERGE (f)-[:DEFINES]->(c)
                """,
                name=cls,
                file=file_path,
            )

        for func in symbols["functions"]:
            session.run(
                """
                MERGE (fn:Function {name:$name})
                MERGE (f:File {path:$file})

                MERGE (f)-[:DEFINES]->(fn)
                """,
                name=func,
                file=file_path,
            )

        for imp in symbols["imports"]:
            session.run(
                """
                MERGE (i:Import {name:$name})
                MERGE (f:File {path:$file})

                MERGE (f)-[:IMPORTS]->(i)
                """,
                name=imp,
                file=file_path,
            )