# 👳‍♂️ Raju's Royal Artifacts — Bargaining Shopkeeper Agent

An AI-powered agentic web application built using **Gemini**, Google's **Agent Development Kit (ADK)**, **FastAPI**, and an interactive HTML5 web frontend.

This project implements the Google Codelab: **[Build your own "Bargaining Shopkeeper" Agent with Gemini 3 and ADK](https://codelabs.developers.google.com/agentic-app-gemini-3-adk)**.

---

## 🌟 Features

- **Dynamic Bargaining Persona**: Meet **Raju**, a witty, dramatic AI shopkeeper with Indian-English flair who negotiates prices and attempts to sell high!
- **Function Calling / Tool Use**: Raju uses a custom Python tool (`check_inventory`) to query real-time stock and prices:
  - 🪔 **Brass Lamp**: 50 coins (Stock: 5)
  - 🧣 **Silk Scarf**: 500 coins (Stock: 2)
  - 🕌 **Taj Mahal**: 2000 coins (Stock: 0 - *SOLD OUT*)
- **ADK FastAPI Runtime**: Powered by ADK's `InMemoryRunner` with automated session management and cross-origin resource sharing (CORS).
- **Vibrant Web Interface**: Glassmorphism Indian bazaar styled UI with item selection cards, typing indicators, and real-time chat.
- **Cross-Platform Compatibility**: Fully supported on **Windows (PowerShell/CMD)**, **Linux**, and **macOS**.

---

## 📋 Prerequisites Before Running

Ensure the following prerequisites are installed and ready before deploying:

1. **Python 3.10 or higher**:
   - Verify by running `python --version` (or `python3 --version`).
2. **Gemini API Key**:
   - Obtain a free API key from [Google AI Studio](https://aistudio.google.com/).

---

## ⚡ Option 1: Automated Deployment Using Scripts (Recommended)

You can set up dependencies, run tests, and deploy the server in **one single command**!

### 🪟 Windows (PowerShell)

1. Open PowerShell and navigate to the project directory:
   ```powershell
   cd raju-shop
   ```
2. Execute the automated setup script:
   ```powershell
   .\run_setup.ps1
   ```
3. *If prompted*, enter your `GEMINI_API_KEY`. The script will automatically configure your environment, run tests, start the server, and open `http://localhost:8000` in your web browser!

---

### 🐧 Linux & 🍎 macOS (Bash / Zsh)

1. Open terminal and navigate to the project directory:
   ```bash
   cd raju-shop
   ```
2. Make the script executable:
   ```bash
   chmod +x run_setup.sh
   ```
3. Execute the automated setup script:
   ```bash
   ./run_setup.sh
   ```
4. *If prompted*, enter your `GEMINI_API_KEY`. The script will build `.venv`, install packages, run tests, start uvicorn, and open `http://localhost:8000`.

---

## 🛠️ Option 2: Step-by-Step Manual Deployment

If you prefer deploying step-by-step manually, follow these instructions:

### 🪟 Windows Step-by-Step (PowerShell)

1. **Navigate to the project directory**:
   ```powershell
   cd raju-shop
   ```

2. **Create and activate virtual environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install required dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set your Gemini API Key**:
   ```powershell
   $env:GEMINI_API_KEY="your_actual_gemini_api_key_here"
   ```

5. **Start the FastAPI Web Server**:
   ```powershell
   $env:PYTHONPATH="."
   python -m uvicorn app.fast_api_app:app --host 127.0.0.1 --port 8000 --reload
   ```

6. **Access the application**:
   Open **`http://localhost:8000`** in your browser to talk to Raju!

---

### 🐧 Linux & 🍎 macOS Step-by-Step (Bash / Zsh)

1. **Navigate to the project directory**:
   ```bash
   cd raju-shop
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your Gemini API Key**:
   ```bash
   export GEMINI_API_KEY="your_actual_gemini_api_key_here"
   ```

5. **Start the FastAPI Web Server**:
   ```bash
   export PYTHONPATH="."
   python3 -m uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the application**:
   Open **`http://localhost:8000`** in your web browser.

---

## 🧪 Running Automated Tests

Run unit tests across platforms using `pytest`:

**Windows**:
```powershell
$env:PYTHONPATH="."
python -m pytest tests/test_agent.py
```

**Linux / macOS**:
```bash
export PYTHONPATH="."
python3 -m pytest tests/test_agent.py
```

---

## 📂 Directory Structure

```text
raju-shop/
├── app/
│   ├── __init__.py
│   ├── agent.py            # Raju's system instructions & check_inventory tool logic
│   └── fast_api_app.py     # ADK FastAPI web server & runner configuration
├── tests/
│   └── test_agent.py       # Pytest unit tests for tool and agent logic
├── index.html              # Indian bazaar themed web frontend
├── pyproject.toml          # Project configuration
├── requirements.txt        # Python dependency manifest
├── run_setup.ps1           # Windows automated setup & launch script
├── run_setup.sh            # Linux/macOS automated setup & launch script
└── README.md               # Project documentation
```

---

## 🛠️ API Reference

### 1. Initialize Session
- **Endpoint**: `POST /apps/app/users/{user_id}/sessions/{session_id}`
- **Response**:
  ```json
  {
    "userId": "user1",
    "sessionId": "session1",
    "status": "initialized"
  }
  ```

### 2. Run Agent Turn
- **Endpoint**: `POST /run`
- **Request Payload**:
  ```json
  {
    "appName": "app",
    "userId": "user1",
    "sessionId": "session1",
    "newMessage": {
      "role": "user",
      "parts": [{ "text": "Do you have any Taj Mahals in stock?" }]
    }
  }
  ```
- **Response Payload**:
  ```json
  {
    "appName": "app",
    "userId": "user1",
    "sessionId": "session1",
    "content": {
      "role": "model",
      "parts": [{ "text": "Arre my friend! The Taj Mahal is OUT OF STOCK..." }]
    }
  }
  ```

---

## 📚 References & Credits

- [Google Agent Development Kit (ADK) Documentation](https://google.github.io/adk-docs/)
- [Google Cloud Agent Starter Pack](https://github.com/GoogleCloudPlatform/agent-starter-pack)
- [Gemini API Documentation](https://ai.google.dev/docs)
