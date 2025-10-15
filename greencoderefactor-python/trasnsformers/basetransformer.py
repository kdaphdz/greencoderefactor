import ast
from config.logger import setup_logger

logger, _ = setup_logger()

class BaseTransformer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.applied_rules = []

    def log_rule(self, message: str):
        self.applied_rules.append(message)
        logger.info(f"Applied rule: {message}")
