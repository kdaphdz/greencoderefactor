from trasnsformers.basetransformer import BaseTransformer
import ast


class UnusedLocalVariablesTransformer(BaseTransformer):
    """
    Sonar rule R1481.
    """

    def __init__(self):
        super().__init__()

    def visit_FunctionDef(self, node):
        changed = True
        while changed:
            self.used_vars = self._collect_used_names(node.body)
            new_body = self._remove_unused_all(node.body, self.used_vars)
            changed = len(new_body) != len(node.body)
            node.body = new_body
        if not node.body:
            node.body = [ast.Pass()]
        return node

    def _remove_unused_all(self, stmts, used_vars, global_vars=None):
        if global_vars is None:
            global_vars = set()

        new_body = []
        for stmt in stmts:
            if hasattr(stmt, "body") and isinstance(stmt.body, list):
                stmt.body = self._remove_unused_all(stmt.body, used_vars, global_vars)
                if hasattr(stmt, "orelse") and isinstance(stmt.orelse, list):
                    stmt.orelse = self._remove_unused_all(stmt.orelse, used_vars, global_vars)

            if isinstance(stmt, (ast.Global, ast.Nonlocal)):
                global_vars.update(stmt.names)
                new_body.append(stmt)
                continue

            if isinstance(stmt, ast.Assign):
                if len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                    var_name = stmt.targets[0].id
                    if var_name not in used_vars and var_name not in global_vars:
                        value = stmt.value
                        if isinstance(value, ast.Call):
                            new_body.append(ast.Expr(value=value))
                            self.log_rule(
                                f"{self.__class__.__name__}: Removed unused variable '{var_name}' but kept call at line {getattr(stmt, 'lineno', '?')}"
                            )
                        else:
                            self.log_rule(
                                f"{self.__class__.__name__}: Removed unused variable '{var_name}' at line {getattr(stmt, 'lineno', '?')}"
                            )
                        continue

            elif isinstance(stmt, ast.AugAssign):
                if isinstance(stmt.target, ast.Name):
                    var_name = stmt.target.id
                    if var_name not in used_vars and var_name not in global_vars:
                        self.log_rule(
                            f"{self.__class__.__name__}: Removed unused variable operation '{var_name}' at line {getattr(stmt, 'lineno', '?')}"
                        )
                        continue

            elif isinstance(stmt, ast.Delete):
                new_targets = [
                    target for target in stmt.targets
                    if not (isinstance(target, ast.Name) and target.id not in used_vars and target.id not in global_vars)
                ]
                if not new_targets:
                    self.log_rule(
                        f"{self.__class__.__name__}: Removed del of unused variable(s) at line {getattr(stmt, 'lineno', '?')}"
                    )
                    continue
                else:
                    stmt.targets = new_targets

            new_body.append(stmt)

        if not new_body:
            new_body = [ast.Pass()]

        return new_body

    def _collect_used_names(self, stmts):
        used = set()

        class NameCollector(ast.NodeVisitor):
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    used.add(node.id)

        for stmt in stmts:
            NameCollector().visit(stmt)
        return used
