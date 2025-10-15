import ast
import os
import difflib
from config.logger import setup_logger
from trasnsformers import (
    ExplicitRaiseToExceptBodyTransformer,
    UnusedLocalVariablesTransformer,
    UnusedAssignmentTransformer
)

logger, log_dir = setup_logger()

ALL_TRANSFORMERS = {
    "ExplicitRaiseToExceptBodyTransformer": ExplicitRaiseToExceptBodyTransformer,
    "UnusedLocalVariablesTransformer": UnusedLocalVariablesTransformer,
    "UnusedAssignmentTransformer": UnusedAssignmentTransformer,
}


def select_transformers(rules):
    candidates = list(ALL_TRANSFORMERS.values())
    if rules is None:
        logger.info("No rules provided, no transformers selected.")
        return []
    filtered = []
    for rule_name in rules:
        cls = ALL_TRANSFORMERS.get(rule_name)
        if cls and cls in candidates:
            filtered.append(cls)
        else:
            logger.warning(f"Rule '{rule_name}' not found among available transformers.")
    candidates = filtered
    logger.info(f"Selected transformers: {[cls.__name__ for cls in candidates]}")
    return [cls() for cls in candidates]


def transform_code(file_path, output_path, rules):
    transformers = select_transformers(rules)

    if not transformers:
        logger.info(f"No transformers to apply for {file_path}, skipping transformation.")
        return {"file": file_path, "changed": False, "rules": []}

    logger.info(f"Reading file {file_path} for transformation.")
    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()

    applied_rules_total = []
    final_code = original_code
    changed_any = False

    # Cada transformador se aplica de forma independiente al código original
    for transformer in transformers:
        try:
            tree = ast.parse(original_code)  # Siempre desde el original
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path} before applying {transformer.__class__.__name__}: {e}")
            continue
        except Exception as e:
            logger.error(f"Error parsing {file_path} before applying {transformer.__class__.__name__}: {e}")
            continue

        try:
            tree = transformer.visit(tree)
            ast.fix_missing_locations(tree)
            transformed_code = ast.unparse(tree)

            applied_rules = getattr(transformer, "applied_rules", [])
            if applied_rules:
                applied_rules_total.extend(applied_rules)
                changed_any = True
                # Actualizamos final_code solo si hubo cambios
                final_code = transformed_code
        except Exception as e:
            logger.error(f"Error applying {transformer.__class__.__name__} to {file_path}: {e}")
            continue

    if changed_any:
        logger.info(f"Changes detected in {file_path}, writing transformed code to {output_path}.")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_code)

    # Generar diff
    diff = ""
    if changed_any:
        diff = "".join(difflib.unified_diff(
            original_code.splitlines(keepends=True),
            final_code.splitlines(keepends=True),
            fromfile=f"{file_path} (original)",
            tofile=f"{output_path} (transformed)"
        ))

    log_content = (
        f"Input file: {file_path}\n"
        f"Output file: {output_path}\n\n"
        f"Applied Rules:\n" +
        ("\n".join(applied_rules_total) if applied_rules_total else "No rules were triggered.") +
        "\n\nChanges (diff):\n" +
        (diff if diff else "No changes detected.") +
        "\n\n---\n\n"
    )

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "transformations.log")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(log_content)
    logger.info(f"Transformation log appended for {file_path}.")

    return {"file": file_path, "changed": changed_any, "rules": applied_rules_total}
