import subprocess
from ai_commit import ollama_client

def get_staged_files() -> list[str]:
    """
    Retrieves a list of staged files, filtering out noise.
    """
    
    command = [
        "git", "diff", "--staged", "--name-only", 
        "--", ".", 
        ":!*-lock.json", 
        ":!*.lock", 
        ":!*.min.js", 
        ":!*.svg"
    ]
    
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
    
    if result.returncode != 0:
        raise RuntimeError(f"Git command failed:\n{result.stderr}")
        
    return [f for f in result.stdout.strip().split('\n') if f]

def get_file_diff(filepath: str) -> str:
    """
    Retrieves the staged diff for a specific file.
    """
    
    command = ["git", "diff", "--staged", "--", filepath]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
    
    return result.stdout.strip()

def extract_and_chunk_diffs(max_chunk_size: int = 4000) -> str:
    """
    Maps across all staged files, combines their changes and returns a summary of changes.
    """
    files = get_staged_files()
    if not files:
        raise ValueError("No staged changes found. Stage files first with `git add`.")

    processed_chunks = []

    for file in files:
        diff = get_file_diff(file)
        
        if len(diff) > max_chunk_size:
            print(f"File {file} exceeds chunk limit. Running Map summarization...")
            safe_diff = diff[:max_chunk_size] + "\n...[TRUNCATED FOR SUMMARIZATION]..."
            
            summary = ollama_client.summarize_file(file, safe_diff)
            
            processed_chunks.append(f"File: {file}\nSummary of changes: {summary}")
        else:
            processed_chunks.append(f"File: {file}\nRaw Diff:\n{diff}")

    final_payload = "\n\n".join(processed_chunks)
    return final_payload

if __name__ == "__main__":
    try:
        final_context = extract_and_chunk_diffs()
        print(final_context)
    except Exception as e:
        print(f"Error: {e}")