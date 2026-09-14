package uclm.esi.alarcos.greenteam.greencoderefactor_java;

import uclm.esi.alarcos.greenteam.greencoderefactor_java.config.LoggerConfig;
import uclm.esi.alarcos.greenteam.greencoderefactor_java.config.LoggerSetupResult;
import uclm.esi.alarcos.greenteam.greencoderefactor_java.transformers.RefactorService;

import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;

public class App {

    private static final LoggerSetupResult loggerSetup = LoggerConfig.setupLogger();
    private static final Logger logger = loggerSetup.getLogger();

    public static void main(String[] args) {

        Map<String, String> argMap = parseArguments(args);

        String input = argMap.get("input");
        String output = argMap.get("output");
        String rulesArg = argMap.get("rules");

        List<String> rules = null;
        if (rulesArg != null && !rulesArg.isEmpty()) {
            rules = Arrays.asList(rulesArg.split(","));
        }

        if (input == null || output == null) {
            logger.severe("Missing required arguments: --input and --output are mandatory.");
            System.exit(1);
        }

        try {
            Map<String, Object> result = RefactorService.runRefactor(
                    input,
                    rules,
                    output
            );

            logger.info("Refactor completed successfully.");
            logger.info("Output directory: " + output);

            if (result.containsKey("message")) {
                logger.info("Message: " + result.get("message"));
            }

        } catch (Exception e) {
            logger.log(Level.SEVERE, "Refactor failed: " + e.getMessage(), e);
            System.exit(1);
        }
    }

    private static Map<String, String> parseArguments(String[] args) {
        Map<String, String> argMap = new HashMap<>();

        for (int i = 0; i < args.length; i++) {
            if (args[i].startsWith("--")) {
                String key = args[i].substring(2);
                String value = (i + 1 < args.length && !args[i + 1].startsWith("--"))
                        ? args[i + 1]
                        : "";

                argMap.put(key, value);

                if (!value.isEmpty()) {
                    i++;
                }
            }
        }

        return argMap;
    }
}
