package uclm.esi.alarcos.greenteam.greencoderefactor_java.transformers.techniques.t10;

import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.expr.ObjectCreationExpr;
import com.github.javaparser.ast.stmt.*;
import com.github.javaparser.ast.visitor.ModifierVisitor;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.github.javaparser.ast.visitor.Visitable;
import uclm.esi.alarcos.greenteam.greencoderefactor_java.transformers.BaseTransformer;

import java.util.HashSet;
import java.util.Set;

public class ExplicitRaiseToExceptBodyTransformer extends BaseTransformer {

    @Override
    public CompilationUnit transform(CompilationUnit cu) {

        Set<String> definedExceptions = new HashSet<>();
        for (var type : cu.getTypes()) {
            if (type instanceof ClassOrInterfaceDeclaration cid) {
                if (cid.getExtendedTypes().stream()
                        .anyMatch(et -> et.getNameAsString().equals("Exception"))) {
                    definedExceptions.add(cid.getNameAsString());
                }
            }
        }

        ModifierVisitor<Void> transformer = new ModifierVisitor<>() {

            private boolean matchesCaughtException(ThrowStmt ts, String caughtException) {
                if (ts.getExpression() instanceof ObjectCreationExpr oce) {
                    return oce.getType().getNameAsString().equals(caughtException);
                }
                return false;
            }

            private boolean containsThrowForException(BlockStmt block, String caughtException) {
                return block.findAll(ThrowStmt.class).stream()
                        .anyMatch(ts -> matchesCaughtException(ts, caughtException));
            }

            @Override
            public Visitable visit(TryStmt n, Void arg) {
                if (n.getCatchClauses().size() == 1) {
                    CatchClause cc = n.getCatchClauses().get(0);
                    String caughtException = cc.getParameter().getType().asString();
                    BlockStmt catchBody = cc.getBody();

                    if (n.getTryBlock().getStatements().size() == 1 &&
                        n.getTryBlock().getStatement(0).isIfStmt()) {

                        IfStmt ifStmt = n.getTryBlock().getStatement(0).asIfStmt();

                        if (ifStmt.getElseStmt().isPresent()) {
                            Statement elseStmt = ifStmt.getElseStmt().get();

                            boolean shouldReplace = false;
                            if (elseStmt.isThrowStmt() &&
                                matchesCaughtException(elseStmt.asThrowStmt(), caughtException)) {
                                shouldReplace = true;
                            } else if (elseStmt.isBlockStmt() &&
                                containsThrowForException(elseStmt.asBlockStmt(), caughtException)) {
                                shouldReplace = true;
                            }

                            if (shouldReplace) {
                                int line = elseStmt.getBegin().map(p -> p.line).orElse(-1);
                                ifStmt.setElseStmt(catchBody.getStatement(0));
                                logRule(String.format(
                                    "%s: Replaced `throw %s` with corresponding catch block at line %d.",
                                    this.getClass().getName(),
                                    caughtException,
                                    line
                                ));
                                return ifStmt;
                            }
                        }
                    }
                }
                return super.visit(n, arg);
            }
        };

        transformer.visit(cu, null);

        Set<String> usedExceptions = new HashSet<>();
        cu.accept(new VoidVisitorAdapter<Void>() {
            @Override
            public void visit(ThrowStmt n, Void arg) {
                super.visit(n, arg);
                if (n.getExpression() instanceof ObjectCreationExpr oce) {
                    String exceptionName = oce.getType().getNameAsString();
                    if (definedExceptions.contains(exceptionName)) {
                        usedExceptions.add(exceptionName);
                    }
                }
            }
        }, null);

        definedExceptions.stream()
                .filter(exc -> !usedExceptions.contains(exc))
                .forEach(unused -> cu.getTypes().removeIf(type ->
                        type instanceof ClassOrInterfaceDeclaration cid &&
                                cid.getNameAsString().equals(unused))
                );

        return cu;
    }
}