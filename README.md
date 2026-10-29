<div align="center">

<img src="https://raw.githubusercontent.com/NaniToka/NaniToka/main/banner.svg?v=3" alt="Toka Nani, Cloud and GenAI Engineer" width="100%" />

<a href="https://github.com/NaniToka">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=20&pause=1200&color=6C5CE7&center=true&vCenter=true&width=760&lines=Building+LLM+cost-optimization+tooling;Shipping+ML+fairness+auditors+on+Google+Cloud;Google+Gemini+Student+Ambassador+%7C+B.Tech+CSE+%2728;Open+to+SWE+%2F+Cloud+%2F+DevOps+internships" alt="Typing SVG" />
</a>

<br/>

[![Portfolio](https://img.shields.io/badge/Portfolio-Live-6c5ce7?style=for-the-badge&logo=googlechrome&logoColor=white)](https://toka-portfolio-2.onrender.com)
[![Resume](https://img.shields.io/badge/Resume-PDF-e17055?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)](https://toka-portfolio-2.onrender.com/nani.pdf)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/toka-nani-33a124359)
[![Email](https://img.shields.io/badge/Email-Hire_me-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:tokananiy@gmail.com)

<img src="https://komarev.com/ghpvc/?username=NaniToka&label=Profile+views&color=6c5ce7&style=flat-square" alt="Profile views" />

</div>

---

## 👋 About

I build **production-deployed AI products on Google Cloud**: not notebooks, live URLs. My focus areas are **LLM cost and latency optimization**, **responsible-AI and bias auditing**, and **multilingual civic-tech decision systems**.

| | |
|---|---|
| 🎓 | B.Tech CSE '28 · DVR & Dr. HS MIC College of Technology |
| 🌟 | Google Gemini Student Ambassador (2026) |
| 🧪 | Data Analyst Intern, Bluestock Fintech (Sep–Oct 2026) |
| 🎯 | Seeking **SWE · Cloud · DevOps internships** · remote or relocation · available immediately |
| 📍 | Vijayawada, India · IST (UTC+5:30) |

---

## 📊 At a glance

<div align="center">

| 🚀 **4** | 🏆 **13+** | ⚡ **~74%** | 🧪 **37** |
|:---:|:---:|:---:|:---:|
| Live deployed AI products | Hackathons | Prompt-token reduction (TokenFlow, own benchmark) | Passing tests (CivicPulse scoring engine) |

</div>

---

## 🚀 Featured projects

<table>
<tr>
<td width="50%" valign="top">

### 🔍 [BiasGuard AI](https://github.com/NaniToka/unbiased-ai-decision)
**Forensic bias auditor for hiring and credit-scoring decisions.**
Streams decision logs through demographic-parity and equalized-odds checks. Gemini 1.5 Flash generates compliance reports mapped to UN SDG-5 and SDG-10 in **under 30 s**. Built solo for Google Solution Challenge 2026.

`Vertex AI` `Gemini` `Flask` `Firestore` `Cloud Run` `Docker`

[**▶ Live demo**](https://biasguard-rzpoqg6s6a-uc.a.run.app) · [Code](https://github.com/NaniToka/unbiased-ai-decision)

</td>
<td width="50%" valign="top">

### ⚡ [TokenFlow AI](https://github.com/NaniToka/TokenFlow-AI)
**LLM middleware that cuts prompt cost.**
Gemini `text-embedding-004` vectors plus exponential recency-decay compression before each completion call, achieving **~74% less prompt-token overhead** (own benchmark).

`FastAPI` `Gemini 1.5 Flash` `React 18` `Render`

[**▶ Live demo**](https://tokenflow-ai.onrender.com) · [API docs](https://tokenflow-ai.onrender.com/docs) · [Code](https://github.com/NaniToka/TokenFlow-AI)

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🏛️ [CivicPulse AI](https://github.com/NaniToka/civicpulse-ai)
**Multilingual civic decision-intelligence layer.**
Gemini detects the language and categorizes citizen complaints. A deterministic 4-factor scoring engine (demand 35 · infra gap 25 · vulnerability 20 · investment overlap 20) ranks priorities. **37 pytest tests.**

`FastAPI` `React` `TypeScript` `Vite` `Gemini`

[**▶ Live demo**](https://civicpulse-ai-frontend.onrender.com/) · [Code](https://github.com/NaniToka/civicpulse-ai)

</td>
<td width="50%" valign="top">

### 🗳️ [VoteWise AI](https://votewise-ai-auoj3wixvq-uc.a.run.app)
**Nonpartisan voter-readiness assistant for first-time voters.**
Deterministic decision-tree engine plus Gemini-powered Q&A, containerized on Cloud Run. Built for PromptWars.

`React` `TypeScript` `Gemini` `Docker` `Cloud Run`

[**▶ Live demo**](https://votewise-ai-auoj3wixvq-uc.a.run.app)

</td>
</tr>
</table>

<details>
<summary><b>More projects</b></summary>

- 📈 **Mutual Fund Analytics Platform**: 9-table SQLite star schema (86,000+ rows), with CAGR / Sharpe / Sortino / Alpha-Beta / VaR / CVaR in a 4-page Streamlit dashboard *(Bluestock capstone)*
- 🏛️ **JanVoice AI**: role-based grievance portals for citizens, MPs and admins, with Gemini daily constituency briefings · [Live](https://spontaneous-raindrop-8a7198.netlify.app/dashboard)

</details>

---

## 🏗️ How BiasGuard works

```mermaid
flowchart LR
    A[Decision logs<br/>hiring / credit] --> B[Cloud Storage]
    B --> C[Cloud Run · Flask API]
    C --> D{Fairness evaluator<br/>Demographic parity<br/>Equalized odds}
    D --> E[Gemini 1.5 Flash<br/>report generation]
    E --> F[(Firestore<br/>audit trail)]
    E --> G[Compliance report<br/>SDG-5 · SDG-10]
    style D fill:#6c5ce7,color:#fff
    style E fill:#0984e3,color:#fff
