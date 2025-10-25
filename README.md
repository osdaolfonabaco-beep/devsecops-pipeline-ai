# Project 4: DevSecOps Pipeline with AI Code Review

[![AI Security Code Review Workflow Status](https://github.com/osdaolfonabaco-beep/devsecops-pipeline-ai/actions/workflows/security-scan.yml/badge.svg)](https://github.com/osdaolfonabaco-beep/devsecops-pipeline-ai/actions)

This project demonstrates a professional-grade DevSecOps pipeline built on GitHub Actions. The system automatically intercepts Pull Requests, scans code (Python/Flask) and infrastructure (Terraform) for vulnerabilities using an LLM (Anthropic Claude 3 Haiku), and posts a detailed security report as a PR comment, acting as an AI-powered security reviewer.

## 🚀 Live Demo: The AI Bot in Action

The value of this project isn't just the analysis; it's the **native integration into the developer's workflow**.

Instead of requiring a developer to hunt through hidden logs, feedback is immediate and delivered directly to the Pull Request. This promotes a true **"shift-left security"** mindset.

### The Problem: Vulnerable Code
The pipeline was designed to catch critical vulnerabilities, such as a **SQL Injection** flaw in the application code and a **Public S3 Bucket** in the Terraform configuration.

![Vulnerable Code](.github/assets/01-vulnerable-code.png)

### The Solution: AI Report on the Pull Request
The GitHub Actions workflow triggered, executed the analysis script, and posted this detailed report, effectively blocking a potentially insecure code merge.

![AI Bot Report on PR](.github/assets/03-bot-comment.png)

![Terraform Analysis](.github/assets/04-terraform-analysis.png)

---

## 🛠️ Architecture and Workflow

1.  **Trigger:** The GitHub Actions workflow (`.github/workflows/security-scan.yml`) activates on every `push` or `pull_request` to the `main` branch.
2.  **Permissions:** The workflow requests `pull-requests: write` permissions to allow it to post comments.
3.  **Environment Setup:** The job checks out the code, sets up Python, and installs dependencies from `requirements.txt`.
4.  **Analysis Execution:**
    * The core Python script (`scripts/analyze_code.py`) is executed.
    * It reads environment variables, including the `ANTHROPIC_API_KEY` (stored securely in **GitHub Secrets**).
    * It identifies the target files to scan (e.g., `app/main.py`, `infra/main.tf`).
5.  **AI Consultation:**
    * The script sends the content of each file to the Anthropic API.
    * It uses a custom **System Prompt** designed to make Claude 3 Haiku act as a senior cybersecurity and DevSecOps expert.
6.  **Report Publishing:**
    * The script aggregates the AI's responses into a single Markdown report.
    * If it detects it's running in a PR (by checking for the `PR_NUMBER` variable), it uses the GitHub API (`requests`) to post the report as a comment on that PR.

![Successful Pipeline in GitHub Actions](.github/assets/02-pipeline-success.png)

---

## 💻 Tech Stack

* **CI/CD:** GitHub Actions
* **AI & LLMs:** Anthropic Claude 3 Haiku
* **Language:** Python
* **Infrastructure as Code (IaC):** Terraform
* **Framework (Demo App):** Flask
* **Security:** GitHub Secrets, GitHub Push Protection
* **Version Control:** Git

---

## ⚙️ Local Setup and Execution

1.  Clone the repository.
2.  Create and activate a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Create a `.env` file in the root directory and add your API key:
    ```
    ANTHROPIC_API_KEY='sk-ant-...'
    ```
5.  Run the analysis script locally:
    ```bash
    python scripts/analyze_code.py
    ```
