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

# Filler words, slang, and self-corrections
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

    # If the text is too long, truncate it
    if current_word_count > target_word_count:
        return " ".join(words[:target_word_count])
    
    # If the text is too short, pad with filler words
    while current_word_count < target_word_count:
        words.append(random.choice(FILLER_WORDS))
        current_word_count += 1
    
    return " ".join(words)

def create_human_like_completion(prompt, word_count, model="gpt-4", temperature=0.9):
    """Generates text using OpenAI's GPT model while aiming for a specific word count."""
    try:
        # Estimate tokens: 1 word ~ 1.3 tokens; adjust max_tokens dynamically
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
Avoid overly formal language or robotic precision—let it flow naturally like a real conversation.

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
        # Random filler word at the start
        if random.random() < 0.3:
            sentence = f"{random.choice(FILLER_WORDS)}, {sentence}"

        # Add self-corrections or unfinished thoughts
        if random.random() < 0.2:
            sentence += f" {random.choice(SELF_CORRECTIONS)}"
        
        # Introduce typos randomly
        for correct, typo in COMMON_TYPO_MISTAKES.items():
            if correct in sentence and random.random() < 0.2:
                sentence = sentence.replace(correct, typo)
        
        # Introduce awkward phrasing or grammar errors
        if random.random() < 0.2:
            sentence = re.sub(r"(\bthe\b)", "uh, the", sentence, count=1)  # Example error
        
        # Add unfinished thoughts
        if random.random() < 0.1:
            sentence += " ... I mean, never mind."

        processed_sentences.append(sentence)
    
    # Slight shuffle in sentence order to break structure
    if random.random() < 0.2:
        random.shuffle(processed_sentences)

    processed_text = " ".join(processed_sentences).strip()

    # Normalize length to match target word count
    return truncate_or_pad_text(processed_text, target_word_count)

@app.route('/api/generate', methods=['POST'])
def generate_text():
    data = request.json
    paragraph = data.get('paragraph', '')
    human_seed = data.get('human_seed', '')

    if not paragraph:
        return jsonify({"error": "Paragraph is required"}), 400

    try:
        # Calculate input paragraph word count
        input_word_count = count_words(paragraph)

        # Prepare the prompt and generate AI text
        prompt = prepare_prompt_for_human_like_text(paragraph, human_seed)
        ai_generated_text = create_human_like_completion(prompt, input_word_count)

        # Post-process the text to match input length
        humanized_text = post_process_text(ai_generated_text, input_word_count)
        return jsonify({"humanized_text": humanized_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Routes
@app.route('/')
def serve_index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
