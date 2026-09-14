import argparse
import sys
from refactor import run_refactor
from config.logger import setup_logger

logger, _ = setup_logger()


def main():
    parser = argparse.ArgumentParser(description="Run Python refactor action")
    parser.add_argument("--input", required=True, help="Directory containing the source code")
    parser.add_argument("--output", required=True, help="Directory to store refactored code")
    parser.add_argument("--rules", default=None, help="Comma-separated list of refactor rules")

    args = parser.parse_args()

    rules = [r.strip() for r in args.rules.split(",")] if args.rules else None

    try:
        result = run_refactor(
            input_dir=args.input,
            rules=rules,
            output_dir=args.output,
        )

        logger.info(
            f"Refactor completed successfully. Output directory: {result['output_dir']}"
        )

    except Exception as e:
        logger.error(f"Refactor failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()