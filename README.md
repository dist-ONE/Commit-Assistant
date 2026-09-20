# Git-Recall

A local CLI tool that generates conventional git commit messages using Ollama. 

Unlike standard AI commit generators, `Git-Recall` uses a local vector database (ChromaDB) to remember your past commits. This means it learns your repository's specific commit style over time instead of just guessing. It also runs 100% locally, so your unreleased code is never sent to a third-party API.

## Features

* **Fully Local and Private:** Powered by Ollama. No API keys required, and your code never leaves your machine.
* **Semantic Memory:** Remembers your past commits on a per-repository basis to match your specific coding style.
* **Smart Diff Handling:** Uses a chunking system to summarize massive file changes without blowing up the LLM's context window.
* **Human in the Loop:** Always prompts you to accept, reject, or manually edit the generated message before actually committing.

## Prerequisites

1. **Python 3.9+**
2. **Git**
3. **[Ollama](https://ollama.com/)** installed and running on your machine.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/Git-Recall.git
   cd git-recall
   ```

2. Install the CLI globally (in editable mode):
   ```bash
   pip install -e .
   ```

3. Pull the required models via Ollama:
   ```bash
   ollama pull llama3
   ollama pull nomic-embed-text
   ```
   *(Note: `nomic-embed-text` is required for the local vector database, but you can change the main generation model by editing `MODEL_NAME` in `src/ollama_client.py`)*

## Usage

Using `git-recall` is designed to be a drop-in replacement for `git commit`. 

1. Stage your files normally:
   ```bash
   git add .
   ```

2. Run the tool from anywhere inside your repository:
   ```bash
   git-recall
   ```

3. The tool will analyze the diff, check your commit history, and generate a message. You will be prompted with:
   ```text
   Commit? [y(accept) / n(reject) / e(edit)]:
   ```
   If you choose `e` to edit, your manually typed message will be saved to the database so the AI learns from your correction for next time.

## How it Works (Under the Hood)

1. **Extraction:** Reads `git diff --staged` and filters out noise like lockfiles and minified assets.
2. **Retrieval:** Embeds the diff and searches a local ChromaDB instance for similar past commits in the current repo.
3. **Generation:** Passes the diff and the retrieved past commits as examples to Llama 3.
4. **Ingestion:** Once a commit is finalized, its diff and message are saved back into ChromaDB to improve future generations.