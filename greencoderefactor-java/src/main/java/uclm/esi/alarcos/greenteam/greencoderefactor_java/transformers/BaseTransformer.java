package uclm.esi.alarcos.greenteam.greencoderefactor_java.transformers;

import com.github.javaparser.ast.CompilationUnit;
import uclm.esi.alarcos.greenteam.greencoderefactor_java.config.LoggerConfig;
import uclm.esi.alarcos.greenteam.greencoderefactor_java.config.LoggerSetupResult;

import java.util.ArrayList;
import java.util.List;
import java.util.logging.Logger;

public abstract class BaseTransformer {

    protected static final LoggerSetupResult loggerSetup = LoggerConfig.setupLogger();
    protected static final Logger logger = loggerSetup.getLogger();
    protected final List<String> appliedRules = new ArrayList<>();

    protected void logRule(String message) {
        appliedRules.add(message);
        logger.info("Applied rule: " + message);
    }

    public List<String> getAppliedRules() {
        return appliedRules;
    }

    public abstract CompilationUnit transform(CompilationUnit cu);
}
