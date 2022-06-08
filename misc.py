from enum import auto


def not_implemented(message: str = ""):
    print(f"TODO: {message} not implemented")
    exit(1)


def operator_predence(operator: str) -> int:
    p = 0

    p=p+1
    if operator in [ "||", "&&"]:
        return p
    
    p=p+1
    if operator in [ "=="]:
        return p
    
    p=p+1
    if operator in ["<", ">"]:
        return p

    p=p+1
    if operator in ["+", "-"]:
        return p

    p=p+1
    if operator in ["*", "/", "%"]:
        return p    
    
    p=p+1
    if operator in ["!", "^"]:
        return p    

    return 0


binary_operators = ["+", "-", "/", "*", "%", "<", ">", "&&", "||", "=="]
unary_operators = ["!", "^"]

operator_list = binary_operators + unary_operators + ["(", ")"]
