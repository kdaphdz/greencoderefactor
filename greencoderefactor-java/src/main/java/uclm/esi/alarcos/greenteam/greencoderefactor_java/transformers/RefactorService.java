package uclm.esi.alarcos.greenteam.greencoderefactor_java.transformers;

import uclm.esi.alarcos.greenteam.greencoderefactor_java.config.LoggerConfig;
import uclm.esi.alarcos.greenteam.greencoderefactor_java.config.LoggerSetupResult;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import java.util.logging.Logger;
import java.util.stream.Collectors;

public class RefactorService {

    private static final LoggerSetupResult loggerSetup = LoggerConfig.setupLogger();
    private static final Logger logger = loggerSetup.getLogger();

    public static Map<String, Object> runRefactor(
            String inputDir,
            List<String> rules,
            String outputDir
    ) {

        logger.info("Starting refactor for directory: " + inputDir);

        Map<String, Object> result = new HashMap<>();

        Path inputPath = Paths.get(inputDir).toAbsolutePath().normalize();
        Path outputPath = Paths.get(outputDir).toAbsolutePath().normalize();

        try {

            if (!Files.exists(inputPath) || !Files.isDirectory(inputPath)) {
                String msg = "Input directory does not exist: " + inputDir;
                logger.severe(msg);
                result.put("message", msg);
                return result;
            }

            Files.createDirectories(outputPath);

            logger.info("Input directory: " + inputPath);
            logger.info("Output directory: " + outputPath);

            if (rules == null || rules.isEmpty()) {
                String msg = "No transformation rules specified.";
                logger.warning(msg);
                result.put("message", msg);
                result.put("output_dir", outputPath.toString());
                return result;
            }

            boolean inPlace = inputPath.equals(outputPath);

            if (inPlace) {
                logger.info(
                        "Input and output directories are the same. "
                                + "Using temporary files for in-place transformation."
                );
            }

            Path tempDir = null;

            if (inPlace) {
                tempDir = Files.createTempDirectory(
                        "greencoderefactor_inplace_"
                );
            }

            try {

                List<Path> javaFiles = Files.walk(inputPath)
                        .filter(Files::isRegularFile)
                        .filter(p -> p.toString().endsWith(".java"))
                        .collect(Collectors.toList());

                if (javaFiles.isEmpty()) {
                    String msg = "No Java files found in input directory.";
                    logger.warning(msg);
                    result.put("message", msg);
                    result.put("output_dir", outputPath.toString());
                    return result;
                }

                List<Map<String, Object>> fileResults = new ArrayList<>();

                for (Path file : javaFiles) {

                    Path relative = inputPath.relativize(file);

                    Path transformationOutput;

                    if (inPlace) {

                        transformationOutput = tempDir.resolve(relative);

                        Files.createDirectories(
                                transformationOutput.getParent()
                        );

                    } else {

                        transformationOutput = outputPath.resolve(relative);

                        Files.createDirectories(
                                transformationOutput.getParent()
                        );
                    }

                    logger.info("Transforming file: " + file);

                    try {

                        Map<String, Object> res =
                                TransformerRunner.transformCode(
                                        file,
                                        transformationOutput,
                                        rules
                                );

                        if (res != null
                                && Boolean.TRUE.equals(res.get("changed"))) {

                            if (inPlace) {

                                Files.move(
                                        transformationOutput,
                                        file,
                                        StandardCopyOption.REPLACE_EXISTING
                                );

                                logger.info(
                                        "Changes detected. Replaced original file: "
                                                + file
                                );

                            } else {

                                logger.info(
                                        "Changes detected. Transformed file written to: "
                                                + transformationOutput
                                );
                            }

                        } else {

                            if (!inPlace) {

                                if (!Files.exists(transformationOutput)) {

                                    Files.copy(
                                            file,
                                            transformationOutput
                                    );

                                    logger.info(
                                            "No transformations applied. "
                                                    + "Copied original file: "
                                                    + file
                                    );

                                } else {

                                    logger.info(
                                            "No transformations applied. "
                                                    + "Output file already exists: "
                                                    + transformationOutput
                                    );
                                }

                            } else {

                                logger.info(
                                        "No transformations applied: "
                                                + file
                                );
                            }
                        }

                        fileResults.add(res);

                    } catch (Exception e) {

                        logger.warning(
                                "Could not transform file "
                                        + file
                                        + ": "
                                        + e.getMessage()
                        );
                    }
                }

                long changedCount = fileResults.stream()
                        .filter(Objects::nonNull)
                        .filter(r -> Boolean.TRUE.equals(r.get("changed")))
                        .count();

                result.put("changed_files", changedCount);
                result.put("total_files", fileResults.size());
                result.put("output_dir", outputPath.toString());

                String message =
                        "Transformation completed. Changed "
                                + changedCount
                                + " of "
                                + fileResults.size()
                                + " files.";

                result.put("message", message);

                logger.info(message);

            } finally {

                if (tempDir != null && Files.exists(tempDir)) {

                    try {

                        Files.walk(tempDir)
                                .sorted(Comparator.reverseOrder())
                                .forEach(path -> {
                                    try {
                                        Files.deleteIfExists(path);
                                    } catch (IOException e) {
                                        logger.warning(
                                                "Could not delete temporary file: "
                                                        + path
                                                        + ": "
                                                        + e.getMessage()
                                        );
                                    }
                                });

                    } catch (IOException e) {

                        logger.warning(
                                "Could not clean temporary directory: "
                                        + tempDir
                                        + ": "
                                        + e.getMessage()
                        );
                    }
                }
            }

        } catch (Exception e) {

            String msg = "Refactor failed: " + e.getMessage();

            logger.severe(msg);

            result.put("message", msg);
            result.put("output_dir", outputPath.toString());
        }

        return result;
    }
}