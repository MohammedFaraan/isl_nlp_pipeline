import spacy
import os
from isl_nlp_pipeline.text_to_gloss.utils.helpers import load_list

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Get the base directory where the module is located
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(os.path.dirname(base_dir), "data")

# Load wh-words from file
wh_words = load_list(os.path.join(data_dir, 'wh_words.txt'))

def classify_sentence(doc):
    """
    Classify sentence type using spaCy's linguistic features.
    Returns: 'wh-question', 'yes-no-question', 'imperative', or 'declarative'
    """
    # Check if it's a question using spaCy's features
    if doc[-1].text == "?":
        # Check for WH-questions using spaCy's built-in WH-word detection
        for token in doc:
            # Use spaCy's tag_ for precise part-of-speech detection
            if token.tag_ in ['WDT', 'WP', 'WP$', 'WRB'] or token.text.lower() in wh_words:
                return "wh-question"
        return "yes-no-question"
    
    # Check for imperatives using multiple spaCy features
    root = [token for token in doc if token.dep_ == "ROOT"][0]
    
    # Imperative checks using spaCy's linguistic features:
    # 1. Root is a verb in base form (VB)
    # 2. No subject dependency at the start
    # 3. Verb is at the start or preceded by "please"
    if (root.pos_ == "VERB" and root.tag_ == "VB" and 
        (doc[0].dep_ != "nsubj" or doc[0].text.lower() == "please")):
        # Additional check for common imperative patterns
        if (doc[0].pos_ == "VERB" or 
            (len(doc) > 1 and doc[0].text.lower() == "please" and doc[1].pos_ == "VERB")):
            return "imperative"
    
    # Default to declarative if no other type matches
    return "declarative"