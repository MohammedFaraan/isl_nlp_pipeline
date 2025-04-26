import spacy

# Load the English model
nlp = spacy.load("en_core_web_sm")

def preprocess(sentence):
    """
    Preprocess the input sentence using spaCy.
    Returns a spaCy Doc object with tokenization, POS tagging, and dependency parsing.
    """
    return nlp(sentence)