package uclm.esi.alarcos.greenteam.greencoderefactor_java.transformers;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import uclm.esi.alarcos.greenteam.greencoderefactor_java.transformers.sonar.r1481.UnusedLocalVariablesTransformer;
import uclm.esi.alarcos.greenteam.greencoderefactor_java.transformers.sonar.r1854.UnusedAssignmentTransformer;
import uclm.esi.alarcos.greenteam.greencoderefactor_java.transformers.techniques.t10.ExplicitRaiseToExceptBodyTransformer;
import uclm.esi.alarcos.greenteam.greencoderefactor_java.config.LoggerConfig;
import uclm.esi.alarcos.greenteam.greencoderefactor_java.config.LoggerSetupResult;

import com.github.difflib.DiffUtils;
import com.github.difflib.patch.AbstractDelta;
import com.github.difflib.patch.Patch;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import java.util.logging.Logger;
import java.util.stream.Collectors;

public class TransformerRunner {

    private static final LoggerSetupResult loggerSetup = LoggerConfig.setupLogger();
    private static final Logger logger = loggerSetup.getLogger();
    private static final Path LOG_DIR = Paths.get(loggerSetup.getLogDir());
    private static final Path LOG_FILE = LOG_DIR.resolve("transformations.log");

    private static final Map<String, Class<? extends BaseTransformer>> ALL_TRANSFORMERS = Map.of(
            "ExplicitRaiseToExceptBodyTransformer", ExplicitRaiseToExceptBodyTransformer.class,
            "UnusedLocalVariablesTransformer", UnusedLocalVariablesTransformer.class,
            "UnusedAssignmentTransformer", UnusedAssignmentTransformer.class
    );

    public static List<BaseTransformer> selectTransformers(List<String> rules) {
        if (rules == null || rules.isEmpty()) {
            logger.info("No rules provided, no transformers selected.");
            return Collections.emptyList();
        }

        List<BaseTransformer> selected = new ArrayList<>();
        for (String ruleName : rules) {
            Class<? extends BaseTransformer> transformerClass = ALL_TRANSFORMERS.get(ruleName);
            if (transformerClass != null) {
                try {
                    selected.add(transformerClass.getDeclaredConstructor().newInstance());
                } catch (Exception e) {
                    logger.warning("Could not instantiate transformer: " + ruleName + " -> " + e.getMessage());
                }
            } else {
                logger.warning("Rule '" + ruleName + "' not found among available transformers.");
            }
        }

        logger.info("Selected transformers: " + selected.stream()
                .map(t -> t.getClass().getSimpleName())
                .collect(Collectors.toList()));
        return selected;
    }

    public static Map<String, Object> transformCode(Path filePath, Path outputPath, List<String> rules) throws IOException {

        List<BaseTransformer> transformers = selectTransformers(rules);

        if (transformers.isEmpty()) {
            logger.info("No transformers to apply for " + filePath + ", skipping transformation.");
            return Map.of("file", filePath.toString(), "changed", false, "rules", Collections.emptyList());
        }

        logger.info("Reading file " + filePath + " for transformation.");
        String originalCode = Files.readString(filePath);

        boolean changedAny = false;
        String finalCode = originalCode;
        List<String> appliedRulesTotal = new ArrayList<>();

        for (BaseTransformer transformer : transformers) {
            CompilationUnit cu;
            try {
                cu = StaticJavaParser.parse(originalCode);
            } catch (Exception e) {
                logger.warning("Syntax error parsing " + filePath + " before applying " +
                        transformer.getClass().getSimpleName() + ": " + e.getMessage());
                continue;
            }

            CompilationUnit transformed;
            try {
                transformed = transformer.transform(cu);
            } catch (Exception e) {
                logger.warning("Error applying " + transformer.getClass().getSimpleName() +
                        " to " + filePath + ": " + e.getMessage());
                continue;
            }

            List<String> appliedRules = transformer.getAppliedRules();

            if (!appliedRules.isEmpty()) {
                changedAny = true;
                appliedRulesTotal.addAll(appliedRules);
                finalCode = transformed.toString();
            }
        }

        if (changedAny) {
            logger.info("Changes detected in " + filePath + ", writing transformed code to " + outputPath + ".");
            Files.createDirectories(outputPath.getParent());
            Files.writeString(outputPath, finalCode);
        } else {
            logger.info("No changes detected in " + filePath + " after applying transformers.");
        }

        String diff = "";
        if (changedAny) {
            List<String> originalLines = Arrays.asList(originalCode.split("\n"));
            List<String> transformedLines = Arrays.asList(finalCode.split("\n"));
            Patch<String> patch = DiffUtils.diff(originalLines, transformedLines);
            StringBuilder diffBuilder = new StringBuilder();
            for (AbstractDelta<String> delta : patch.getDeltas()) {
                diffBuilder.append(delta).append("\n");
            }
            diff = diffBuilder.toString();
        }

        String logContent = String.format(
                "Input file: %s%nOutput file: %s%n%nApplied Rules:%n%s%n%nChanges (diff):%n%s%n%n---%n%n",
                filePath, outputPath,
                appliedRulesTotal.isEmpty() ? "No rules were triggered." : String.join("\n", appliedRulesTotal),
                changedAny ? diff : "No changes detected."
        );

        Files.createDirectories(LOG_DIR);
        try (BufferedWriter writer = Files.newBufferedWriter(LOG_FILE, StandardOpenOption.CREATE, StandardOpenOption.APPEND)) {
            writer.write(logContent);
        }

        logger.info("Transformation log appended for " + filePath + ".");

        return Map.of(
                "file", filePath.toString(),
                "changed", changedAny,
                "rules", appliedRulesTotal
        );
    }
}
