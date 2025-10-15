package uclm.esi.alarcos.greenteam.greencoderefactor_java.config;

import java.util.logging.Logger;

public class LoggerSetupResult {
    private final Logger logger;
    private final String logDir;

    public LoggerSetupResult(Logger logger, String logDir) {
        this.logger = logger;
        this.logDir = logDir;
    }

    public Logger getLogger() {
        return logger;
    }

    public String getLogDir() {
        return logDir;
    }
}
