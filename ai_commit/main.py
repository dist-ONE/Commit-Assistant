import sys
import os
import subprocess
import argparse
from ai_commit.git_handler import extract_and_chunk_diffs
from ai_commit.ollama_client import generate_commit_message
from ai_commit.memory import CommitMemory

def get_repo_name() -> str:
    """
    Gets the name of the root folder of the current git repository.
    """

    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, encoding="utf-8", check=True)
    return os.path.basename(result.stdout.strip())

def get_latest_commit_hash() -> str:
    """
    Retrieves the SHA-1 hash of the commit we just made.
    """

    result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, encoding="utf-8", check=True)
    return result.stdout.strip()

def execute_commit(commit_message: str):
    """
    Executes the git commit command.
    """

    try:
        subprocess.run(["git", "commit", "-m", commit_message], encoding="utf-8", check=True)
        print("\nSuccessfully committed!")
    except subprocess.CalledProcessError as e:
        print(f"\nFailed to commit: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Local AI Git Commit Assistant with RAG Memory")
    parser.parse_args() 

    try:
        repo_name = get_repo_name()
        memory = CommitMemory(repo_name)

        print("Analyzing staged files...")
        diff_payload = extract_and_chunk_diffs()
        
        print("Retrieving semantic memory and generating message...")
        similar_commits = memory.get_similar_commits(diff_payload)
        commit_message = generate_commit_message(diff_payload, similar_commits)
        
        print("\n" + "="*50)
        print(" GENERATED COMMIT MESSAGE")
        print("="*50)
        print(f"\n{commit_message}\n")
        print("="*50 + "\n")
        
        final_message = commit_message
        while True:
            choice = input("Commit? [y(accept) / n(reject) / e(edit)]: ").strip().lower()
            
            if choice == 'y':
                break
            elif choice == 'e':
                print("\nType your new commit message (press Enter to confirm):")
                user_edit = input("> ").strip()
                if user_edit:
                    final_message = user_edit
                    break
                else:
                    print("Message cannot be empty. Try again.")
            elif choice in ('n', ''):
                print("Commit aborted.")
                sys.exit(0)

        execute_commit(final_message)
        
        commit_hash = get_latest_commit_hash()
        memory.save_commit(diff_payload, final_message, commit_hash)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()