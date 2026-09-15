import sys
import subprocess
import argparse
from git_handler import extract_and_chunk_diffs
from ollama_client import generate_commit_message

def execute_commit(commit_message: str):
    """Executes the git commit command with the generated message."""
    try:
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("\nSuccessfully committed!")
        
    except subprocess.CalledProcessError as e:
        print(f"\nFailed to commit: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Local AI Git Commit Assistant")
    parser.parse_args() 

    print("Analyzing staged files...")
    try:
        diff_payload = extract_and_chunk_diffs()
        
        print("Generating commit message via Ollama...")
        commit_message = generate_commit_message(diff_payload)
        
        print("\n" + "-"*50)
        print(" GENERATED COMMIT MESSAGE")
        print("-"*50)
        print(f"\n{commit_message}\n")
        print("-"*50 + "\n")
        
        choice = input("Do you want to commit with this message? [Y/N]: ").strip().lower()
        
        if choice == 'y':
            execute_commit(commit_message)
        else:
            print("Commit aborted. You can modify your staged files and try again.")
            
    except ValueError as ve:
        print(f"Notice: {ve}")
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()