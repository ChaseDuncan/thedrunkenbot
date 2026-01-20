"""Text processing utilities for lyric completion."""
import re

def normalize_text(text: str) -> str:
    """
    Normalize text by converting to lowercase and removing punctuation. 
    
    :param text: Text to normalize
    :type text: str
    :return: Normalize text with only lowercase alphanumeric and spaces
    :rtype: str
    """
    return re.sub(r'[^\w\s]', '', text.lower())

def remove_overlap(input_text: str, completion: str) -> str:
    """

    
    """


def remove_overlap(input_text: str, completion: str) -> str:
    """
    Remove overlapping words between end of input and start of completion.

    Example:
        input_text: "My mind is the sky"
        completion: "My mind is the sky, everything else is the weather"
        returns: ", everything else is the weather 
   
    :param input_text: Input text from user
    :type input_text: str
    :param completion: LLM response to input text
    :type completion: str
    :return: Completion text with overlapping prefix removed
    :rtype: str
    """
    input_words = input_text.strip().split()
    completion_words = completion.strip().split()

    if input_words == completion_words:
        return ''

    overlap_length = 0

    # Find the longest overlap between end of input and start of completion
    for i in range(1, min(len(input_words), len(completion_words)) + 1):
        input_end = normalize_text(' '.join(input_words[-i:]))
        completion_start = normalize_text(' '.join(completion_words[:i]))

        if input_end == completion_start:
            overlap_length = i

    if overlap_length > 0:
        # Grab any trailing punctuation from last overlapping word
        last_word_in_overlap = completion_words[overlap_length - 1]
        trailing_punct = re.search(r'[^\w\s]+$', last_word_in_overlap)
        trailing_punct_str = trailing_punct.group() if trailing_punct else '' 

        # Prepend trailing punctuation is it exists
        if trailing_punct_str:
            return ' '.join([trailing_punct_str] + completion_words[overlap_length:])

        input_has_trailing_space = input_text != input_text.rstrip() 

        # If input does not have trailing whitespace add some
        remaining = ' '.join(completion_words[overlap_length:])
        return remaining if input_has_trailing_space else ' ' + remaining

    return completion

def clean_completion(input_text: str, raw_completion: str) -> str:
    """
    Clean up raw completion text by:
    1. Removing <think> tags
    2. Removing overlap with input
    
    :param input_text: User input text
    :type input_text: str
    :param raw_completion: Raw completion output from model
    :type completion: str
    :return: Model output with think tags and overlap removed
    :rtype: str
    """

    import re
    # Remove <think> tags
    completion = re.sub(r'</?think>', '', raw_completion, flags=re.IGNORECASE).strip()
    
    # Remove overlap
    return remove_overlap(input_text, completion)