from backend.graph.graph_search import (
    find_class,
    find_function,
)

print(
    find_class("HTTPDigestAuth")
)

print(
    find_function("get_auth_from_url")
)