package uclm.esi.alarcos.greenteam.greencoderefactor_java.transformers;

import uclm.esi.alarcos.greenteam.greencoderefactor_java.config.LoggerConfig;
import uclm.esi.alarcos.greenteam.greencoderefactor_java.config.LoggerSetupResult;

import java.nio.file.*;
import java.util.*;
import java.util.logging.Logger;
import java.util.stream.Collectors;

public class RefactorService {

    private static final LoggerSetupResult loggerSetup = LoggerConfig.setupLogger();
    private static final Logger logger = loggerSetup.getLogger();

    public static Map<String, Object> runRefactor(
            String repo,
            String ref,
            List<String> rules,
            String outputDir,
            String ci,
            String runId,
            String workflowName,
            String workflowId,
            String commitHash
    ) {
        logger.info(String.format("[CI=%s] Starting refactor for repo: %s on branch: %s", ci, repo, ref));

        Map<String, Object> result = new HashMap<>();
        Path outputPath = Paths.get(outputDir != null ? outputDir : System.getProperty("java.io.tmpdir"), "greencoderefactor_output");
        Path clonePath = outputPath.resolve("repo");

        try {
            Files.createDirectories(outputPath);
            logger.info("Output directory: " + outputPath);

            String repoUrl;
            if (repo.startsWith("http")) {
                repoUrl = repo; // URL HTTPS
            } else {
                repoUrl = "git@github.com:" + repo + ".git";
            }
            logger.info("Cloning repository from: " + repoUrl);

            ProcessBuilder clonePb = new ProcessBuilder(
                    "git", "clone", "--depth", "1", "--branch", ref, repoUrl, clonePath.toString()
            );
            clonePb.redirectErrorStream(true);
            clonePb.inheritIO();

            Process cloneProcess = clonePb.start();
            int exitCode = cloneProcess.waitFor();
            if (exitCode != 0) {
                String msg = "❌ Failed to clone repository: " + repoUrl;
                logger.severe(msg);
                result.put("message", msg);
                return result;
            }
            logger.info("✅ Repository cloned successfully.");

            List<Path> javaFiles = Files.walk(clonePath)
                    .filter(p -> p.toString().endsWith(".java"))
                    .collect(Collectors.toList());

            if (javaFiles.isEmpty()) {
                String msg = "⚠️ No Java files found in repository.";
                logger.warning(msg);
                result.put("message", msg);
                return result;
            }

            Path transformedDir = outputPath.resolve("transformed");
            Files.createDirectories(transformedDir);

            List<Map<String, Object>> fileResults = new ArrayList<>();

            for (Path file : javaFiles) {
                Path relative = clonePath.relativize(file);
                Path outputFile = transformedDir.resolve(relative);
                Files.createDirectories(outputFile.getParent());

                logger.info("🔧 Transforming file: " + file);
                try {
                    Map<String, Object> res = TransformerRunner.transformCode(file, outputFile, rules);
                    fileResults.add(res);
                } catch (Exception e) {
                    logger.warning("⚠️ Could not transform file " + file + ": " + e.getMessage());
                }
            }

            long changedCount = fileResults.stream().filter(r -> (boolean) r.get("changed")).count();
            result.put("changed_files", changedCount);
            result.put("total_files", fileResults.size());
            result.put("message", "Transformation completed. Changed " + changedCount + " of " + fileResults.size() + " files.");
            result.put("output_dir", transformedDir.toString());

            logger.info("Refactor finished. Changed " + changedCount + " of " + fileResults.size() + " files.");

        } catch (Exception e) {
            String msg = "Refactor failed: " + e.getMessage();
            logger.severe(msg);
            result.put("message", msg);
            e.printStackTrace();
        }

        return result;
    }
}
