from trasnsformers.basetransformer import BaseTransformer
import ast

class ExplicitRaiseToExceptBodyTransformer(BaseTransformer):
    """
    Replace explicitly raised exceptions inside a try block
    with the corresponding except body if no alias is used.
    """

    def __init__(self):
        super().__init__()
        self.removed_exceptions = set()
        self.current_module = None

    def visit_Module(self, node):
        self.current_module = node
        self.generic_visit(node)
        self.remove_unused_imports_and_definitions(node)
        return node

    def visit_Try(self, node):
        exc_map = {}
        remaining_handlers = []

        for handler in node.handlers:
            handler_exceptions = []

            if isinstance(handler.type, ast.Name):
                handler_exceptions = [handler.type.id]
            elif isinstance(handler.type, ast.Tuple):
                handler_exceptions = [
                    elt.id for elt in handler.type.elts if isinstance(elt, ast.Name)
                ]
            else:
                return self.generic_visit(node)

            if handler.name:
                if self._alias_is_used(handler.body, handler.name):
                    remaining_handlers.append(handler)
                    continue

            for exc_name in handler_exceptions:
                exc_map[exc_name] = handler.body

        new_body = []
        for stmt in node.body:
            new_stmt = self.replace_raise(stmt, exc_map)
            if isinstance(new_stmt, list):
                new_body.extend(new_stmt)
            else:
                new_body.append(new_stmt)

        self.removed_exceptions.update(exc_map.keys())
        still_raised = self._collect_raised_exceptions(new_body)
        final_handlers = []

        for handler in node.handlers:
            types = []
            if isinstance(handler.type, ast.Name):
                types = [handler.type.id]
            elif isinstance(handler.type, ast.Tuple):
                types = [elt.id for elt in handler.type.elts if isinstance(elt, ast.Name)]

            kept_types = [t for t in types if t in still_raised]

            if kept_types:
                if len(kept_types) == 1:
                    handler.type = ast.Name(id=kept_types[0], ctx=ast.Load())
                else:
                    handler.type = ast.Tuple(
                        elts=[ast.Name(id=t, ctx=ast.Load()) for t in kept_types],
                        ctx=ast.Load()
                    )
                final_handlers.append(handler)

        if final_handlers:
            return ast.Try(
                body=new_body,
                handlers=final_handlers,
                orelse=node.orelse,
                finalbody=node.finalbody,
            )
        else:
            return new_body

    def _alias_is_used(self, stmts, alias_name):
        for node in ast.walk(ast.Module(body=stmts, type_ignores=[])):
            if isinstance(node, ast.Name) and node.id == alias_name:
                return True
        return False

    def _collect_raised_exceptions(self, stmts):
        raised = set()

        class RaiseVisitor(ast.NodeVisitor):
            def visit_Raise(self, node):
                if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
                    raised.add(node.exc.func.id)

        for stmt in stmts:
            RaiseVisitor().visit(stmt)
        return raised

    def replace_raise(self, node, exc_map):
        if isinstance(node, ast.Raise):
            if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
                exc_id = node.exc.func.id
                if exc_id in exc_map:
                    self.log_rule(
                        f"{self.__class__.__name__}: Replaced `raise {exc_id}()` with corresponding except block at line {getattr(node, 'lineno', '?')}."
                    )
                    return exc_map[exc_id]
            return node

        elif isinstance(node, ast.If):
            node.body = self.replace_statements_list(node.body, exc_map)
            node.orelse = self.replace_statements_list(node.orelse, exc_map)
            return node

        elif isinstance(node, ast.Expr):
            node.value = self.replace_raise(node.value, exc_map)
            return node

        return node

    def replace_statements_list(self, stmts, exc_map):
        new_stmts = []
        for stmt in stmts:
            replaced = self.replace_raise(stmt, exc_map)
            if isinstance(replaced, list):
                new_stmts.extend(replaced)
            else:
                new_stmts.append(replaced)
        return new_stmts

    def remove_unused_imports_and_definitions(self, module_node):
        used_names = {node.id for node in ast.walk(module_node) if isinstance(node, ast.Name)}

        def is_exception_unused(name):
            return name in self.removed_exceptions and name not in used_names

        new_body = []
        for stmt in module_node.body:
            if isinstance(stmt, ast.ImportFrom):
                new_names = [alias for alias in stmt.names if not is_exception_unused(alias.name)]
                if new_names:
                    stmt.names = new_names
                    new_body.append(stmt)
            elif isinstance(stmt, ast.Import):
                new_names = [alias for alias in stmt.names if not is_exception_unused(alias.name)]
                if new_names:
                    stmt.names = new_names
                    new_body.append(stmt)
            elif isinstance(stmt, ast.ClassDef):
                if not is_exception_unused(stmt.name):
                    new_body.append(stmt)
            else:
                new_body.append(stmt)

        module_node.body = new_body
