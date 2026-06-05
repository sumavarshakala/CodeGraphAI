from backend.graph.neo4j_client import driver

with driver.session() as session:

    session.run(
        """
        CREATE (r:Repository {
            name: 'psf_requests'
        })
        """
    )

print("Repository node created")