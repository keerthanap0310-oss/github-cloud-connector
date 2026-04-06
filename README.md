# GitHub Cloud Connector

A high-performance GitHub API connector built with **FastAPI**. This application allows you to interact with GitHub resources (Repositories, Issues, Pull Requests, Commits) through a standardized RESTful interface.

---

## 🚀 Features

- **OAuth-ready Authentication**: Securely handles GitHub Personal Access Tokens (PAT).
- **Comprehensive API Coverage**:
  - **Repositories**: List user/org repos and fetch metadata.
  - **Issues**: List and programmatically create issues.
  - **Pull Requests**: List and create PRs between branches.
  - **Commits**: Fetch detailed commit history for any branch.
- **Robust Error Handling**: Standardized JSON error responses for API failures (401, 403, 404, etc.).
- **Automatic Docs**: Interactive Swagger UI generated out-of-the-box.

---

## 🛠️ Setup Instructions

### 1. Prerequisites
- **Python 3.10+**
- A **GitHub Personal Access Token (Classic)**.
  - **To get one**: Go to GitHub Settings -> Developer settings -> Personal access tokens -> Tokens (classic).
  - **Important**: Ensure you check the **`repo`** scope box.

### 2. Installation
1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd github-cloud-connector
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Environment Configuration
Create a `.env` file in the project root:

```bash
touch .env
```

Open `.env` and configure the following variables:

| Variable | Description | Example |
| :--- | :--- | :--- |
| `GITHUB_PAT` | **Required**. Your GitHub Personal Access Token. | `ghp_ABC123...` |
| `GITHUB_API_BASE_URL` | Optional. Defaults to `https://api.github.com`. | `https://api.github.com` |
| `REQUEST_TIMEOUT` | Optional. Request timeout in seconds. | `10` |

> **Note**: The `.env` file contains sensitive information and is automatically ignored by Git (via `.gitignore`) to prevent accidental commits.

---

## 🏃 Running the Project

Run the application using Uvicorn from the project root:

```bash
# From the directory containing 'app/'
uvicorn app.main:app --reload
```

- **API URL**: `http://127.0.0.1:8000`
- **Interactive Docs (Swagger)**: `http://127.0.0.1:8000/`

---

## 📖 API Documentation & Examples

### **1. Authentication**
#### `GET /auth/me`
Validate your token and see your GitHub profile.
- **Example Response**:
  ```json
  { "login": "keerthanap0310-oss", "id": 12345, "public_repos": 10 }
  ```

### **2. Repositories**
#### `GET /repos/user/{username}`
List public repositories for any GitHub user.
- **Path Parameter**: `username` = `keerthanap0310-oss`
- **Query Parameter**: `sort` = `updated`, `per_page` = `30`

#### `GET /repos/{owner}/{repo}`
Fetch detailed metadata for a specific repository.
- **Path Parameters**: `owner` = `fastapi`, `repo` = `fastapi`

### **3. Issues**
#### `GET /repos/{owner}/{repo}/issues`
List issues (excluding PRs) for a repository.
- **Path Parameters**: `owner` = `microsoft`, `repo` = `vscode`
- **Query Parameter**: `state` = `open` (or `closed`, `all`)

#### `POST /repos/{owner}/{repo}/issues`
Create a new issue in a repository.
- **Example JSON Body**:
  ```json
  {
    "title": "Bug: Connection Timeout",
    "body": "The app timed out while fetching repos.",
    "labels": ["bug", "high-priority"],
    "assignees": ["keerthanap0310-oss"]
  }
  ```

### **4. Pull Requests**
#### `POST /repos/{owner}/{repo}/pulls`
Create a new pull request.
- **Example JSON Body**:
  ```json
  {
    "title": "Add logging to github client",
    "head": "feature-logging",
    "base": "main",
    "body": "Detailed logs added for debugging.",
    "draft": false
  }
  ```
  *(Note: The `head` branch must already exist on GitHub.)*

### **5. Commits**
#### `GET /repos/{owner}/{repo}/commits`
Fetch the commit history for a repository.
- **Path Parameters**: `owner` = `python`, `repo` = `cpython`
- **Query Parameter**: `branch` = `main`

---

## 📂 Project Structure

- [main.py](file:///Users/keerthanap/Downloads/backend-test/app/main.py): Entry point and router configuration.
- [github_client.py](file:///Users/keerthanap/Downloads/backend-test/app/github_client.py): Async HTTP client for GitHub API interaction.
- [routers/](file:///Users/keerthanap/Downloads/backend-test/app/routers): Modular API endpoints (repos, issues, pulls, commits).
- [schemas.py](file:///Users/keerthanap/Downloads/backend-test/app/schemas.py): Pydantic models for request/response validation.
- [config.py](file:///Users/keerthanap/Downloads/backend-test/app/config.py): Settings management with Pydantic.
- [error_handlers.py](file:///Users/keerthanap/Downloads/backend-test/app/error_handlers.py): Global exception handling for GitHub errors.
