import logging
import json
from pdf_processor import get_pages_content, bm25_search

LOG_FILE = "readai.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==========================================
# READAI PERSONA
# ==========================================
READAI_PERSONA = """
You are ReadAI — a smart personal reading assistant.

Your role:
- Help users understand books and documents better.
- Generate clear, detailed summaries of reading material.
- Answer questions based on the provided content only.
- Be professional, helpful, and encouraging.

STRICT RULES:
- Use ONLY the provided content to answer.
- Do NOT make up information.
- If answer is not in content, say: "This information is not available in the provided content."
- Always be concise but complete.

*** LANGUAGE INSTRUCTION ***
{language_instruction}
"""

# ==========================================
# LANGUAGE DETECTOR
# ==========================================
URDU_WORDS = {
    'kya', 'hai', 'hain', 'mein', 'ka', 'ki', 'ke', 'se', 'ko',
    'aur', 'nahi', 'nahin', 'koi', 'yeh', 'ye', 'wo', 'woh',
    'ap', 'aap', 'kab', 'kahan', 'kyun', 'kaise', 'kitna',
    'kitni', 'batao', 'bata', 'chahiye', 'milta', 'milti',
    'hoga', 'hogi', 'tha', 'thi', 'par', 'pe', 'wala',
    'wali', 'liye', 'sath', 'lekin', 'magar', 'phir', 'bas',
    'sirf', 'bhi', 'hi', 'jo', 'jab', 'tak', 'ya', 'agar',
    'karen', 'hota', 'hoti', 'karta', 'karti', 'karna',
    'chahta', 'chahti', 'pata', 'maloom', 'theek', 'bilkul',
    'zaroor', 'abhi', 'baad', 'pehle', 'accha', 'acha', 'ji',
    'haan', 'konsa', 'konsi', 'kuch', 'sab', 'bohat', 'bahut',
}

ENGLISH_WORDS = {
    'what', 'where', 'when', 'how', 'which', 'who', 'why',
    'is', 'are', 'was', 'were', 'do', 'does', 'did',
    'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for',
    'and', 'or', 'but', 'with', 'from', 'by', 'about',
    'can', 'could', 'will', 'would', 'should', 'have', 'has',
    'your', 'my', 'this', 'that', 'please', 'tell', 'me',
    'summary', 'explain', 'describe', 'define', 'list',
    'generate', 'create', 'make', 'give', 'show',
}

def detect_language(text: str) -> str:
    words = text.lower().split()
    if not words:
        return "ENGLISH"
    urdu_count = sum(1 for w in words if w in URDU_WORDS)
    english_count = sum(1 for w in words if w in ENGLISH_WORDS)
    if english_count > 0 and urdu_count == 0:
        return "ENGLISH"
    if urdu_count / len(words) > 0.15:
        return "URDU"
    return "ENGLISH"

def build_language_instruction(lang: str) -> str:
    if lang == "URDU":
        return (
            "User ne Urdu ya Roman Urdu mein likha hai.\n"
            "Aap ka jawab 100% Urdu script mein hona chahiye.\n"
            "Roman Urdu (English letters mein Urdu) nahi likhna.\n"
            "Sirf technical terms jaise 'Chapter', 'Page' English mein rakh sakte hain."
        )
    else:
        return (
            "User has written in English.\n"
            "Reply 100% in English only.\n"
            "Do not use any Urdu or Roman Urdu phrases."
        )


# ==========================================
# SUMMARY GENERATOR
# ==========================================
def generate_summary(book_id, page_from, page_to, client, model_name):
    try:
        content = get_pages_content(book_id, page_from, page_to)
        if not content:
            return "❌ Could not extract content from the selected pages."

        prompt = f"""
You are ReadAI. Generate a clear, detailed, and well-structured summary of the following content.

Content (Pages {page_from} to {page_to}):
{content}

Instructions:
- Start with a brief overview (2-3 sentences).
- List the key points covered.
- End with main takeaways.
- Be thorough but concise.
- Use bullet points where appropriate.
"""
        response = client.chat.completions.create(
            model=model_name,
            temperature=0.3,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        summary = response.choices[0].message.content
        logging.info(f"✅ Summary generated for book {book_id}, pages {page_from}-{page_to}")
        return summary

    except Exception as e:
        logging.error(f"❌ Summary generation error: {e}")
        return "❌ Summary generation failed. Please try again."


# ==========================================
# Q&A — VECTORLESS RAG (BM25)
# ==========================================
def answer_question(book_id, page_from, page_to, question, client, model_name):
    try:
        # BM25 se relevant pages dhundo — poora range nahi bhejte
        context = bm25_search(book_id, question, top_k=4)

        # BM25 fail ho toh fallback: page range se
        if not context:
            context = get_pages_content(book_id, page_from, page_to)
        if not context:
            return "❌ Could not extract content from the selected pages."

        lang = detect_language(question)
        lang_instruction = build_language_instruction(lang)
        system_prompt = READAI_PERSONA.replace("{language_instruction}", lang_instruction)

        response = client.chat.completions.create(
            model=model_name,
            temperature=0,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Relevant Book Content:\n\n{context}\n\nQuestion: {question}"
                }
            ]
        )
        answer = response.choices[0].message.content
        logging.info(f"✅ BM25 Q&A answered for book {book_id}")
        return answer

    except Exception as e:
        logging.error(f"❌ Q&A error: {e}")
        return "❌ Could not answer the question. Please try again."


# ==========================================
# TEST
# ==========================================
if __name__ == "__main__":
    print("✅ ReadAI Bot ready!")
    print("🧠 AI Functions:")
    print("   - generate_summary()")
    print("   - answer_question()")
