# 🛡️ AI Security RSS Feed to Notion

Keep track of real-time GenAI and LLM security risks — without constantly checking blogs and research sites.

This repo pulls from trusted sources (like arXiv, OpenAI, Anthropic, and others), applies optional keyword filters, and pushes new entries to a Notion database via the Notion API. Scheduled via GitHub Actions to run daily.

---

## 🔍 What It Tracks

- Jailbreaks and prompt injections
- Model theft and reverse engineering
- AI red team reports
- Supply chain risks in open-source LLMs
- Compliance news (AI RMF, GDPR, etc.)

---

## 📚 Sources Included

- [arXiv: LLM Security](https://arxiv.org/)
- [AI Snake Oil](https://aisnakeoil.substack.com/)
- [Anthropic News](https://www.anthropic.com/news)
- [OpenAI Blog](https://openai.com/blog)
- [Google DeepMind Blog](https://www.deepmind.com/blog)
- [NIST News](https://www.nist.gov/news-events/news)
- [Invariant Labs](https://invariant.ai/blog) *(manual scraping)*

Feeds and filters are configurable in `feeds/ai_security_feeds.json`.

---

## ✅ How to Deploy

1. **Fork this repo**
2. **Create a Notion integration + database**
3. **Add your `NOTION_TOKEN` and `NOTION_DATABASE_ID` as GitHub secrets**
4. **Enable GitHub Actions**

📝 Full setup instructions: [INSTALL.md](INSTALL.md)

---

## 🛠 Customization

- Tweak feeds and keywords in `feeds/ai_security_feeds.json`
- Adjust how many entries per source or add new filters
- Extend with support for Mattermost, Slack, email alerts, or other destinations

---

## 🙋‍♂️ Why This Exists

Security threats around LLMs evolve daily — and typical infosec feeds don’t track them well. This project helps AI builders, red teamers, and researchers stay ahead with minimal effort.

---

Built by [@mermoddity](https://github.com/mermoddity) — contributions welcome!
