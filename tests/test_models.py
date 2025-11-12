"""Tests for data models."""

import pytest
from story_seq.models import BlastHit, BlastResult, SequenceNarrative


def test_blast_hit_creation() -> None:
    """Test creating a BlastHit."""
    hit = BlastHit(
        query_id="query1",
        subject_id="subject1",
        identity=95.5,
        alignment_length=100,
        evalue=1e-10,
        bit_score=200.0,
        query_start=1,
        query_end=100,
        subject_start=1,
        subject_end=100,
    )
    assert hit.query_id == "query1"
    assert hit.identity == 95.5


def test_blast_result_num_hits() -> None:
    """Test BlastResult num_hits property."""
    result = BlastResult(
        query_id="query1",
        query_length=150,
        database="test_db",
        hits=[],
    )
    assert result.num_hits == 0


def test_blast_result_top_hit() -> None:
    """Test BlastResult top_hit property."""
    hit1 = BlastHit(
        query_id="query1",
        subject_id="subject1",
        identity=95.0,
        alignment_length=100,
        evalue=1e-10,
        bit_score=150.0,
        query_start=1,
        query_end=100,
        subject_start=1,
        subject_end=100,
    )
    hit2 = BlastHit(
        query_id="query1",
        subject_id="subject2",
        identity=98.0,
        alignment_length=100,
        evalue=1e-15,
        bit_score=200.0,
        query_start=1,
        query_end=100,
        subject_start=1,
        subject_end=100,
    )
    
    result = BlastResult(
        query_id="query1",
        query_length=150,
        database="test_db",
        hits=[hit1, hit2],
    )
    
    assert result.top_hit == hit2
    assert result.top_hit.bit_score == 200.0


def test_sequence_narrative_creation() -> None:
    """Test creating a SequenceNarrative."""
    narrative = SequenceNarrative(
        sequence_id="seq1",
        narrative="This is a test narrative.",
        confidence=0.95,
        sources=["source1", "source2"],
    )
    assert narrative.sequence_id == "seq1"
    assert narrative.confidence == 0.95
    assert len(narrative.sources) == 2
