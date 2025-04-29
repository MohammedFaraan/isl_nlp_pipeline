# modules/generator.py

def generate_gloss(transformed_gloss, sentence_type):
    transformed_gloss = transformed_gloss.strip()
    if sentence_type in ("yes-no-question", "wh-question"):
        if not transformed_gloss.endswith("?"):
            transformed_gloss += "?"
    return " ".join(transformed_gloss.split())
