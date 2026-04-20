That key management setup is spot on. Using the `.pem` file content in your `.env` to sign a JWT locally is exactly how enterprise GitHub Apps securely authenticate. 

Here is the comprehensive breakdown of the pending features for Trace AI. I have structured this logically from the core data pipeline out to the user-facing features, explaining the "what" and the "why" in plain English.

### Feature 1: Dynamic Authentication & Diff Extraction
**What we are achieving:** Giving Trace AI the ability to actually "read" the code inside the Pull Request.
**Why we are doing it:** Right now, your webhook only tells you *that* a PR was opened and by whom. It doesn't include the code. We need to securely ask GitHub for the raw text of the code changes so we can hand it to the AI.

**Pending Sub-features:**
* **JWT Generation:** A utility function in `app/utils/github_auth.py` that uses your `.pem` key to generate a short-lived cryptographic token (JWT).
* **Installation Token Exchange:** An API call to GitHub that trades your JWT for a temporary "Installation Token" specific to the repository the webhook came from.
* **Raw Diff Fetching:** Using that Installation Token to call the GitHub PR API with a special header (`Accept: application/vnd.github.v3.diff`) to download the raw code changes (the `.diff` file).

---

### Feature 2: Diff Pre-processing & The AI Engine
**What we are achieving:** Slicing the code into digestible pieces and having the LLM actively hunt for security flaws.
**Why we are doing it:** If a developer submits a massive PR (like updating a `package-lock.json` alongside 50 other files), passing all that text to Claude/OpenAI will crash the app, cost a fortune, or confuse the AI. We must filter out the noise and feed the AI small, focused chunks of code.

**Pending Sub-features:**
* **Noise Filtering Logic:** A Python utility to strip out deleted lines, markdown files, and auto-generated lockfiles from the raw diff.
* **Intelligent Chunking:** Splitting the remaining diff into logical blocks (e.g., function by function) while keeping the file names and line numbers intact.
* **Async Prompt Chaining:** A service in `app/services/ai_service.py` that asynchronously sends these chunks to your LLM using strict system prompts (e.g., "You are a SOC2 auditor. Output ONLY JSON if a vulnerability is found in this chunk").

---

### Feature 3: Inline GitHub PR Commenting (The Co-Pilot)
**What we are achieving:** Posting the AI's security warnings directly onto the exact line of bad code inside the GitHub PR.
**Why we are doing it:** Developers hate context switching. If they have to log into a separate dashboard to see what they did wrong, they will ignore it. By putting the fix right where they are looking, you make the security process frictionless.

**Pending Sub-features:**
* **Line-Number Mapping:** Taking the AI's JSON output and translating it back to the exact line number in the GitHub diff format.
* **GitHub Review API Integration:** Formatting a payload to create a "Pull Request Review" comment via the GitHub API, acting as the Trace AI bot.

---

### Feature 4: Automated Enforcement (The Merge Blocker)
**What we are achieving:** Physically stopping developers from clicking the green "Merge" button if Trace AI finds a vulnerability.
**Why we are doing it:** A core requirement of SOC2 compliance is *provable enforcement*. A warning comment isn't enough; you have to prove to auditors that bad code *cannot* reach production.

**Pending Sub-features:**
* **Commit Status API Integration:** When the webhook hits, immediately post a `pending` status to the PR.
* **Resolution Logic:** If the AI finds zero issues, update the status to `success` (unlocking the merge button). If issues are found, update to `failure` (blocking the merge button).

---

### Feature 5: The CTO Command Center API
**What we are achieving:** Building the backend REST endpoints that will power your React frontend dashboard.
**Why we are doing it:** While developers live in GitHub, Engineering Managers and CTOs need a bird's-eye view of the team's security health to know if their engineers are repeatedly making the same mistakes.

**Pending Sub-features:**
* **GitHub OAuth Login:** Endpoints to let managers log into the React dashboard using their GitHub accounts, ensuring they only see data for their own repositories.
* **Analytics Aggregation:** Complex MongoDB aggregation pipelines to calculate metrics like "Most Common Vulnerabilities" or "Total Blocked PRs this Month."
* **REST API Endpoints:** standard `GET` routes in `app/api/routes/analytics.py` for the React app to consume.

---

### Feature 6: Custom Rules & SOC2 Audit Reporting
**What we are achieving:** Letting companies enforce their own specific rules and export proof of compliance.
**Why we are doing it:** Every company has different security stacks (e.g., "Never use MD5, only use our internal crypto library"). Furthermore, SOC2 auditors require hard evidence (usually PDFs) that your automated checks were actually running for the past 6 months.

**Pending Sub-features:**
* **Dynamic Prompt Injection:** Modifying the backend so users can save custom text rules in MongoDB, which are then seamlessly injected into the AI's base prompt during Feature 2.
* **PDF Audit Generation:** A utility using a library like ReportLab to generate an immutable, timestamped PDF listing every caught vulnerability and blocked PR over a requested date range.

---