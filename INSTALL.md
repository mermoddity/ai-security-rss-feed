# 🚀 How to Deploy Your Own AI Security Feed to Notion

This tool fetches curated AI security news (from sources like arXiv, OpenAI, Anthropic, etc.) and pushes them daily to a Notion table — so you can track risks like jailbreaks, prompt injections, and supply chain exploits in one place.

---

## 📦 Prerequisites
- A **GitHub account**
- A **Notion account**
- A basic understanding of GitHub Actions and environment variables

---

## ✅ Step-by-Step Setup

### 1. Fork the Repository
Go to [https://github.com/mermoddity/ai-security-rss-feed](https://github.com/mermoddity/ai-security-rss-feed) and click **"Fork"**.

---

### 2. Set Up Your Notion Database
1. In Notion, create a **full-page database** (Table view).
2. Add the following columns:
   - `Title` (Title)
   - `URL` (URL)
   - `Source` (Text)
   - `Published Date` (Date)
3. Click **“Share”** → **“Invite”** your integration (see next step)

---

### 3. Create a Notion Integration Token
1. Go to: [https://www.notion.com/my-integrations](https://www.notion.com/my-integrations)
2. Click **“+ New integration”**
   - Name: `AI Security Feed`
   - Permissions: **Read and write**
   - Copy your **Internal Integration Token**
3. Go back to your database in Notion:
   - Click **“Share”** → Invite your integration
   - Grant **“Can edit”** access

---

### 4. Add Your Secrets to GitHub
In your forked repo:
- Go to **Settings → Secrets and variables → Actions → New repository secret**

Create these two secrets:

| Secret Name            | Value                                |
|------------------------|--------------------------------------|
| `NOTION_TOKEN`         | Paste your Notion integration token  |
| `NOTION_DATABASE_ID`   | Paste your Notion database ID        |

**To find your Notion Database ID:**
1. Open your database as a full page
2. Copy the URL, e.g.  
   ```
   https://www.notion.so/yourworkspace/Feed-123abcde456f7890abcd1234567890ef
   ```
3. Take the last part (32 characters, no dashes):  
   ```
   123abcde456f7890abcd1234567890ef
   ```

---

### 5. Enable GitHub Actions
- Go to the **Actions** tab in your forked repo
- Enable GitHub Actions if prompted

To trigger manually:
- Go to the workflow named **"AI Security Feed to Notion"**
- Click **“Run workflow”**

The job also runs **daily at 08:00 UTC** via GitHub’s scheduler.

---

## 🔄 Optional: Customize Feeds
Edit the file:  
```feeds/ai_security_feeds.json```  
You can:
- Add/remove sources
- Add keyword filters per feed (e.g., "jailbreak", "alignment")

---

## ✅ Done!
Your Notion table will now automatically update each day with the latest AI/LLM security insights.

Questions? Open an issue or ping @mermoddity.
