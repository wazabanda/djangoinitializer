import ast,astor
import os
import parso

""" 
This file contains the code needed to modify the varibles in a python file

Note that this has the dumb effect of removing most of the formatting so a 
better workaround for that will be created later
"""


def get_file_values(settings_path, variable):
    with open(settings_path, 'r') as file:
        tree = ast.parse(file.read(), filename=settings_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable:
                    value = node.value

                    if isinstance(value, ast.List):
                        return [_ast_to_python(elt) for elt in value.elts]
                    elif isinstance(value, ast.Dict):
                        return {_ast_to_python(key): _ast_to_python(value) for key, value in zip(value.keys, value.values)}
                    else:
                        return _ast_to_python(value)
    return None


def _ast_to_python(node):

    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.NameConstant):
        return node.value
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.List):
        return [_ast_to_python(elt) for elt in node.elts]
    elif isinstance(node, ast.Dict):
        return {_ast_to_python(key): _ast_to_python(value) for key, value in zip(node.keys, node.values)}
    elif isinstance(node, ast.Tuple):
        return tuple(_ast_to_python(elt) for elt in node.elts)
    elif isinstance(node, ast.Attribute):
        return _ast_to_python(node.value) + '.' + node.attr
    elif isinstance(node, ast.Subscript):
        return _ast_to_python(node.value) + '[' + _ast_to_python(node.slice) + ']'
    elif isinstance(node, ast.Index):
        return _ast_to_python(node.value)
    elif isinstance(node, ast.BinOp):
        return _ast_to_python(node.left) + _ast_to_python(node.op) + _ast_to_python(node.right)
    elif isinstance(node, ast.Compare):
        return _ast_to_python(node.left) + _ast_to_python(node.ops) + _ast_to_python(node.comparators)
    elif isinstance(node, ast.Call):
        return _ast_to_python(node.func) + '(' + _ast_to_python(node.args) + _ast_to_python(node.keywords) + ')'
    elif isinstance(node, ast.keyword):
        return _ast_to_python(node.arg) + '=' + _ast_to_python(node.value)
    else:
        return None


def modify_or_add_setting(settings_path, variable, new_value):
    with open(settings_path, 'r') as file:
        code = file.read()
        module = parso.parse(code)

    found = False
    for node in module.children:
        if isinstance(node, parso.python.tree.ExprStmt) and node.get_defined_names():
            name = node.get_defined_names()[0].value
            if name == variable:
                new_code = f"{variable} = {repr(new_value)}"
                node.children[-1].value = new_code
                found = True
                break

    if not found:
        new_code = f"\n{variable} = {repr(new_value)}\n"
        module.children.append(parso.parse(new_code).children[0])

    with open(settings_path, 'w') as file:
        file.write(module.get_code())


def _python_to_ast(value):
    if isinstance(value, str):
        return ast.Constant(value=value)
    elif isinstance(value, bool):
        return ast.NameConstant(value=value)
    elif isinstance(value, int):
        return ast.Constant(value=value)
    elif isinstance(value, list):
        elts = [_python_to_ast(item) for item in value]
        return ast.List(elts=elts, ctx=ast.Load())
    elif isinstance(value, dict):
        keys = [_python_to_ast(k) for k in value.keys()]
        values = [_python_to_ast(v) for v in value.values()]
        return ast.Dict(keys=keys, values=values)
    else:
        raise ValueError(f"Unsupported value type: {type(value)}")



