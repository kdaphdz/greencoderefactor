package uclm.esi.alarcos.greenteam.greencoderefactor_java.config;

import java.io.IOException;
import java.nio.file.*;
import java.util.logging.*;

public class LoggerConfig {

    private static Logger logger;
    private static String logDir;

    public static LoggerSetupResult setupLogger() {
        if (logger != null && logDir != null) {
            return new LoggerSetupResult(logger, logDir);
        }

        try {
            String home = System.getProperty("user.home");
            logDir = Paths.get(home, "greencoderefactor").toString();
            Files.createDirectories(Paths.get(logDir));
            String logFilePath = Paths.get(logDir, "app.log").toString();

            logger = Logger.getLogger("greencoderefactor");
            logger.setUseParentHandlers(false);

            if (logger.getHandlers().length == 0) {
                Formatter formatter = new SimpleFormatter();

                FileHandler fileHandler = new FileHandler(logFilePath, true);
                fileHandler.setFormatter(formatter);
                logger.addHandler(fileHandler);

                ConsoleHandler consoleHandler = new ConsoleHandler();
                consoleHandler.setFormatter(formatter);
                logger.addHandler(consoleHandler);

                logger.setLevel(Level.INFO);
            }

        } catch (IOException e) {
            System.err.println("Failed to initialize logger: " + e.getMessage());
        }

        return new LoggerSetupResult(logger, logDir);
    }
}

