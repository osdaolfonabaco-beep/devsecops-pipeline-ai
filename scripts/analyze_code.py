"""
scripts/analyze_code.py

This script is the core "brain" of the DevSecOps AI pipeline.
It is executed by the GitHub Actions workflow and performs the following:

1.  Reads specified files from the repository.
2.  Sends their content to the Anthropic API for security analysis.
3.  If running in a GitHub Pull Request, posts the analysis as a PR comment.
4.  If running locally or in 'main', prints the report to stdout.
"""

import os
import sys
import requests
import anthropic
from dotenv import load_dotenv
from typing import List, Optional

# --- Constants ---
# Files to be scanned by the AI
FILES_TO_ANALYZE: List[str] = [
    "app/main.py",
    "infra/main.tf"
]

# --- Environment and API Configuration ---
load_dotenv()
ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

# GitHub Actions environment variables
GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
PR_NUMBER: Optional[str] = os.getenv("PR_NUMBER")
GITHUB_API_URL: str = os.getenv("GITHUB_API_URL", "https://api.github.com")
GITHUB_REPOSITORY: Optional[str] = os.getenv("GITHUB_REPOSITORY")

# --- AI Client Initialization ---
try:
    if not ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY not found in environment.", file=sys.stderr)
        sys.exit(1)
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
except Exception as e:
    print(f"Error initializing Anthropic client: {e}", file=sys.stderr)
    sys.exit(1)

def read_file_content(filepath: str) -> str:
    """
    Reads and returns the content of a file.

    Args:
        filepath (str): The relative path to the file.

    Returns:
        str: The content of the file.
    
    Raises:
        FileNotFoundError: If the file is not found.
        IOError: If an error occurs during file reading.
    """
    print(f"--- Reading file: {filepath} ---")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}", file=sys.stderr)
        raise
    except IOError as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        raise

def get_security_analysis(file_content: str, filename: str) -> str:
    """
    Sends the file content to the Anthropic API for security analysis.

    Args:
        file_content (str): The source code or config to analyze.
        filename (str): The name of the file being analyzed (for context).

    Returns:
        str: A Markdown-formatted security report from the AI.
    """
    print(f"--- Starting AI analysis (Haiku) for: {filename} ---")
    
    SYSTEM_PROMPT: str = """
    You are a senior cybersecurity and DevSecOps expert with 20 years of experience.
    Your task is to analyze the following code file for security vulnerabilities 
    and bad practices.
    
    For each vulnerability found:
    1.  Identify the vulnerability type (e.g., SQL Injection, S3 Public Access).
    2.  Cite the exact problematic line(s) of code.
    3.  Explain why it is a vulnerability.
    4.  Provide a code suggestion for remediation.
    
    If you find no vulnerabilities, state this explicitly.
    Respond in Markdown format.
    """
    
    USER_PROMPT: str = f"Analyze the following file: `{filename}`\n\nContent:\n```{file_content}```"
    
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2048,
            temperature=0.2,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": USER_PROMPT}]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error calling Anthropic API: {e}", file=sys.stderr)
        return f"Error: Could not get analysis from AI. Details: {e}"

def post_comment_to_pr(report_body: str):
    """
    Posts the analysis report as a comment on the GitHub Pull Request.

    Args:
        report_body (str): The complete Markdown-formatted report.
    """
    if not all([GITHUB_TOKEN, PR_NUMBER, GITHUB_REPOSITORY]):
        print("Missing GitHub environment variables. Skipping PR comment.")
        return

    url: str = f"{GITHUB_API_URL}/repos/{GITHUB_REPOSITORY}/issues/{PR_NUMBER}/comments"
    
    headers: dict = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    body: dict = {"body": report_body}
    
    print(f"--- Posting comment to Pull Request #{PR_NUMBER} ---")
    
    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        print("Comment posted successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error posting comment to GitHub: {e}", file=sys.stderr)
        if e.response is not None:
            print(f"Server Response: {e.response.text}", file=sys.stderr)

def main():
    """
    Main execution function for the script.
    
    Orchestrates the file reading, analysis, and reporting.
    """
    full_report: str = "## 🤖 AI Security Analysis Report (Haiku)\n\n"
    full_report += "I have analyzed the new code and found the following:\n\n"
    
    has_errors: bool = False
    
    for file_path in FILES_TO_ANALYZE:
        try:
            content = read_file_content(file_path)
            analysis_report = get_security_analysis(content, file_path)
            
            full_report += f"### Analysis for: `{file_path}`\n"
            full_report += analysis_report
            full_report += "\n---\n"
            
        except Exception as e:
            print(f"Failed to analyze {file_path}: {e}", file=sys.stderr)
            full_report += f"### Analysis for: `{file_path}`\n"
            full_report += f"**Error:** Could not analyze this file. Details: {e}\n---\n"
            has_errors = True
    
    # Decide how to output the report
    if PR_NUMBER:
        post_comment_to_pr(full_report)
    else:
        print("--- LOCAL OR 'MAIN' BRANCH EXECUTION (NOT A PR) ---")
        print(full_report)
        
    if has_errors:
        print("One or more files failed to analyze.", file=sys.stderr)
        sys.exit(1) # Exit with an error code if any analysis failed

if __name__ == "__main__":
    main()
