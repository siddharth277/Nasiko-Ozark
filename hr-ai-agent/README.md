# HR AI Agent — Nasiko A2A Deployment

An intelligent HR hiring platform agent that handles the full recruitment lifecycle via the A2A (Agent-to-Agent) protocol.

## 🚀 Skills

| # | Skill | Description |
|---|-------|-------------|
| 1 | **JD Generator** | Generate compelling Job Descriptions in 5 styles |
| 2 | **Resume Screener** | Evaluate resumes against JDs with structured scoring |
| 3 | **Interview Kit** | Generate 10 tailored interview questions |
| 4 | **Offer Letter** | Draft FAANG-grade professional offer letters |
| 5 | **Company Handbook** | Create comprehensive employee handbooks |
| 6 | **HR Helpdesk** | Answer HR policy questions (PTO, benefits, etc.) |
| 7 | **Email Drafter** | Draft interview invitation emails |

## 📦 Project Structure

```
hr-ai-agent/
├── src/
│   ├── __init__.py
│   ├── __main__.py      # A2A JSON-RPC server (port 5000)
│   ├── models.py        # Pydantic models for A2A protocol
│   ├── agent.py         # LangChain Agent with GPT-4o
│   └── tools.py         # 7 LangChain @tool functions
├── Dockerfile
├── docker-compose.yml
├── AgentCard.json
└── README.md
```

## 🛠️ Local Testing

### Prerequisites
- Docker Desktop installed
- OpenAI API Key

### Build & Run

```bash
cd hr-ai-agent
docker build -t hr-ai-agent .
docker run -p 5000:5000 -e OPENAI_API_KEY=your_key_here hr-ai-agent
```

### Test with curl

```bash
curl -X POST http://localhost:5000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "Generate a JD for Senior ML Engineer at a fintech startup"}]
      }
    }
  }'
```

## 🚢 Deployment on Nasiko

### Option 1: GitHub
1. Push this folder to a GitHub repo
2. Go to Nasiko Dashboard → Add Agent → Connect GitHub
3. Select your repo — it auto-deploys

### Option 2: ZIP Upload
1. ZIP this folder: `zip -r hr-ai-agent.zip hr-ai-agent/`
2. Go to Nasiko Dashboard → Add Agent → Upload ZIP
3. Upload and wait for deployment

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | Your OpenAI API key for GPT-4o |
