# modules/extractor.py

from utils.helpers import load_list

time_words = load_list('data/time_words.txt')

def extract_components(doc):
    subject, verb, original_verb, object_, prep_object, time_exp = None, None, None, None, None, None
    negation, modal, complement, possessive = False, None, None, None

    # Fallback: if the very first token is a time word, capture it.
    if doc and doc[0].text.lower().strip(",") in time_words:
        time_exp = doc[0]

    for token in doc:
        # Extract subject: if token is a determiner ("the", "a", "an"), choose its following token.
        if token.dep_ in ("nsubj", "nsubjpass"):
            if subject is None:
                if token.text.lower() in ["the", "a", "an"]:
                    if token.i + 1 < len(doc):
                        subject = doc[token.i + 1]
                else:
                    subject = token
        elif token.dep_ == "ROOT":
            original_verb = token
            verb = token
        elif token.dep_ == "dobj":
            if object_ is None:
                object_ = token
        elif token.dep_ in ("advmod", "npadvmod", "tmod"):
            token_clean = token.text.lower().strip(",")
            if token_clean in time_words:
                time_exp = token
        elif token.dep_ == "neg":
            negation = True
        elif token.pos_ == "AUX" and token.lemma_ not in ["be", "have"]:
            modal = token
        elif token.dep_ == "poss":
            # Build full possessive phrase, e.g., "my parents"
            possessive = f"{token.text} {token.head.text}"
    
    # Fallback: if subject still missing, check for pronoun "I"
    if subject is None:
        for token in doc:
            if token.pos_ == "PRON" and token.text.lower() == "i":
                subject = token
                break

    # Handle copula "be" constructions.
    if original_verb and original_verb.lemma_ == "be":
        complement = next((child for child in original_verb.children if child.dep_ in ("acomp", "attr")), None)
        if not complement:
            prep = next((child for child in original_verb.children if child.dep_ == "prep"), None)
            if prep:
                pobj = next((child for child in prep.children if child.dep_ == "pobj"), None)
                if pobj:
                    verb = pobj
        elif complement and complement.pos_ in ("ADJ", "NOUN", "PROPN"):
            verb = complement
            if subject and subject.text.lower() == "it":
                subject = None

    # Handle "feel" constructions.
    if original_verb and original_verb.lemma_ == "feel":
        complement = next((child for child in original_verb.children 
                           if child.dep_ == "acomp" or child.pos_ in ("ADV", "ADJ")), None)
        if complement:
            verb = complement

    # Handle "want" or "need" constructions.
    if original_verb and original_verb.lemma_ in ["want", "need"]:
        infinitive = next((child for child in original_verb.children if child.dep_ == "xcomp"), None)
        if infinitive:
            if infinitive.lemma_ == "take":
                inf_obj = next((child for child in infinitive.children if child.dep_ == "dobj"), None)
                if inf_obj and inf_obj.text.lower() in ["rest", "bath"]:
                    verb = (original_verb, inf_obj)
                else:
                    verb = (original_verb, infinitive)
            else:
                verb = (original_verb, infinitive)
            prep = next((child for child in infinitive.children if child.dep_ == "prep"), None)
            if prep:
                pobj = next((child for child in prep.children if child.dep_ == "pobj"), None)
                if pobj:
                    prep_object = pobj

    # Only assign a prepositional object if a direct object hasn't been set.
    if not prep_object and not object_:
        for token in doc:
            if token.dep_ == "prep":
                pobj = next((child for child in token.children if child.dep_ == "pobj"), None)
                if pobj:
                    prep_object = pobj
                    break

    # Fallback for time: if still not set, scan the tokens.
    if not time_exp:
        for token in doc:
            if token.text.lower().strip(",") in time_words:
                time_exp = token
                break

    # Special handling for "switch on"
    if original_verb and original_verb.lemma_ == "switch":
        # First, try to explicitly find the token "fan".
        for token in doc:
            if token.text.lower() == "fan":
                prep_object = token
                break
        # Otherwise, if "on" exists, use its head.
        if not prep_object:
            for token in doc:
                if token.text.lower() == "on":
                    prep_object = token.head
                    break
        if prep_object:
            verb = prep_object  # Force the main verb to be the destination (e.g., FAN)

    return subject, verb, original_verb, object_, prep_object, time_exp, negation, modal, complement, possessive
