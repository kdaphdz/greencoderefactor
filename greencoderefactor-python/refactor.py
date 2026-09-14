import os
import shutil
import tempfile

from config.logger import setup_logger
from trasnsformers.transform import transform_code

logger, _ = setup_logger()


def run_refactor(
    input_dir: str,
    rules=None,
    output_dir: str = None,
):
    logger.info(f"Starting refactor for directory: {input_dir}")

    empty_result = {
        "transformations": [],
        "message": None,
        "output_dir": output_dir,
    }

    if not rules:
        logger.info("No transformation rules specified: skipping refactor")
        empty_result["message"] = (
            "No transformation rules provided; no refactor performed"
        )
        return empty_result

    if not os.path.isdir(input_dir):
        raise ValueError(f"Input directory does not exist: {input_dir}")

    if output_dir is None:
        output_dir = tempfile.mkdtemp(
            prefix="greencoderefactor_output_"
        )
        logger.info(
            f"No output_dir provided. Using temporary directory: {output_dir}"
        )
    else:
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Using provided output directory: {output_dir}")

    input_abs = os.path.abspath(input_dir)
    output_abs = os.path.abspath(output_dir)

    in_place = input_abs == output_abs

    if in_place:
        logger.info("Input and output directories are the same. "
                    "Using temporary files for in-place transformation.")

    transformations = []
    any_changes = False

    # Temporary directory used only for in-place transformations
    temp_dir = None

    if in_place:
        temp_dir = tempfile.mkdtemp(
            prefix="greencoderefactor_inplace_"
        )

    try:
        for root, _, files in os.walk(input_dir):
            for fname in files:

                if not fname.endswith(".py"):
                    continue

                full_path_input = os.path.join(root, fname)

                rel_path = os.path.relpath(
                    full_path_input,
                    input_dir
                )

                if in_place:
                    # Never write directly to the input file.
                    temp_output_path = os.path.join(
                        temp_dir,
                        rel_path
                    )

                    os.makedirs(
                        os.path.dirname(temp_output_path),
                        exist_ok=True
                    )

                    output_file = temp_output_path

                else:
                    output_file = os.path.join(
                        output_dir,
                        rel_path
                    )

                    os.makedirs(
                        os.path.dirname(output_file),
                        exist_ok=True
                    )

                logger.info(
                    f"Transforming file: {full_path_input}"
                )

                result = transform_code(
                    full_path_input,
                    output_file,
                    rules
                )

                if result and result.get("changed"):
                    any_changes = True

                    if in_place:
                        # Replace the original only after the
                        # transformation has completed successfully.
                        shutil.move(
                            output_file,
                            full_path_input
                        )

                        logger.info(
                            f"Changes detected. Replaced original file: "
                            f"{full_path_input}"
                        )
                    else:
                        logger.info(
                            f"Changes detected. Transformed file written to: "
                            f"{output_file}"
                        )

                else:
                    if not in_place:
                        if not os.path.exists(output_file):
                            shutil.copy2(
                                full_path_input,
                                output_file
                            )

                            logger.info(
                                f"No transformations applied. "
                                f"Copied original file: {full_path_input}"
                            )
                        else:
                            logger.info(
                                f"No transformations applied. "
                                f"Output file already exists: {output_file}"
                            )
                    else:
                        logger.info(
                            f"No transformations applied: "
                            f"{full_path_input}"
                        )

                transformations.append(result)

        if any_changes:
            message = "Refactor completed successfully"
            logger.info(message)
        else:
            message = "No code changes detected"
            logger.info(message)

        return {
            "transformations": transformations,
            "message": message,
            "output_dir": output_dir,
        }

    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )