import argparse
import sys
from refactor import run_refactor
from config.logger import setup_logger

logger, _ = setup_logger()

def main():
    parser = argparse.ArgumentParser(description="Run Python refactor action")
    parser.add_argument("--repo", required=True, help="Repository (local path or CI URL/slug)")
    parser.add_argument("--ref", help="Branch to use")
    parser.add_argument("--output", required=True, help="Directory to store refactor output")
    parser.add_argument("--rules", default=None, help="Comma-separated list of refactor rules")
    parser.add_argument("--ci", help="CI provider name (GitHub, GitLab, AzureDevOps, etc.)")
    parser.add_argument("--run_id", help="Pipeline run ID")
    parser.add_argument("--workflow_name", help="Workflow name or pipeline name")
    parser.add_argument("--workflow_id", help="Workflow ID")
    parser.add_argument("--commit_hash", help="Commit SHA")

    args = parser.parse_args()

    rules = [r.strip() for r in args.rules.split(",")] if args.rules else None

    try:
        result = run_refactor(
            repo=args.repo,
            ref=args.ref,
            rules=rules,
            output_dir=args.output,
            ci=args.ci,
            run_id=args.run_id,
            workflow_name=args.workflow_name,
            workflow_id=args.workflow_id,
            commit_hash=args.commit_hash,
        )

        logger.info(f"Refactor completed successfully. Output directory: {result['output_dir']}")
        if 'branch_url' in result and result['branch_url']:
            logger.info(f"Branch URL: {result['branch_url']}")

    except Exception as e:
        logger.error(f"Refactor failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
