package uclm.esi.alarcos.greenteam.greencoderefactor_java.transformers.sonar.r1854;

import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.stmt.*;
import com.github.javaparser.ast.visitor.ModifierVisitor;
import com.github.javaparser.ast.visitor.Visitable;
import uclm.esi.alarcos.greenteam.greencoderefactor_java.transformers.BaseTransformer;

import java.util.*;

/**
 * Transformer Sonar R1854:
 */
public class UnusedAssignmentTransformer extends BaseTransformer {

    @Override
    public CompilationUnit transform(CompilationUnit cu) {

        ModifierVisitor<Void> transformer = new ModifierVisitor<>() {

            @Override
            public Visitable visit(MethodDeclaration md, Void arg) {
                if (md.getBody().isEmpty()) return md;

                BlockStmt body = md.getBody().get();
                BlockStmt newBody = removeConsecutiveDeadStores(body);
                md.setBody(newBody);

                return super.visit(md, arg);
            }

            private BlockStmt removeConsecutiveDeadStores(BlockStmt body) {
                List<Statement> statements = body.getStatements();
                List<Statement> newBody = new ArrayList<>();

                String lastVar = null;
                Statement lastStmt = null;

                for (Statement stmt : statements) {
                    if (stmt.isExpressionStmt()) {
                        Expression expr = stmt.asExpressionStmt().getExpression();

                        if (expr.isAssignExpr()) {
                            AssignExpr assign = expr.asAssignExpr();
                            String varName = extractTargetId(assign.getTarget());

                            if (varName != null) {
                                if (lastVar != null && lastVar.equals(varName) && newBody.contains(lastStmt)) {
                                    Set<String> usedNames = findUsedNames(assign);
                                    if (!usedNames.contains(lastVar)) {
                                        newBody.remove(lastStmt);
                                        logRule(String.format(
                                                "%s: Removed consecutive dead store to '%s' at line %d",
                                                this.getClass().getSimpleName(),
                                                varName,
                                                lastStmt.getBegin().map(p -> p.line).orElse(-1)
                                        ));
                                    }
                                }

                                lastVar = varName;
                                lastStmt = stmt;
                                newBody.add(stmt);
                                continue;
                            }
                        }
                    }

                    lastVar = null;
                    lastStmt = null;
                    newBody.add(stmt);
                }

                BlockStmt cleaned = new BlockStmt();
                newBody.forEach(cleaned::addStatement);
                return cleaned;
            }

            private Set<String> findUsedNames(Node node) {
                Set<String> used = new HashSet<>();

                node.walk(NameExpr.class, ne -> used.add(ne.getNameAsString()));
                node.walk(FieldAccessExpr.class, fae -> {
                    if (fae.getScope().isNameExpr()) {
                        used.add(fae.getScope().asNameExpr().getNameAsString() + "." + fae.getNameAsString());
                    }
                });

                return used;
            }

            private String extractTargetId(Expression target) {
                if (target.isNameExpr()) {
                    return target.asNameExpr().getNameAsString();
                }
                if (target.isFieldAccessExpr()) {
                    FieldAccessExpr fae = target.asFieldAccessExpr();
                    if (fae.getScope().isNameExpr()) {
                        return fae.getScope().asNameExpr().getNameAsString() + "." + fae.getNameAsString();
                    }
                }
                return null;
            }
        };

        transformer.visit(cu, null);
        return cu;
    }
}

