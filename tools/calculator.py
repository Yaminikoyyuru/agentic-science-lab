import ast
import operator as op


_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def calculate(expression):

    node = ast.parse(
        expression,
        mode="eval"
    ).body

    return _evaluate(node)


def _evaluate(node):

    if isinstance(node, ast.Constant) and isinstance(
        node.value,
        (int, float)
    ):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:

        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError(
                "Exponent too large."
            )

        return _ALLOWED_OPERATORS[type(node.op)](
            left,
            right
        )

    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:

        return _ALLOWED_OPERATORS[type(node.op)](
            _evaluate(node.operand)
        )

    raise ValueError(
        "Unsupported mathematical expression."
    )
