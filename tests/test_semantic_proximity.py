"""
Level 2 Test Suite: Semantic Proximity
Uses sentence-transformers (all-MiniLM-L6-v2) to calculate cosine similarity between
student inputs and Jarvis chatbot responses to ensure answers are topically relevant.
"""

import asyncio

import pytest
from cache_manager import get_or_create_cache
from sentence_transformers import SentenceTransformer, util

from chatbot import chat
from config import app_state, get_default_case_study


@pytest.fixture(scope="module")
def setup_context_cache():
    """Ensure clean case text context is loaded before running tests."""
    app_state.cache_ttl = "12600s"
    cache = get_or_create_cache(get_default_case_study(), force_refresh=True)
    assert len(app_state.case_text_context) > 0 or app_state.active_cache_name is not None
    yield cache


@pytest.fixture(scope="module")
def embedder():
    """Load lightweight SentenceTransformer model once for the test module."""
    return SentenceTransformer("all-MiniLM-L6-v2")


def collect_stream(question, history, student_name="Test Student"):
    """Helper to collect final yielded output from async generator chat function."""

    async def _runner():
        final_text = ""
        async for chunk in chat(question, history, student_name=student_name):
            final_text = chunk
        return final_text

    return asyncio.run(_runner())


def compute_similarity(embedder_model, text1: str, text2: str) -> float:
    """Compute cosine similarity between two text strings using sentence embeddings."""
    emb1 = embedder_model.encode(text1, convert_to_tensor=True)
    emb2 = embedder_model.encode(text2, convert_to_tensor=True)
    similarity = util.cos_sim(emb1, emb2).item()
    return similarity


# [verifies: MODE-001/AC-MODE-001.1]
def test_scope3_semantic_proximity(setup_context_cache, embedder):
    """Verify response to Scope 3 question is semantically close (> 0.30) AND factually anchored (85%)."""
    app_state.active_mode = "qa"
    question = "What percentage of EcoBrew's total carbon footprint is represented by Scope 3 emissions?"
    response = collect_stream(question, [])

    sim = compute_similarity(embedder, question, response)
    print(f"\n[Semantic Proximity Score - Scope 3]: {sim:.3f}")
    assert sim >= 0.30, f"Scope 3 response had low semantic similarity to question: {sim:.3f}"
    # Factual grounding anchor: prevents high similarity hallucinations
    assert any(
        num in response.lower() for num in ["85%", "85.2%", "85 percent", "85.2 percent", "eighty-five percent"]
    ), (
        f"Scope 3 response had topical similarity ({sim:.3f}) but lacked the critical factual figure (85%): {response[:150]}"
    )


# [verifies: MODE-001/AC-MODE-001.1]
def test_circulargrain_semantic_proximity(setup_context_cache, embedder):
    """Verify response to CircularGrain question is semantically close (> 0.30) AND concept anchored (upcycle / spent grain)."""
    app_state.active_mode = "qa"
    question = "What is CircularGrain and how does it contribute to circular economy?"
    response = collect_stream(question, [])

    sim = compute_similarity(embedder, question, response)
    print(f"\n[Semantic Proximity Score - CircularGrain]: {sim:.3f}")
    assert sim >= 0.30, f"CircularGrain response had low semantic similarity: {sim:.3f}"
    # Conceptual grounding anchor
    assert any(
        term in response.lower() for term in ["upcycle", "spent grain", "brew", "protein", "byproduct", "waste"]
    ), f"CircularGrain response lacked circular economy concept grounding: {response[:150]}"


# [verifies: MODE-001/AC-MODE-001.1]
def test_water_stewardship_semantic_proximity(setup_context_cache, embedder):
    """Verify response to water stewardship is semantically close (> 0.30) AND metric anchored."""
    app_state.active_mode = "qa"
    question = "How does EcoBrew handle water stewardship in high-stress watershed areas?"
    response = collect_stream(question, [])

    sim = compute_similarity(embedder, question, response)
    print(f"\n[Semantic Proximity Score - Water Stewardship]: {sim:.3f}")
    assert sim >= 0.30, f"Water stewardship response had low semantic similarity: {sim:.3f}"
    # Context grounding anchor
    assert any(
        term in response.lower() for term in ["watershed", "stress", "efficiency", "hl/hl", "2.38", "2.5", "basin"]
    ), f"Water stewardship response lacked domain terms: {response[:150]}"


# [verifies: CHAT-004/AC-CHAT-004.1]
def test_off_topic_semantic_dissimilarity(setup_context_cache, embedder):
    """Verify off-topic response declines question, keeping similarity low or distinct from trivia answer."""
    app_state.active_mode = "qa"
    question = "Who won the FIFA World Cup in 2022?"
    response = collect_stream(question, [])

    # Off-topic response should contain standard refusal phrases
    assert any(phrase in response.lower() for phrase in ["outside", "not covered", "do not know", "documents", "scope"])

    # Calculate similarity to FIFA answer concept - should be low (< 0.35) compared to direct factual answers
    fifa_target = "Argentina won the 2022 FIFA World Cup in Qatar defeating France in penalties."
    sim_to_fifa = compute_similarity(embedder, response, fifa_target)
    print(f"\n[Semantic Proximity Score - Refusal vs FIFA Answer]: {sim_to_fifa:.3f}")
    assert sim_to_fifa < 0.35, (
        f"Chatbot refusal string should maintain low similarity to actual trivia answer: {sim_to_fifa:.3f}"
    )
