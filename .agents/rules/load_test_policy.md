# Load Testing Policy

## Rule
* **Do NOT execute the 50-student concurrency load test (`tests/test_load.py`) automatically during routine builds, verification steps, or code updates.**
* **Only run unit/functional tests (`tests/test_chatbot.py`) for regular validation.**
* **The load test (`tests/test_load.py`) must ONLY be run when the user explicitly requests it.**
