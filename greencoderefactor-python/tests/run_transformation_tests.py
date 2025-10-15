import os
from trasnsformers.transform import transform_code

def get_test_rules_for_path(file_path: str):
    path_lower = file_path.lower().replace("\\", "/")
    if "techniques/t10" in path_lower:
        return ["ExplicitRaiseToExceptBodyTransformer", "UnusedLocalVariablesTransformer", "UnusedAssignmentTransformer"]
    elif "sonar/r1481" in path_lower:
        return ["ExplicitRaiseToExceptBodyTransformer", "UnusedLocalVariablesTransformer", "UnusedAssignmentTransformer"]
    elif "sonar/r1854" in path_lower:
        return ["ExplicitRaiseToExceptBodyTransformer", "UnusedLocalVariablesTransformer", "UnusedAssignmentTransformer"]
    else:
        return []

def run_and_transform(file_path, input_dir, output_dir):
    rel_path = os.path.relpath(file_path, input_dir)
    transformed_path = os.path.join(output_dir, rel_path)
    os.makedirs(os.path.dirname(transformed_path), exist_ok=True)

    rules = get_test_rules_for_path(file_path)
    if not rules:
        print(f"No test rules matched for {file_path}, skipping.")
        return

    try:
        transform_code(file_path, transformed_path, rules=rules)
    except Exception as e:
        print(f"Failed to transform {file_path}: {e}")
        return

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "IN")
    output_dir = os.path.join(script_dir, "OUT")
    os.makedirs(output_dir, exist_ok=True)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                run_and_transform(full_path, input_dir, output_dir)

if __name__ == "__main__":
    main()
