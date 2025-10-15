# Available Transformers

This project currently provides the following code transformers:

## 1. ExplicitRaiseToExceptBodyTransformer
- Replace explicitly raised exceptions inside a `try` block with the corresponding `except` body if no alias is used.  

## 2. UnusedLocalVariablesTransformer
- Detects and removes unused local variables.  
- Reference: [RSPEC-1481](https://rules.sonarsource.com/java/RSPEC-1481)

## 3. UnusedAssignmentTransformer
- Removes assignments that are never used in the code.  
- Reference: [RSPEC-1854](https://rules.sonarsource.com/java/RSPEC-1854)
