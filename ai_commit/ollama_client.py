import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma4:31b-cloud" 

def generate_commit_message(diff_payload: str, past_commits: list[str]) -> str:
    """
    Sends the git diff and few-shot examples to the local Ollama API.
    """
    
    system_prompt = (
        "You are an expert software engineer. Generate a concise, conventional "
        "commit message for the provided git diff.\n"
        "Format: <subject>\n"
        "Rules:\n"
        "1. Keep the subject line under 50 characters.\n"
        "2. Do NOT output explanations, markdown formatting, or introductory text."
    )

    if past_commits:
        system_prompt += "\n\nHere are examples of past commits from this repository to match the style:\n"
        for msg in past_commits:
            system_prompt += f"- {msg}\n"

    payload = {
        "model": MODEL_NAME,
        "system": system_prompt,
        "prompt": f"Here is the diff:\n\n{diff_payload}",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=45)
        response.raise_for_status()
        
        data = response.json()
        return data.get("response", "").strip()
        
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Could not connect to Ollama."
        )
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ollama API request failed: {e}")
    
def summarize_file(filename: str, diff_payload: str) -> str:
    """
    Sends a truncated file diff to Ollama to generate a short summary.
    """
    
    system_prompt = (
        f"You are an expert developer analyzing a git diff for the file '{filename}'. "
        "Summarize the core technical changes in exactly one concise sentence. "
        "Do NOT output any conversational text, explanations, or markdown formatting. "
        "Output ONLY the summary sentence."
    )

    payload = {
        "model": MODEL_NAME,
        "system": system_prompt,
        "prompt": diff_payload,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data.get("response", "").strip()
        
    except requests.exceptions.RequestException as e:
        return f"[Failed to summarize {filename} automatically due to API error]"

if __name__ == "__main__":
    print("Testing connection to Ollama...")
    try:
        test_msg = generate_commit_message("diff --git a/test.txt b/test.txt\n+ Added a new test file.", ["Initial commit", "Added feature X", "Fixed bug Y"])
        print(f"Response:\n{test_msg}")
    except Exception as e:
        print(f"Error: {e}")