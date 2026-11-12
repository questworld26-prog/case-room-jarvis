# Interactive Quiz Parsing & Scoring Specifications

## QUIZ-001: Multiple-Choice Parsing and Brand Casing Normalization

While grading interactive quiz responses, the quiz parser shall normalize standalone option choices and evaluate brand names case-insensitively.

Acceptance Criteria:
- AC-QUIZ-001.1: When parsing a student message for a multiple-choice selection, `parse_mcq_choice` shall extract standalone letters A through D without matching full sentences starting with those letters.
- AC-QUIZ-001.2: When a student submits an open-ended or multiple-choice response with lowercase or mixed-case brand names, the quiz engine shall evaluate the response case-insensitively.

## QUIZ-002: Two-Attempt Quiz Scoring and Scorecard Generation

While grading interactive quiz responses, the quiz engine shall enforce a two-attempt progression protocol and render a final scorecard after Question 5.

Acceptance Criteria:
- AC-QUIZ-002.1: When a student submits a correct answer on the first attempt, the quiz engine shall award 1.0 point and advance to the next question.
- AC-QUIZ-002.2: If a student submits an incorrect answer on the first attempt and a correct answer on the second attempt, then the quiz engine shall award 0.5 points and advance to the next question.
- AC-QUIZ-002.3: If a student submits incorrect answers on both the first and second attempts, then the quiz engine shall award 0.0 points, reveal the explanation, and advance to the next question.
- AC-QUIZ-002.4: When a student completes Question 5, `format_quiz_scorecard` shall render the final HTML scorecard displaying the total score out of 5.0 and per-question results.

## QUIZ-003: Case Study Markdown Quiz Bank Parsing, Validation, and Admin Inspection

While initializing or staging interactive quiz mode, the quiz system shall parse case-specific markdown quiz banks, validate question structure, and report diagnostics.

Acceptance Criteria:
- AC-QUIZ-003.1: When reading a multiple-choice question from a case markdown quiz bank, the quiz system shall extract the topic, prompt text under the question heading, four options A through D, single marked correct choice, hint, and official answer.
- AC-QUIZ-003.2: When reading an open-ended question from a case markdown quiz bank, the quiz system shall extract the topic, prompt text under the question heading, rubric key points list under the answer rubric heading, hint, and official answer.
- AC-QUIZ-003.3: When a case markdown quiz bank contains schema violations, the quiz system shall report explicit diagnostic errors identifying the offending line numbers.
- AC-QUIZ-003.4: If a case study lacks a valid markdown quiz bank or contains syntax violations, then the quiz system shall log an error and display a diagnostic alert in the instructor admin panel.
- AC-QUIZ-003.5: In the instructor admin panel, the system shall render the validation status of the active case quiz bank and display an interactive preview of the rendered question cards.
