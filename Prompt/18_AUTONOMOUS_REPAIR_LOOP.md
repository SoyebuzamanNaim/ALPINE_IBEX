# Autonomous Repair Loop

On failure:

1. Reproduce.
2. Classify:
   - data
   - schema
   - dependency
   - code
   - model
   - retrieval
   - agent
   - API
   - frontend
   - science
3. Identify root cause.
4. Apply smallest justified fix.
5. Rerun failing test.
6. Run neighboring tests.
7. Rerun phase validation.
8. Maximum three repair cycles.
9. If still failing:
   - mark BLOCKED
   - write exact blocker
   - stop progression

Never weaken a test merely to force PASS.
