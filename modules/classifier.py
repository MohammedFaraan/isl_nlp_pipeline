from utils.helpers import load_list

# Load wh-words from file
wh_words = load_list('data/wh_words.txt')

def classify_sentence(doc):
    if any(token.text.lower() in ["?", *wh_words] for token in doc):  # Use imported wh_words
        if any(token.text.lower() in wh_words for token in doc):
            return "wh-question"
        return "yes-no-question"
    elif any(token.dep_ == "ROOT" and token.pos_ == "VERB" and doc[0].dep_ != "nsubj" for token in doc):
        return "imperative"
    return "declarative"