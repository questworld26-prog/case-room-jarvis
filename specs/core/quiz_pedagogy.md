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
