import ast


def extract_python_symbols(code: str):

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "classes": [],
            "functions": [],
            "imports": [],
        }

    classes = []
    functions = []
    imports = []

    for node in ast.walk(tree):

        if isinstance(node, ast.ClassDef):
            classes.append(node.name)

        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)

        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return {
        "classes": classes,
        "functions": functions,
        "imports": imports,
    }