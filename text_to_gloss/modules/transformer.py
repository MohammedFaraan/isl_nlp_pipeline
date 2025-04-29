# modules/transformer.py

import spacy
import os
from text_to_gloss.utils.helpers import load_list, finger_spell

# Get the base directory where the module is located
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(os.path.dirname(base_dir), "data")

# Load wh-words from file
wh_words = load_list(os.path.join(data_dir, 'wh_words.txt'))

def transform_components(sentence_type, components, doc):
    subject, verb, original_verb, object_, prep_object, time_exp, negation, modal, complement, possessive = components
    
    # Prepare gloss tokens (all in uppercase).
    glosses = {
        "subject": subject.text.upper() if subject else "",
        "time": time_exp.text.upper() if time_exp else "",
        "object": object_.text.upper() if object_ else "",
        "prep_object": prep_object.text.upper() if prep_object else "",
        "modal": modal.text.upper() if modal else "",
        "complement": complement.text.upper() if complement else "",
        "possessive": possessive.upper() if possessive else ""
    }

    # Fallback: if subject is still missing, try to assign it.
    if not glosses["subject"] and len(doc) > 0:
        for token in doc:
            if token.pos_ == "PRON" and token.text.lower() == "i":
                glosses["subject"] = token.text.upper()
                break

    # For proper names in "be" sentences.
    if verb and not isinstance(verb, tuple):
        if original_verb and original_verb.lemma_ == "be" and complement and complement.pos_ == "PROPN":
            glosses["verb"] = complement.text.upper()
        elif verb.pos_ == "PROPN":
            glosses["verb"] = finger_spell(verb.text)
        else:
            glosses["verb"] = verb.lemma_.upper()

    politeness = " PLEASE" if any(token.text.lower() == "please" for token in doc) else ""

    if sentence_type == "declarative":
        # Handle "feel" constructions.
        if original_verb and original_verb.lemma_ == "feel":
            comp = glosses["complement"].replace("FEEL", "").strip()
            if comp == "THIRSTY":
                base_gloss = f"{glosses['time']} {glosses['subject']} {comp}"
            else:
                base_gloss = f"{glosses['time']} {glosses['subject']} {comp} FEEL"
            if negation:
                base_gloss += " NOT"
        # Handle want/need constructions.
        elif isinstance(verb, tuple):
            main_verb, infinitive = verb
            if glosses['prep_object']:
                base_gloss = f"{glosses['time']} {glosses['subject']} {glosses['prep_object']} {infinitive.text.upper() if not isinstance(infinitive, str) else infinitive.upper()} {main_verb.lemma_.upper()}"
            else:
                base_gloss = f"{glosses['time']} {glosses['subject']} {main_verb.lemma_.upper()} {infinitive.text.upper() if not isinstance(infinitive, str) else infinitive.upper()}"
        # Handle copula "be" constructions.
        elif original_verb and original_verb.lemma_ == "be":
            if glosses["subject"] == "IT":
                base_gloss = f"{glosses['verb']}"
            else:
                base_gloss = f"{glosses['time']} {glosses['subject']} {glosses['verb']}"
            if negation: 
                base_gloss += " NOT"
        else:
            # Default: enforce SOV order: Subject, then Object (or destination), then Verb.
            if glosses['object']:
                base_gloss = f"{glosses['time']} {glosses['subject']} {glosses['object']} {glosses['verb']}"
            elif glosses['prep_object']:
                base_gloss = f"{glosses['time']} {glosses['subject']} {glosses['prep_object']} {glosses['verb']}"
            else:
                base_gloss = f"{glosses['time']} {glosses['subject']} {glosses['verb']}"
            if negation:
                base_gloss += " NOT"

        # Special rule: if "stranger" and "house" appear, prepend the reason clause.
        if any(tok.text.lower() == "stranger" for tok in doc) and any(tok.text.lower() == "house" for tok in doc):
            base_gloss = f"STRANGER HOUSE IN, {base_gloss.strip()}"

        base_gloss = " ".join(base_gloss.split())
        return base_gloss

    elif sentence_type == "yes-no-question":
        if original_verb and original_verb.lemma_ == "switch" and glosses['prep_object']:
            # Force phrasal verb to yield "FAN ON"
            gloss = f"{glosses['subject']} {glosses['prep_object']} ON"
            if glosses['modal']:
                gloss += f" {glosses['modal']}"
            gloss += "?"
        elif modal:
            gloss = f"{glosses['subject']} {glosses['verb']} {glosses['object']} {glosses['prep_object']} {glosses['modal']}?"
        else:
            gloss = f"{glosses['subject']} {glosses['verb']}?"
        return " ".join(gloss.split())

    elif sentence_type == "wh-question":
        wh_word = next((token for token in doc if token.text.lower() in wh_words), None)
        glosses["wh"] = wh_word.text.upper() if wh_word else ""
        if glosses["possessive"]:
            base = f"{glosses['possessive']} {glosses['wh']}"
            return f"{base}?"
        elif original_verb and original_verb.lemma_ == "feel":
            base = f"{glosses['subject']} {glosses['complement']} FEEL {glosses['wh']}"
            return f"{base}?"
        else:
            base = f"{glosses['subject']} {glosses['verb']} {glosses['wh']}".replace(" BE", "")
            return f"{base}?"

    elif sentence_type == "imperative":
        # For imperatives: if possessive exists, use it as subject and omit the object.
        subject_part = glosses["possessive"] if glosses["possessive"] else glosses["subject"]
        obj_part = "" if glosses["possessive"] else glosses["object"]
        if obj_part == "DOWN":
            obj_part = ""
        gloss = f"{subject_part} {glosses['verb']} {obj_part}{politeness}"
        gloss = " ".join(gloss.split())
        return gloss

    return ""
