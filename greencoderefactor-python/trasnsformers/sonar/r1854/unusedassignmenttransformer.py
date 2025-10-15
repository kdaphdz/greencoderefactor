import ast
from trasnsformers.basetransformer import BaseTransformer

class UnusedAssignmentTransformer(BaseTransformer):
    """
    Sonar rule R1854.
    """

    def visit(self, node):
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, ast.stmt):
                        new_list.append(self.visit(item))
                    else:
                        new_list.append(item)
                setattr(node, field, self._remove_consecutive_dead_stores(new_list))
            elif isinstance(value, ast.AST):
                setattr(node, field, self.visit(value))
        return node

    def _remove_consecutive_dead_stores(self, stmts):
        new_body = []
        last_var = None
        last_stmt = None

        for stmt in stmts:
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                var_name = self._get_var_name(stmt.targets[0])
                if var_name:
                    if last_var == var_name and last_stmt in new_body:
                        used_in_current = self._find_used_names(stmt)
                        if last_var not in used_in_current:
                            new_body.remove(last_stmt)
                            self.log_rule(
                                f"{self.__class__.__name__}: Removed consecutive dead store to '{var_name}' at line {last_stmt.lineno}"
                            )

                    last_var = var_name
                    last_stmt = stmt
                else:
                    last_var = None
                    last_stmt = None
            else:
                last_var = None
                last_stmt = None

            new_body.append(stmt)

        return new_body

    def _get_var_name(self, target):
        if isinstance(target, ast.Name):
            return target.id
        elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
            return f"{target.value.id}.{target.attr}"
        return None

    def _find_used_names(self, node):
        used = set()

        class Visitor(ast.NodeVisitor):
            def visit_Name(self, n):
                if isinstance(n.ctx, ast.Load):
                    used.add(n.id)

            def visit_Attribute(self, n):
                if isinstance(n.ctx, ast.Load) and isinstance(n.value, ast.Name):
                    used.add(f"{n.value.id}.{n.attr}")
                self.generic_visit(n)

        Visitor().visit(node)
        return used
