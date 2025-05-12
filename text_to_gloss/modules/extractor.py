# modules/extractor.py

import spacy
import os
from isl_nlp_pipeline.text_to_gloss.utils.helpers import load_list

# Get the base directory where the module is located
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(os.path.dirname(base_dir), "data")

# Load time words from file
time_words = load_list(os.path.join(data_dir, 'time_words.txt'))

def extract_components(doc):
    """
    Extract grammatical components from a sentence using spaCy's dependency parsing.
    
    This function identifies key sentence components including:
    - Subject, verb, and object
    - Time expressions
    - Negation markers
    - Modal verbs
    - Prepositional objects
    - Possessive markers
    
    Args:
        doc: A spaCy Doc object with parsed sentence
        
    Returns:
        tuple: Components extracted from the sentence
    """
    subject, verb, original_verb, object_, prep_object, time_exp = None, None, None, None, None, None
    negation, modal, complement, possessive = False, None, None, None

    # First pass: extract time expressions from sentence start
    if doc and len(doc) > 0:
        if doc[0].text.lower().strip(",") in time_words:
            time_exp = doc[0]
        # Also check the second token if first is followed by a comma
        elif len(doc) > 2 and doc[0].text.lower().strip(",") in time_words and doc[1].text == ",":
            time_exp = doc[0]

    # Collect all named entities (might be useful for special handling)
    entities = {ent.text: ent.label_ for ent in doc.ents}

    # Second pass: extract main grammatical components
    for token in doc:
        # Subject extraction - handle determiner + noun combinations
        if token.dep_ in ("nsubj", "nsubjpass"):
            if subject is None:
                # Handle the case where subject has a determiner
                if token.text.lower() in ["the", "a", "an"]:
                    if token.i + 1 < len(doc):
                        subject = doc[token.i + 1]
                else:
                    subject = token
        # Verb extraction - handle main verbs and special verbs
        elif token.dep_ == "ROOT":
            original_verb = token
            verb = token
        # Object extraction - handle direct objects
        elif token.dep_ == "dobj":
            if object_ is None:
                # Handle determiners similarly to subjects
                if token.text.lower() in ["the", "a", "an"] and token.i + 1 < len(doc):
                    object_ = doc[token.i + 1]
                else:
                    object_ = token
        # Time expressions - handle various positions
        elif token.dep_ in ("advmod", "npadvmod", "tmod"):
            token_clean = token.text.lower().strip(",")
            if token_clean in time_words:
                time_exp = token
        # Negation markers
        elif token.dep_ == "neg":
            negation = True
        # Modal verbs - extract but exclude "be" and "have"
        elif token.pos_ == "AUX" and token.lemma_ not in ["be", "have"]:
            modal = token
        # Possessive extraction with improved handling
        elif token.dep_ == "poss":
            # Check if head is a proper noun or part of entity
            if token.head.pos_ in ["NOUN", "PROPN"]:
                if token.head.text in entities:
                    # For named entities, include the full entity
                    possessive = f"{token.text} {token.head.text}"
                else:
                    # For regular nouns, just use the possessive + noun
                    possessive = f"{token.text} {token.head.text}"

    # Special handling for first person pronoun
    if subject is None:
        for token in doc:
            if token.pos_ == "PRON" and token.text.lower() == "i":
                subject = token
                break

    # Handle copular "be" constructions with better complement detection
    if original_verb and original_verb.lemma_ == "be":
        # Look for adjective or noun complements
        for child in original_verb.children:
            if child.dep_ in ("acomp", "attr") and complement is None:
                complement = child
                if complement.pos_ in ("ADJ", "NOUN", "PROPN"):
                    verb = complement
        
        # If no complement found, check for prepositional phrases
        if not complement:
            for child in original_verb.children:
                if child.dep_ == "prep":
                    # Find the object of preposition
                    for grandchild in child.children:
                        if grandchild.dep_ == "pobj":
                            prep_object = grandchild
                            if not verb or verb == original_verb:
                                verb = prep_object

        # Special handling for "it is" expressions
        if subject and subject.text.lower() == "it":
            # For expressions like "it is an emergency", subject can be omitted in ISL
            if complement and complement.pos_ == "NOUN":
                subject = None

    # Improved handling for "feel" constructions
    if original_verb and original_verb.lemma_ == "feel":
        for child in original_verb.children:
            if child.dep_ in ["acomp", "advmod", "xcomp"] or child.pos_ in ["ADV", "ADJ"]:
                complement = child
                # Allow for richer expressions of feeling
                if child.text.lower() in ["well", "hot", "cold", "thirsty"]:
                    verb = child

    # Improved handling for "want" or "need" constructions with infinitives
    if original_verb and original_verb.lemma_ in ["want", "need"]:
        # Look for infinitive clauses (with or without "to")
        infinitive = None
        for child in original_verb.children:
            if child.dep_ == "xcomp" or (child.dep_ == "dobj" and child.pos_ == "VERB"):
                infinitive = child
                break
                
        if infinitive:
            # Handle multi-word expressions like "take rest" or "take bath"
            if infinitive.lemma_ == "take":
                for inf_child in infinitive.children:
                    if inf_child.dep_ == "dobj" and inf_child.text.lower() in ["rest", "bath"]:
                        verb = (original_verb, inf_child)
                        break
                else:
                    # Default case for other infinitives
                    verb = (original_verb, infinitive)
            else:
                verb = (original_verb, infinitive)
                
            # Extract destinations or prep objects from the infinitive
            for inf_child in infinitive.children:
                if inf_child.dep_ == "prep":
                    for pobj_child in inf_child.children:
                        if pobj_child.dep_ == "pobj":
                            prep_object = pobj_child
                            break

    # Assign prepositional objects if no direct object is found
    if not prep_object and not object_:
        for token in doc:
            if token.dep_ == "prep":
                for child in token.children:
                    if child.dep_ == "pobj":
                        prep_object = child
                        break
                if prep_object:
                    break

    # Final special handling for "switch on" and similar phrases
    for token in doc:
        if token.lemma_ == "switch" and token.dep_ == "ROOT":
            # Look for particles that indicate direction (on/off)
            particle = None
            for child in token.children:
                if child.dep_ == "prt" and child.text.lower() in ["on", "off"]:
                    particle = child
                    break
                    
            # Also look for objects like "fan"
            for token in doc:
                if token.text.lower() == "fan" or token.text.lower() == "light":
                    prep_object = token
                    break
                    
            if prep_object and particle:
                verb = prep_object  # E.g., "FAN ON" instead of "SWITCH FAN ON"

    return subject, verb, original_verb, object_, prep_object, time_exp, negation, modal, complement, possessive
