# retail_trend_agent
# Retail Trend AI - User Guide

This application generates daily fashion trend reports and cross-references them with your inventory using AI.

## 1. Google Cloud Setup (First Time Users)

To use the AI features (Gemini & Imagen), you need a specific Google Cloud Setup.

### Step 1: Create a Google Cloud Account
1.  Go to [Google Cloud Console](https://console.cloud.google.com/).
2.  Sign in with your Google Account.
3.  Click **"Get Started for Free"** (new accounts usually get $300 credit).
4.  Follow the prompts to verify your account (requires credit card for identity verification, but you won't be charged unless you upgrade).

### Step 2: Create a New Project
1.  In the top-left dropdown (next to "Google Cloud"), click **Select a project**.
2.  Click **New Project** (top right of the modal).
3.  **Project Name**: `retail-trend-ai` (or similar).
4.  Click **Create**.
5.  **Copy your Project ID** (it will look like `retail-trend-ai-123456`). You will need this later.

### Step 3: Enable APIs
You need to turn on the "brains" of the account.
1.  In the Dashboard search bar, type **"Vertex AI API"**.
2.  Select **Vertex AI API** from Marketplace results.
3.  Click **Enable**.
4.  Do the same for **"Cloud Resource Manager API"** (often needed for authentication).

### Step 4: Install Google Cloud SDK (CLI)
To let your local computer talk to Google Cloud:
1.  Download the **Google Cloud CLI** installer for Windows: [Download Link](https://cloud.google.com/sdk/docs/install#windows).
2.  Run the installer.
3.  When finished, a terminal window will open. If not, open PowerShell and type `gcloud init`.
4.  Follow the login prompt (it will open your browser).
5.  Select the **Project** you just created (`retail-trend-ai`).

### Step 5: Application Default Credentials (ADC)
This is the magic step that lets Python code work without managing keys manually.
1.  Open your command prompt / terminal.
2.  Run:
    ```bash
    gcloud auth application-default login
    ```
3.  A browser window will pop up. Login and click **Allow**.
4.  It will save a JSON key file to your computer automatically. The app will find this file.

Credentials saved to file: [C:\Users\rbhar\AppData\Roaming\gcloud\application_default_credentials.json]

These credentials will be used by any library that requests Application Default Credentials (ADC).
WARNING:
Cannot find a quota project to add to ADC. You might receive a "quota exceeded" or "API not enabled" error. Run $ gcloud auth application-default set-quota-project to add a quota project.
---

## 2. Project Configuration

### Step 1: Update Environment
Open the file `.env` in this directory.
Fill in your Project ID:
```env
PROJECT_ID=put-your-project-id-here (e.g., retail-trend-ai-123456)
LOCATION=us-central1
```

### Step 2: Install Python Libraries
Ensure you are in the `retail_trend_ai` folder in your terminal:
```bash
pip install -r requirements.txt
```

---

## 3. Running the Application

Execute the main script:
```bash
python src/main.py
```

### What to Expect
1.  **"Initializing..."**: The app starts up.
2.  **Inventory Check**:
    *   *First Run*: It will say "No data found. Generating synthetic inventory...". It creates 50 mock items.
    *   *Subsequent Runs*: It loads `data/inventory.json`.
3.  **Trend Analysis**:
    *   It searches the web for "January 2026 Men's Fashion Trends".
    *   It uses Gemini AI to compile a Top 20 list.
4.  **RAG / Inventory Matching**:
    *   It compares those trends against your mock inventory.
5.  **Report**:
    *   It prints a report recommending items to **BUY** (if high trend + low stock) or **PROMOTE** (if high trend + high stock).
    *   The report is saved to `trend_report.txt`.

---

## Troubleshooting

*   **"Quota exceeded"**: If you are on a brand new free tier, you might hit API limits. Wait a minute and try again.
*   **"Default Credentials not found"**: Re-run `gcloud auth application-default login`.
*   **"Imagen not found"**: Image generation requires approval in some regions. The app will skip image generation if this fails, but the rest will work.

