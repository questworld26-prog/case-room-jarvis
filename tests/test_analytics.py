"""
Automated Pytest suite for Classroom Engagement Analytics system.
Verifies Gini index calculation, telemetry parsing, session metric computation, and AI prompt classification.
"""

from analytics import (
    classify_prompts_ai,
    compute_gini_coefficient,
    compute_metrics,
    generate_analytics_charts,
    generate_pdf_report,
    get_available_log_files,
    load_telemetry_logs,
)


# [verifies: ANLY-001/AC-ANLY-001.1]
def test_gini_coefficient():
    # Equal participation: Gini = 0.0
    equal_counts = [5, 5, 5, 5]
    assert compute_gini_coefficient(equal_counts) == 0.0

    # Highly unequal participation
    unequal_counts = [1, 1, 1, 100]
    gini = compute_gini_coefficient(unequal_counts)
    assert gini > 0.6

    # Single student
    assert compute_gini_coefficient([10]) == 0.0


# [verifies: ANLY-001/AC-ANLY-001.2]
def test_load_telemetry_logs(tmp_path):
    log_files = get_available_log_files()
    if not log_files:
        sample_log = tmp_path / "classroom_chats_sample.jsonl"
        sample_log.write_text(
            '{"timestamp": "2026-11-11 10:00:00", "session_id": "S1", "student_name": "Alex", "turn_number": 1, "prompt": "Hi", "response": "Hello"}\n'
            '{"malformed line\n'
            '{"timestamp": "2026-11-11 10:01:00", "session_id": "S1", "student_name": "Alex", "turn_number": 2, "prompt": "Scope 3", "response": "85%"}\n',
            encoding="utf-8",
        )
        records = load_telemetry_logs([str(sample_log)])
        assert len(records) == 2
        assert records[0]["student_name"] == "Alex"
        assert records[0]["turn_number"] == 1
    else:
        assert isinstance(log_files, list)
        assert len(log_files) > 0
        records = load_telemetry_logs(log_files[:2])
        assert isinstance(records, list)
        if records:
            rec = records[0]
            assert "session_id" in rec
            assert "student_name" in rec
            assert "turn_number" in rec


# [verifies: ANLY-001/AC-ANLY-001.3]
def test_compute_metrics():
    log_files = get_available_log_files()
    metrics = compute_metrics(log_files[:2])
    assert "total_questions" in metrics
    assert "active_students_count" in metrics
    assert "gini_coefficient" in metrics
    assert "participation_equality_score" in metrics
    assert "max_student_name" in metrics
    assert "max_student_questions" in metrics
    assert "question_histogram" in metrics
    assert isinstance(metrics["question_histogram"], dict)
    assert 0.0 <= metrics["participation_equality_score"] <= 100.0

    # Test question and answer length stats
    assert "question_length_stats" in metrics
    assert "avg_words" in metrics["question_length_stats"]
    assert "median_words" in metrics["question_length_stats"]
    assert "answer_length_stats" in metrics
    assert "avg_words" in metrics["answer_length_stats"]
    assert "median_words" in metrics["answer_length_stats"]

    # Test mode stats & relevance
    assert "mode_stats" in metrics
    assert "overall_mode_relevance_score" in metrics
    assert 0.0 <= metrics["overall_mode_relevance_score"] <= 100.0


# [verifies: ANLY-001/AC-ANLY-001.4]
def test_ai_classification_charts_and_pdf():
    log_files = get_available_log_files()
    metrics = compute_metrics(log_files)
    records = metrics.get("records", [])[:5]  # Small sample batch for quick unit test

    bloom_counts, topic_counts, gap_topics = classify_prompts_ai(records)
    assert isinstance(bloom_counts, dict)
    assert isinstance(topic_counts, dict)
    assert isinstance(gap_topics, list)

    # Test chart generation with 8 subplots
    buf = generate_analytics_charts(metrics, bloom_counts, topic_counts)
    assert buf is not None
    assert buf.getvalue() is not None

    # Test PDF Report Generation
    pdf_path = generate_pdf_report(
        selected_logfiles=log_files[:2],
        metrics=metrics,
        bloom_counts=bloom_counts,
        topic_counts=topic_counts,
        gap_topics=gap_topics,
        debrief_text="Test debrief executive summary.",
    )
    assert pdf_path is not None
    assert pdf_path.endswith(".pdf")


# [verifies: PRIV-002/AC-PRIV-002.3]
def test_test_log_file_isolation():
    """Verify that test/build runs log to test_ files and are excluded from standard analytics by default."""
    from logger import get_log_file_path, is_test_environment, log_interaction

    # Verify is_test_environment detects pytest
    assert is_test_environment() is True

    log_path = get_log_file_path()
    assert "test_classroom_chats_" in log_path.name

    # Test logger behavior
    log_interaction(
        mode="qa",
        framework=None,
        prompt="Unit test query",
        response="Unit test response",
        latency_seconds=0.1,
        student_name="Test Student",
        session_id="Test_Session_Isolation",
    )

    # Verify default get_available_log_files excludes test_ files
    clean_files = get_available_log_files(include_test_logs=False)
    assert not any(f.startswith("test_") for f in clean_files)

    # Verify including test logs lists test_ files
    all_files = get_available_log_files(include_test_logs=True)
    assert any(f.startswith("test_") for f in all_files)
