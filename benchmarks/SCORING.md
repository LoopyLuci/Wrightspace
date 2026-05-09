# Benchmark Scoring

This page defines the first-pass scoring rubric for the Agentic Builder benchmark suite.

## Scoring Dimensions

- `task completion`: did the run satisfy the benchmark's expected outcome?
- `edit discipline`: did the run avoid unrelated file or IR churn?
- `recovery quality`: if the run failed, did it return a clear step log and rollback cleanly?
- `validation status`: did the resulting project remain IR-valid, and when required, pass emitted project checks?

## Pass Levels

- `full pass`: benchmark outcome satisfied, validation checks passed, and no unrelated changes were introduced.
- `partial pass`: core reasoning was correct but the run stopped short of full remediation or final validation.
- `fail`: the run missed the benchmark intent, introduced invalid state, or could not explain the failure clearly.

## Audit Benchmark Rule

For the first agent-loop increment, the `security-accessibility-audit` benchmark allows `detect-and-report` as a partial pass.

To earn a partial pass, the agent must:

- flag issues with severity ratings
- include suggested fixes
- avoid destructive or unrelated changes

Automatic remediation becomes a full-pass requirement in the next iteration.