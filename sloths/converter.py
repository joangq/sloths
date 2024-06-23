from .comparisons import comparison
import inspect
import ast
    
def parse_function(func):
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    source_lines, _ = inspect.getsourcelines(func)
    source = ''.join(source_lines)
    last_decorator_line = source.rfind('def')

    source_lines = source[last_decorator_line:-1] # erase decorators

    module_ast = ast.parse(source)

    # Find the function definition in the AST
    for node in module_ast.body:
        if isinstance(node, ast.FunctionDef) and node.name == func.__name__:
            func_ast = node
            break
    else:
        raise ValueError("Function definition not found in AST")

    return params, func_ast.body

def create_curried_ast(params, body):
    current_body = body # innermost function, contains the original body

    # Start nesting from the last to the first
    for param in reversed(params):
        is_kwarg = param.kind == param.VAR_KEYWORD

        inner_func_name = f'__{param.name}' # fresh def

        args = ast.arguments(
            posonlyargs=[],

            # check if is kwarg because we could have duplicate kwargs
            args=[ast.arg(arg=param.name, annotation=None)] if not is_kwarg else [],
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None if not is_kwarg else ast.arg(arg=param.name, annotation=None),
            defaults=[] if param.default is param.empty else [ast.Constant(value=param.default)]
        )

        return_node = ast.Return(value=ast.Name(id=inner_func_name, ctx=ast.Load()))

        is_innermost = param is params[-1]

        func_def = ast.FunctionDef(
            lineno=1, # dummy
            name=inner_func_name,
            args=args,
            body=current_body,
            decorator_list=[] if not is_innermost else [
                # @comparison.make
                ast.Attribute(value=ast.Name(id='comparison', ctx=ast.Load()), attr='make', ctx=ast.Load())
            ],
        )

        current_body = [func_def, return_node]

    return current_body[0]

def curry(f):
    params, func_body = parse_function(f)
    curried_ast = create_curried_ast(params, func_body)
    curried_ast.name = f.__name__
    code = ast.unparse(curried_ast)
    code = code.replace('\n\n', '\n')
    
    __globals = {'comparison': comparison}
    exec(code, __globals)
    new_f = __globals[f.__name__]
    return new_f

def make_queryable(df):
    def lookup(**kwargs):
        self = df

        result = self
        for kw, val in kwargs.items():
            if kw not in self.columns:
                raise ValueError(f'Column {kw} not found in dataframe.')
            
            if callable(val):
                mask = self[kw].apply(val)
                result = result.where(mask).dropna()
            else:
                result = result[self[kw] == val]

        return result
    
    setattr(df, 'lookup', lookup)

    return df