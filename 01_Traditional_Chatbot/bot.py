"""Deterministic intent matching. All campus information is fictional demo data."""
import re

MAX_MESSAGE_LENGTH = 500
RULES = [
    ("help", r"\b(help|menu|capabilities|commands)\b", "I can answer questions about library hours, admissions, tuition, and IT support. Try 'library hours', 'admissions', 'tuition', or 'IT support'. You can also say hello or goodbye. All campus details are fictional demonstration data."),
    ("library", r"\b(library|libraries)\b", "Demo library hours: Monday-Friday, 8 a.m.-8 p.m.; Saturday, 10 a.m.-4 p.m.; closed Sunday. These are fictional hours for this prototype."),
    ("admissions", r"\b(admission|admissions|apply|application|enroll|enrol)\b", "Demo admissions: complete an application and submit academic transcripts. Contact admissions@example.com for this fictional campus."),
    ("tuition", r"\b(tuition|fees|fee|cost|payment)\b", "Demo tuition help: contact finance@example.com for fee and payment information. This prototype does not provide real tuition amounts."),
    ("it_support", r"\b(it support|technical support|password|wifi|wi-fi|internet|login)\b", "Demo IT support: contact support@example.com for Wi-Fi or login help. Never share your password in this chat."),
    ("greeting", r"\b(hello|hi|hey)\b", "Hello! I am Campus Help Bot, a traditional rule-based chatbot. Type 'help' to see what I can do."),
    ("goodbye", r"\b(bye|goodbye|exit|quit)\b", "Goodbye! You can start another conversation whenever you like."),
]


def get_response(message):
    """Validate, normalize, match topic rules, and return an auditable reply."""
    if not isinstance(message, str):
        return {"intent": "invalid", "reply": "Please send your question as text."}
    if len(message) > MAX_MESSAGE_LENGTH:
        return {"intent": "invalid", "reply": "Please keep your message to 500 characters or fewer."}
    normalized = " ".join(message.casefold().split())
    if not normalized or not any(c.isalnum() for c in normalized):
        return {"intent": "invalid", "reply": "Please enter a question using words. Type 'help' for examples."}
    # Help takes precedence; multiple information topics require clarification.
    matches = [rule for rule in RULES if re.search(rule[1], normalized)]
    topics = [rule for rule in matches if rule[0] in {"library", "admissions", "tuition", "it_support"}]
    if matches and matches[0][0] == "help":
        selected = matches[0]
    elif len(topics) > 1:
        return {"intent": "clarify", "reply": "You mentioned several topics. Please ask about one at a time: library, admissions, tuition, or IT support."}
    elif topics:
        selected = topics[0]
    elif matches:
        selected = matches[0]
    else:
        return {"intent": "fallback", "reply": "I do not recognize that question yet. Type 'help' to see my supported topics."}
    return {"intent": selected[0], "reply": selected[2]}
