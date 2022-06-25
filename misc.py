def not_implemented(message: str = ""):
    print(f"TODO: {message} not implemented")
    exit(1)


def report_error(message: str, file: str, line: int):
    print(f"{file}:{line}:")
    print(f"Compilation error: {message}")
    exit(1)


def operator_predence(operator: str) -> int:
    p = 0

    p = p+1
    if operator in ["||", "&&"]:
        return p

    p = p+1
    if operator in ["==", "!="]:
        return p

    p = p+1
    if operator in ["<", ">"]:
        return p

    p = p+1
    if operator in ["+", "-"]:
        return p

    p = p+1
    if operator in ["*", "/", "%"]:
        return p

    p = p+1
    if operator in ["!", "^"]:
        return p

    return 0


binary_operators = ["+", "-", "/", "*", "%", "<", ">", "&&", "||", "==", "!="]
unary_operators = ["!", "^"]

operator_list = binary_operators + unary_operators + ["(", ")"]
