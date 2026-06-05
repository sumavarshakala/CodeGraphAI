from backend.graph.graph_extractor import (
    extract_python_symbols,
)

code = """
import requests
import os

class User:
    pass

def login():
    pass

def logout():
    pass
"""

result = extract_python_symbols(code)

print(result)