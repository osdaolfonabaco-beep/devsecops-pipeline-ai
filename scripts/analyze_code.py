import os
import anthropic
import requests # We use 'requests' to talk to the GitHub API
from dotenv import load_dotenv

# --- 1. CONFIGURATION AND VARIABLE LOADING ---
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# GitHub Actions environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
PR_NUMBER = os.getenv("PR_NUMBER")
GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")

if not ANTHROPIC_API_KEY:
    print("Error: ANTHROPIC_API_KEY not found.")
    exit(1)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# --- 2. ANALYSIS FUNCTIONS (Now in English) ---

def read_file_content(filepath):
    """Reads and returns the content of a file."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at {filepath}"
    except Exception as e:
        return f"Error reading {filepath}: {e}"

def get_security_analysis(file_content, filename):
    """Sends the file content to Anthropic Haiku for security analysis."""
    print(f"--- Starting AI analysis (Haiku) for: {filename} ---")
    
    # THE SYSTEM PROMPT IS NOW IN ENGLISH
    SYSTEM_PROMPT = """
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
    
    # The user prompt is also in English
    USER_PROMPT = f"Analyze the following file: `{filename}`\n\nContent:\n```{file_content}```"
    
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
        return f"Error during AI analysis: {e}"

# --- 3. GITHUB POSTING FUNCTION (No changes needed) ---

def post_comment_to_pr(report_body):
    """Posts the analysis report as a comment on the PR."""
    
    if not all([GITHUB_TOKEN, PR_NUMBER, GITHUB_REPOSITORY]):
        print("Missing GitHub environment variables. Skipping PR comment.")
        return

    url = f"{GITHUB_API_URL}/repos/{GITHUB_REPOSITORY}/issues/{PR_NUMBER}/comments"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    body = {"body": report_body}
    
    print(f"--- Posting comment to Pull Request #{PR_NUMBER} ---")
    
    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status() 
        print("Comment posted successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error posting comment to GitHub: {e}")
        if e.response is not None:
            print(f"Server Response: {e.response.text}")

# --- 4. MAIN SCRIPT (Now in English) ---

if __name__ == "__main__":
    files_to_analyze = [
        "app/main.py",
        "infra/main.tf"
    ]
    
    # Report header is now in English
    full_report = "## 🤖 AI Security Analysis Report (Haiku)\n\n"
    full_report += "I have analyzed the new code and found the following:\n\n"
    
    for file_path in files_to_analyze:
        content = read_file_content(file_path)
        analysis_report = get_security_analysis(content, file_path)
        
        full_report += f"### Analysis for: `{file_path}`\n"
        full_report += analysis_report
        full_report += "\n---\n" # Separator
    
    if PR_NUMBER:
        post_comment_to_pr(full_report)
    else:
        # Local execution log is now in English
        print("--- LOCAL OR 'MAIN' BRANCH EXECUTION (NOT A PR) ---")
        print(full_report)
