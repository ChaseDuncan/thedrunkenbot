"""Tests for text processing utilities."""

import pytest
from app.core.text_utils import(
    normalize_text,
    remove_overlap,
    clean_completion
)

class TestNormalizeText:
    """ Tests for normalize_text function. """

    def test_removes_punctuation(self):
        assert normalize_text("test,") == "test"
        assert normalize_text("test!") == "test"
        assert normalize_text("te'st?") == "test"

    def test_converts_to_lowercase(self):
        assert normalize_text("tEsT") == "test"
        assert normalize_text("TEST") == "test"

    def test_preserves_spaces(self):
        assert normalize_text("t E s T") == "t e s t"

    def test_combined(self):
        assert normalize_text("This is a test, combined!") == "this is a test combined"

class TestRemoveOverlap:
    """ Tests for remove_overlap function. """
    def test_preserves_trailing_punctuation_from_overlap(self):
        """ Test that trailing punctuation from overlapping word is preserved. """
        input_text = "My mind is the sky"
        completion = "My mind is the sky, everything else is the weather"
        result = remove_overlap(input_text, completion)
        assert result == ", everything else is the weather"

    def test_extra_space_when_input_string_has_none(self):
        """ Test that no extra space is added when there's no trailing punctuation. """
        input_text = "My mind is the sky"
        completion = "My mind is the sky everything else is the weather"
        result = remove_overlap(input_text, completion)
        assert result == " everything else is the weather"

    def test_no_extra_space_added_to_input_with_space(self):
        """ Test that no extra space is added when there's no trailing punctuation. """
        input_text = "My mind is the sky "
        completion = "My mind is the sky everything else is the weather"
        result = remove_overlap(input_text, completion)
        assert result == "everything else is the weather"

    def test_non_exact_overlap(self):
        """ Test that overlap removal works when input doesn't exactly match the start of the completion. """
        input_text = " When I need to clear my head I think to myself, 'My mind is the sky"
        completion = "my mind is the sky and everything else is the weather."
        result = remove_overlap(input_text, completion)
        assert result == " and everything else is the weather."

class TestCleanCompletion:
    """Integration tests for clean_completion function."""
    
    def test_removes_empty_think_tags(self):
        """Test that empty <think></think> tags are removed."""
        input_text = "hello"
        raw = "<think></think>hello world"
        result = clean_completion(input_text, raw)
        assert result == " world"  # Leading space from overlap removal
        assert "<think>" not in result
    
    def test_removes_think_tags_case_insensitive(self):
        """Test that <THINK> tags are removed regardless of case."""
        input_text = "hello"
        raw = "<THINK></THINK>hello world"
        result = clean_completion(input_text, raw)
        assert result == " world"  # Leading space from overlap removal
        assert "<THINK>" not in result
    
    def test_removes_overlap_with_leading_space(self):
        """Test that overlapping text is removed and spacing preserved."""
        input_text = "My mind is the sky"
        raw = "My mind is the sky, and I fly so high"
        result = clean_completion(input_text, raw)
        assert result == ", and I fly so high"
    
    def test_preserves_quotes_in_lyrics(self):
        """Test that quotes in lyrics are preserved."""
        input_text = "She said"
        raw = 'She said "Don\'t look back"'
        result = clean_completion(input_text, raw)
        assert '"' in result
        assert result == ' "Don\'t look back"'
    
    def test_full_pipeline_with_think_and_overlap(self):
        """Test complete cleaning pipeline with both think tags and overlap."""
        input_text = "My mind is the sky"
        raw = "<think></think>My mind is the sky, and I fly so high"
        result = clean_completion(input_text, raw)
        
        # Should have no think tags
        assert "<think>" not in result
        assert "</think>" not in result
        # Should be cleaned
        assert result == ", and I fly so high"
    
    def test_handles_empty_after_cleaning(self):
        """Test when cleaning results in empty string."""
        input_text = "hello world"
        raw = "hello world"
        result = clean_completion(input_text, raw)
        assert result == ""
    
    def test_handles_empty_after_overlap_removal(self):
        """Test when only overlap exists."""
        input_text = "the sky is blue"
        raw = "the sky is blue"
        result = clean_completion(input_text, raw)
        assert result == ""
    
    def test_preserves_punctuation_in_lyrics(self):
        """Test that punctuation like commas, quotes, apostrophes are preserved."""
        input_text = "He whispered"
        raw = 'He whispered "I love you," she smiled'
        result = clean_completion(input_text, raw)
        assert '"' in result
        assert ',' in result
        assert result == ' "I love you," she smiled'
    
    def test_only_overlap_no_think_tags(self):
        """Test removing overlap when there are no think tags."""
        input_text = "the sky is blue"
        raw = "the sky is blue and bright"
        result = clean_completion(input_text, raw)
        assert result == " and bright"
    
    def test_no_overlap_preserves_content(self):
        """Test that content is preserved when there's no overlap."""
        input_text = "hello"
        raw = "goodbye world"
        result = clean_completion(input_text, raw)
        assert result == "goodbye world"
    
    def test_multiple_empty_think_tags(self):
        """Test removing multiple empty think tag pairs."""
        input_text = "hello"
        raw = "<think></think><think></think>hello world"
        result = clean_completion(input_text, raw)
        assert result == " world"  # Leading space from overlap removal
        assert "<think>" not in result