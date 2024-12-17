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
FILLER_WORDS = ["uh", "well", "you know", "like", "I mean", "basically", "honestly"]
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
def create_human_like_completion(prompt, model="gpt-4", temperature=0.9, max_tokens=300):
    """Generates text using OpenAI's GPT model with randomness."""
    try:
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
    """Prepares the prompt with guidelines for generating natural human-like text."""
    human_seed_text = f"Here's my take: {human_seed}" if human_seed else ""
    return f"""
Rewrite the following paragraph to sound human-like, conversational, and chaotic in tone. 
Add imperfections, filler words, informal slang, unfinished thoughts, self-corrections, 
and occasional grammar mistakes to make it unpredictable.

Avoid sounding robotic or overly polished. Make it sound like a casual conversation with a friend.

{human_seed_text}

Original Paragraph:
{paragraph}

Guidelines:
1. Include filler words (uh, well, you know) and natural pauses.
2. Use informal phrases, contractions, and regional slang.
3. Add unfinished thoughts, rhetorical questions, or sudden tone changes.
4. Introduce occasional grammar mistakes or awkward phrasing.
5. Make it less polished, like a human explaining it casually.

Rewritten Paragraph:
"""

def post_process_text(text):
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

    return " ".join(processed_sentences).strip()


# Routes
@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_text():
    data = request.json
    paragraph = data.get('paragraph', '')
    human_seed = data.get('human_seed', '')

    if not paragraph:
        return jsonify({"error": "Paragraph is required"}), 400

    try:
        # Prepare the prompt and generate AI text
        prompt = prepare_prompt_for_human_like_text(paragraph, human_seed)
        ai_generated_text = create_human_like_completion(prompt)

        # Post-process the text to enhance its human-like quality
        humanized_text = post_process_text(ai_generated_text)
        return jsonify({"humanized_text": humanized_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
