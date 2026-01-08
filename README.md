# QA Assistant: LLM-Powered Question-Answering Chatbot

An intelligent, tool-enabled conversational chatbot built with Gemini 2.5 Flash, featuring comprehensive evaluation metrics and an interactive web dashboard.

## Overview

This project implements a question-answering agent that leverages:
- **LLM-powered conversation** with function calling capabilities via OpenRouter
- **Multi-tool integration** (web search + calculator) for enhanced reasoning
- **Rigorous evaluation framework** with LLM-as-judge metrics
- **Interactive web dashboard** for live chatbot interaction and analytics

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python, FastAPI |
| **LLM** | Gemini 2.5 Flash via OpenRouter |
| **Tools** | SerpAPI (web search), Calculator |
| **Frontend** | Next.js 14, React, Tailwind CSS |
| **Charts** | Recharts |

## Features

### Core Chatbot
- **Function Calling**: Automatic tool selection and execution
- **Conversation Context**: Maintains chat history for coherent multi-turn dialogues
- **Two Integrated Tools**:
  - **Search**: Web search via SerpAPI for current information
  - **Calculator**: Safe mathematical expression evaluation

### Evaluation Framework
- **LLM-as-Judge**: Uses the same LLM to evaluate responses
- **5 Metrics**: Relevance, Accuracy, Completeness, Coherence, Tool Usage
- **25-question Dataset**: Covers math calculations and factual queries
- **Detailed Reporting**: Per-question breakdown with explanations

### Web Dashboard
- **Chat Interface**: Real-time conversation with tool visibility
- **Evaluation Dashboard**: Run evaluations and view results
- **Visualizations**: Bar charts and radar charts for metrics
- **Responsive Design**: Works on desktop and mobile

## Project Structure

```
.
├── backend/
│   ├── app.py                    # FastAPI application
│   ├── requirements.txt          # Python dependencies
│   ├── chatbot/
│   │   ├── agent.py              # LLM agent with tool calling
│   │   ├── config.py             # Configuration settings
│   │   └── tools/
│   │       ├── search.py         # SerpAPI web search
│   │       └── calculator.py     # Math calculator
│   ├── evaluation/
│   │   ├── evaluator.py          # Evaluation runner
│   │   ├── metrics.py            # LLM-as-judge metrics
│   │   └── dataset.py            # Dataset loader
│   └── api/
│       ├── routes.py             # API endpoints
│       └── models.py             # Pydantic models
├── frontend/
│   ├── src/
│   │   ├── app/                  # Next.js pages
│   │   ├── components/           # React components
│   │   └── lib/                  # API client & types
│   └── package.json
├── data/
│   ├── evaluation_dataset.json   # 25 QA pairs
│   └── results/                  # Evaluation results
├── .env.example                  # Environment template
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenRouter API key ([get one here](https://openrouter.ai/keys))
- SerpAPI key ([get one here](https://serpapi.com/manage-api-key))

### Installation

1. **Clone and navigate to the project**
   ```bash
   cd houston
   ```

2. **Set up Python backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cd ..
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Set up frontend**
   ```bash
   cd frontend
   npm install
   cp .env.local.example .env.local
   ```

### Running the Application

1. **Start the backend** (from project root)
   ```bash
   cd backend
   source venv/bin/activate
   python app.py
   ```
   Backend runs at `http://localhost:8000`

2. **Start the frontend** (in another terminal)
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend runs at `http://localhost:3000`

3. **Open the dashboard**
   Navigate to `http://localhost:3000` in your browser

## Usage

### Chat Interface
1. Type a question in the chat input
2. Press Enter or click Send
3. View the response and any tools used
4. Click "X tools used" to see tool details

### Running Evaluation
1. Navigate to the Evaluation tab
2. Click "Run Evaluation"
3. Wait for completion (evaluates 25 questions)
4. View metrics, charts, and detailed results

### Example Questions
- "What is 15% of 250?" (uses calculator)
- "Who is the CEO of OpenAI?" (uses search)
- "Calculate sqrt(144) + 2^5" (uses calculator)
- "What is the capital of Australia?" (uses search)

## API Endpoints

### Chat
- `POST /api/chat` - Send a message
  ```json
  { "query": "What is 2 + 2?", "conversation_id": "optional-uuid" }
  ```

### Evaluation
- `POST /api/evaluation/run` - Start evaluation
- `GET /api/evaluation/status` - Check progress
- `GET /api/evaluation/results` - Get results

### Conversations
- `GET /api/conversations` - List all
- `GET /api/conversations/{id}` - Get one
- `DELETE /api/conversations/{id}` - Delete one

## Evaluation Metrics

| Metric | Weight | Description |
|--------|--------|-------------|
| Accuracy | 30% | Factual correctness compared to expected answer |
| Relevance | 25% | How well the response addresses the question |
| Completeness | 20% | Coverage of all aspects of the question |
| Tool Usage | 15% | Appropriate use of available tools |
| Coherence | 10% | Clarity and logical structure |

## Configuration

### Backend (`backend/chatbot/config.py`)
- `MODEL_NAME`: LLM model (default: `google/gemini-2.5-flash-preview`)
- `MAX_TOKENS`: Maximum response tokens (default: 4096)
- `TEMPERATURE`: Response randomness (default: 0.7)

### Frontend (`frontend/.env.local`)
- `NEXT_PUBLIC_API_URL`: Backend API URL

## Development

### Adding a New Tool

1. Create `backend/chatbot/tools/my_tool.py`:
   ```python
   class MyTool:
       name = "my_tool"
       description = "What this tool does"

       def get_schema(self):
           return {
               "type": "function",
               "function": {
                   "name": self.name,
                   "description": self.description,
                   "parameters": { ... }
               }
           }

       def execute(self, **kwargs):
           # Implementation
           return {"success": True, "result": ...}
   ```

2. Register in `backend/chatbot/tools/__init__.py`

### Running Evaluation CLI
```bash
cd backend
python -m evaluation.evaluator --dataset ../data/evaluation_dataset.json
```

## Troubleshooting

**"API key not found"**
- Ensure `.env` file exists in project root with valid keys

**"CORS error in browser"**
- Verify backend is running on port 8000
- Check frontend `.env.local` has correct API URL

**"Tool execution failed"**
- Check SerpAPI key is valid and has quota
- Review backend logs for details

## License

MIT License
