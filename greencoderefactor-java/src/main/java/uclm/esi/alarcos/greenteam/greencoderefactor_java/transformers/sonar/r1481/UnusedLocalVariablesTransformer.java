package uclm.esi.alarcos.greenteam.greencoderefactor_java.transformers.sonar.r1481;

import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.stmt.*;
import com.github.javaparser.ast.visitor.ModifierVisitor;
import com.github.javaparser.ast.visitor.Visitable;
import uclm.esi.alarcos.greenteam.greencoderefactor_java.transformers.BaseTransformer;

import java.util.HashSet;
import java.util.Set;

/**
 * Transformer Sonar R1481:
 */
public class UnusedLocalVariablesTransformer extends BaseTransformer {

    @Override
    public CompilationUnit transform(CompilationUnit cu) {

        ModifierVisitor<Void> transformer = new ModifierVisitor<>() {

            @Override
            public Visitable visit(MethodDeclaration md, Void arg) {
                if (md.getBody().isEmpty()) return md;

                boolean changed = true;
                while (changed) {
                    BlockStmt originalBody = md.getBody().orElse(new BlockStmt());
                    Set<String> usedVars = collectUsedVariables(originalBody);
                    BlockStmt newBody = removeUnusedAssignments(originalBody, usedVars);

                    changed = !originalBody.equals(newBody);
                    md.setBody(newBody);
                }

                if (md.getBody().isPresent() && md.getBody().get().isEmpty()) {
                    BlockStmt body = new BlockStmt();
                    body.addStatement(new EmptyStmt());
                    md.setBody(body);
                }

                return super.visit(md, arg);
            }

            private Set<String> collectUsedVariables(BlockStmt body) {
                Set<String> used = new HashSet<>();
                body.walk(NameExpr.class, nameExpr -> used.add(nameExpr.getNameAsString()));
                return used;
            }

            private BlockStmt removeUnusedAssignments(BlockStmt body, Set<String> usedVars) {
                BlockStmt newBody = new BlockStmt();

                for (Statement stmt : body.getStatements()) {
                	
                    if (stmt.isBlockStmt()) {
                        newBody.addStatement(removeUnusedAssignments(stmt.asBlockStmt(), usedVars));
                        continue;
                    }

                    if (stmt.isIfStmt()) {
                        IfStmt ifStmt = stmt.asIfStmt();
                        ifStmt.setThenStmt(removeUnusedAssignments(getBlock(ifStmt.getThenStmt()), usedVars));
                        ifStmt.getElseStmt().ifPresent(elseStmt ->
                                ifStmt.setElseStmt(removeUnusedAssignments(getBlock(elseStmt), usedVars))
                        );
                        newBody.addStatement(ifStmt);
                        continue;
                    }

                    if (stmt.isExpressionStmt()) {
                        Expression expr = stmt.asExpressionStmt().getExpression();

                        if (expr.isVariableDeclarationExpr()) {
                            VariableDeclarationExpr decl = expr.asVariableDeclarationExpr();
                            NodeList<VariableDeclarator> newVars = new NodeList<>();

                            for (VariableDeclarator var : decl.getVariables()) {
                                String varName = var.getNameAsString();
                                if (!usedVars.contains(varName)) {
                                    if (var.getInitializer().isPresent()
                                            && var.getInitializer().get().isMethodCallExpr()) {
                                        newBody.addStatement(new ExpressionStmt(var.getInitializer().get()));
                                        logRule(String.format(
                                                "%s: Removed unused variable '%s' but kept call at line %d",
                                                this.getClass().getSimpleName(),
                                                varName,
                                                stmt.getBegin().map(p -> p.line).orElse(-1)
                                        ));
                                    } else {
                                        logRule(String.format(
                                                "%s: Removed unused local variable '%s' at line %d",
                                                this.getClass().getSimpleName(),
                                                varName,
                                                stmt.getBegin().map(p -> p.line).orElse(-1)
                                        ));
                                    }
                                } else {
                                    newVars.add(var);
                                }
                            }

                            if (!newVars.isEmpty()) {
                                VariableDeclarationExpr newDecl = new VariableDeclarationExpr(newVars);
                                newBody.addStatement(new ExpressionStmt(newDecl));
                            }

                            continue;
                        }

                        if (expr.isAssignExpr()) {
                            AssignExpr assign = expr.asAssignExpr();
                            if (assign.getTarget().isNameExpr()) {
                                String varName = assign.getTarget().asNameExpr().getNameAsString();
                                if (!usedVars.contains(varName)) {
                                    logRule(String.format(
                                            "%s: Removed unused assignment to '%s' at line %d",
                                            this.getClass().getSimpleName(),
                                            varName,
                                            stmt.getBegin().map(p -> p.line).orElse(-1)
                                    ));
                                    if (assign.getValue().isMethodCallExpr()) {
                                        newBody.addStatement(new ExpressionStmt(assign.getValue()));
                                    }
                                    continue;
                                }
                            }
                        }

                        if (expr.isAssignExpr() && expr.asAssignExpr().getOperator() != AssignExpr.Operator.ASSIGN) {
                            AssignExpr assign = expr.asAssignExpr();
                            if (assign.getTarget().isNameExpr()) {
                                String varName = assign.getTarget().asNameExpr().getNameAsString();
                                if (!usedVars.contains(varName)) {
                                    logRule(String.format(
                                            "%s: Removed unused augmented assignment '%s' at line %d",
                                            this.getClass().getSimpleName(),
                                            varName,
                                            stmt.getBegin().map(p -> p.line).orElse(-1)
                                    ));
                                    continue;
                                }
                            }
                        }

                        newBody.addStatement(stmt);
                        continue;
                    }

                    newBody.addStatement(stmt);
                }

                if (newBody.isEmpty()) {
                    newBody.addStatement(new EmptyStmt());
                }

                return newBody;
            }

            private BlockStmt getBlock(Statement stmt) {
                if (stmt.isBlockStmt()) {
                    return stmt.asBlockStmt();
                } else {
                    BlockStmt block = new BlockStmt();
                    block.addStatement(stmt);
                    return block;
                }
            }
        };

        transformer.visit(cu, null);
        return cu;
    }
}
