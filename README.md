# Human-Like Text Generator

This Flask web application generates human-like, conversational text using the OpenAI API. It takes an input paragraph and rephrases it to sound less polished and more casual, mimicking the imperfections, slang, and tone of everyday speech.

---

## Features

- **Text Generation:** Rewrite a given paragraph into a conversational and chaotic tone.
- **Natural Imperfections:** Includes filler words, unfinished thoughts, slang, typos, and occasional grammar mistakes.
- **OpenAI Integration:** Uses OpenAI GPT-4 API for text generation.
- **Customizable:** Users can add optional "seeds" to influence the tone of the output.

---

## Installation

1. Clone the repository:
    ```bash
    git clone git@github.com:dilawaizkhan08/ai_to_human.git
    ```

2. Navigate to the project directory:
    ```bash
    cd ai_to_human
    ```

3. Set up a virtual environment (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the Streamlit app:
    ```bash
    python3 test.py
    ```

2. The application will open in your web browser. You can now start querying.