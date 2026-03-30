# Trace 🛡️
**Automated SOC2 & Security Compliance Engine for GitHub Pull Requests**

Trace is an AI-powered security co-pilot that lives inside your CI/CD pipeline. It automatically scans GitHub Pull Requests for OWASP top 10 vulnerabilities, hardcoded secrets, and SOC2 compliance violations, blocking dangerous code from ever reaching production. 

---

## 🚀 The Problem & Solution
Engineering teams spend thousands of hours manually reviewing code for security compliance to maintain their SOC2 status. Human error leads to leaked API keys, unencrypted PII, and massive security liabilities. 

Trace replaces manual security audits with an asynchronous AI engine. It intercepts `git diffs` via GitHub Webhooks, analyzes the context of the code using advanced LLMs, and posts actionable fix suggestions directly on the specific lines of code in the PR—all before a human reviewer even opens the tab.

---
 
## ✨ Core Features
* **Zero-Config GitHub Integration:** Installs at the organization level via GitHub Apps.
* **Asynchronous Webhook Processing:** Handles massive concurrent PRs without bottlenecking, utilizing FastAPI's non-blocking architecture.
* **Context-Aware AI Analysis:** Chunks complex code diffs and passes them through a strictly prompted LLM to identify security flaws with near-zero false positives.
* **Automated Enforcement:** Physically blocks the GitHub merge button until the flagged vulnerability is resolved.
* **CTO Analytics Dashboard:** A React-based command center to visualize caught vulnerabilities, configure compliance strictness, and export audit logs for SOC2 certification.

---

## 🛠️ Tech Stack & Architecture

**Frontend**
* React / TypeScript
* Tailwind CSS (Styling)
* Vercel (Hosting)

**Backend & AI Engine**
* Python 3.10+ / FastAPI
* AsyncIO & Pydantic (Data validation)
* OpenAI API / Claude 3.5 Sonnet (LLM Inference)
* GitHub Apps API (Authentication & PR interacting)

**Database**
* MongoDB Atlas
* PyMongo / Motor (Async MongoDB driver)

---

## 💻 Local Development Setup

Because Trace offloads heavy AI inference to cloud APIs, it is highly optimized and can run comfortably on standard local hardware (e.g., i5 processor, 8GB RAM). 

### Prerequisites
* Python 3.10+
* Node.js & npm
* MongoDB (Local or Atlas)
* Ngrok (For local webhook tunneling)

### 1. Clone & Backend Setup
```bash
git clone https://github.com/yourusername/trace-ai.git
cd trace-ai/backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 3. Environment Variables
Create a `.env` file in your `backend` directory:
```env
GITHUB_WEBHOOK_SECRET=your_generated_secret
GITHUB_APP_PRIVATE_KEY=your_downloaded_pem_file
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/trace
OPENAI_API_KEY=sk-your-openai-key
```

### 4. Webhook Tunneling (Local Testing)
To receive GitHub webhooks locally, expose your FastAPI port using Ngrok:
```bash
ngrok http 8000
```
*Copy the forwarding URL and paste it into your GitHub App's Webhook settings.*

---

## 🗺️ Roadmap
* [x] Core GitHub Webhook ingestion
* [x] AI diff analysis and prompt chaining
* [ ] Implement OAuth for CTO dashboard login
* [ ] Add support for custom, company-specific security rules
* [ ] Export automated PDF audit reports for SOC2 compliance

---

## 📄 License
This project is licensed under the MIT License.
