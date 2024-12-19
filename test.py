import os
import random
import re
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# Initialize OpenAI API with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not client.api_key:
    raise ValueError("OPENAI_API_KEY is missing. Please set it in your .env file.")

# Constants
FILLER_WORDS = ["well", "you know", "like", "I mean", "basically", "honestly"]
SELF_CORRECTIONS = [
    "Actually, scratch that...",
    "Wait, let me rephrase that.",
    "Hmm, maybe I should put it this way...",
    "No, that doesn't make sense. Let me try again."
]
COMMON_TYPO_MISTAKES = {
    "definitely": "definately",
    "receive": "recieve",
    "occurred": "occured",
    "separate": "seperate",
    "necessary": "neccessary",
}
IDIOMATIC_PHRASES = [
    "at the end of the day",
    "to be honest",
    "I guess you could say",
    "if you ask me",
    "you know what I mean?",
    "let's face it"
]

# Functions
def count_words(text):
    """Counts the number of words in a given text."""
    return len(re.findall(r'\b\w+\b', text))

def truncate_or_pad_text(text, target_word_count):
    """Ensures the text has a target word count by truncating or padding with filler words."""
    words = text.split()
    current_word_count = len(words)

    if current_word_count > target_word_count:
        return " ".join(words[:target_word_count])
    while current_word_count < target_word_count:
        words.append(random.choice(FILLER_WORDS))
        current_word_count += 1
    return " ".join(words)

def create_human_like_completion(prompt, word_count, model="gpt-4", temperature=0.9):
    """Generates text using OpenAI's GPT model while aiming for a specific word count."""
    try:
        max_tokens = int(word_count * 1.5)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.9,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating text: {e}"

def prepare_prompt_for_human_like_text(paragraph, human_seed=""):
    """Prepare a prompt to generate undetectable, human-like text."""
    human_seed_text = f"Here's how I'd put it: {human_seed}" if human_seed else ""
    return f"""
Reword the following paragraph to sound natural and conversational, as if a regular person were explaining it casually.

Key Instructions:
1. Use contractions and light filler words like "you know," "well," "I guess," or "pretty much."
2. Add occasional pauses, rhetorical questions, or informal phrasing.
3. Slightly vary sentence length and structure for a relaxed feel.
4. Make it sound like it was written quickly and casually, not like it was carefully polished.
5. Avoid perfect grammar—it's fine to have minor imperfections or tone shifts.

{human_seed_text}

Original Paragraph:
{paragraph}

Rewritten Paragraph:
"""

def post_process_text(text, target_word_count):
    """Adds imperfections, filler words, typos, tone shifts, and unfinished thoughts."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    processed_sentences = []
    
    for sentence in sentences:
        if random.random() < 0.3:
            sentence = f"{random.choice(FILLER_WORDS)}, {sentence}"
        if random.random() < 0.2:
            sentence += f" {random.choice(SELF_CORRECTIONS)}"
        for correct, typo in COMMON_TYPO_MISTAKES.items():
            if correct in sentence and random.random() < 0.2:
                sentence = sentence.replace(correct, typo)
        if random.random() < 0.2:
            sentence = re.sub(r"(\bthe\b)", " the", sentence, count=1)
        if random.random() < 0.1:
            sentence += " ... I mean, never mind."
        processed_sentences.append(sentence)
    if random.random() < 0.2:
        random.shuffle(processed_sentences)
    processed_text = " ".join(processed_sentences).strip()
    return truncate_or_pad_text(processed_text, target_word_count)

def chunk_text(text, chunk_size, overlap=50):
    """Splits text into chunks with overlap to ensure coherence."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks

@app.route('/api/generate', methods=['POST'])
def generate_text():
    data = request.json
    paragraph = data.get('paragraph', '')
    human_seed = data.get('human_seed', '')

    if not paragraph:
        return jsonify({"error": "Paragraph is required"}), 400

    try:
        chunks = chunk_text(paragraph, chunk_size=100, overlap=20)
        humanized_chunks = []
        for chunk in chunks:
            chunk_word_count = count_words(chunk)
            prompt = prepare_prompt_for_human_like_text(chunk, human_seed)
            ai_generated_text = create_human_like_completion(prompt, chunk_word_count)
            humanized_chunk = post_process_text(ai_generated_text, chunk_word_count)
            humanized_chunks.append(humanized_chunk)
        humanized_text = " ".join(humanized_chunks)
        return jsonify({"humanized_text": humanized_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def serve_index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
