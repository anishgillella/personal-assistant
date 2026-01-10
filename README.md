# QA Assistant: LLM-Powered Question-Answering Chatbot

An intelligent, multi-tool conversational chatbot built with Gemini 2.5 Flash, featuring comprehensive evaluation metrics, token usage tracking, and an interactive web dashboard.

## Overview

This project implements a question-answering agent that leverages:
- **LLM-powered conversation** with function calling capabilities via OpenRouter
- **7 integrated tools** for enhanced reasoning and real-world data access
- **Rigorous evaluation framework** with LLM-as-judge metrics
- **Interactive web dashboard** for live chatbot interaction and analytics
- **Token usage tracking** with per-request and cumulative statistics

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.9+, FastAPI, Uvicorn |
| **LLM** | Gemini 2.5 Flash via OpenRouter |
| **Frontend** | Next.js 14, React 19, TypeScript |
| **Styling** | Tailwind CSS |
| **Charts** | Recharts |

## Features

### Core Chatbot (7 Tools)

| Tool | Description | Example Use Case |
|------|-------------|------------------|
| **calculator** | Safe mathematical expression evaluation | "What is 15% of 250?" |
| **search** | Web search via SerpAPI | "Who is the CEO of OpenAI?" |
| **wikipedia** | Authoritative encyclopedic information | "Who was Albert Einstein?" |
| **weather** | Current weather via OpenWeatherMap | "What's the weather in Tokyo?" |
| **code_executor** | Safe Python code execution | "Calculate factorial of 10 using Python" |
| **unit_converter** | Convert between units (length, weight, temp, etc.) | "Convert 100 miles to km" |
| **datetime** | Date/time calculations | "How many days until Christmas?" |

### Evaluation Framework
- **LLM-as-Judge**: Uses the same LLM to evaluate responses
- **5 Weighted Metrics**: Relevance (25%), Accuracy (30%), Completeness (20%), Coherence (10%), Tool Usage (15%)
- **30-question Dataset**: Covers math, factual, Wikipedia, conversions, datetime, and code
- **Parallel Processing**: Runs evaluations in batches of 10 for speed

### Web Dashboard
- **Chat Interface**: Real-time conversation with tool visibility
- **Token Usage Display**: Track tokens per message and cumulative usage
- **Evaluation Dashboard**: Run evaluations and view detailed results
- **Visualizations**: Bar charts and radar charts for metrics
- **Responsive Design**: Works on desktop and mobile

## Project Structure

```
.
├── backend/
│   ├── app.py                    # FastAPI application (hot reload enabled)
│   ├── requirements.txt          # Python dependencies
│   ├── chatbot/
│   │   ├── agent.py              # LLM agent with tool calling & token tracking
│   │   ├── config.py             # Configuration & system prompt
│   │   └── tools/
│   │       ├── calculator.py     # Math calculator
│   │       ├── search.py         # SerpAPI web search
│   │       ├── wikipedia.py      # Wikipedia API
│   │       ├── weather.py        # OpenWeatherMap API
│   │       ├── code_executor.py  # Safe Python sandbox
│   │       ├── unit_converter.py # Unit conversions
│   │       └── datetime_tool.py  # Date/time operations
│   ├── evaluation/
│   │   ├── evaluator.py          # Parallel batch evaluation
│   │   ├── metrics.py            # LLM-as-judge metrics
│   │   └── dataset.py            # Dataset loader
│   └── api/
│       ├── routes.py             # API endpoints
│       └── models.py             # Pydantic models
├── frontend/
│   ├── src/
│   │   ├── app/                  # Next.js pages
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx # Chat with token display
│   │   │   ├── EvaluationDashboard.tsx
│   │   │   └── Sidebar.tsx
│   │   └── lib/
│   │       ├── api.ts            # API client
│   │       └── types.ts          # TypeScript types
│   └── package.json
├── data/
│   ├── evaluation_dataset.json   # 30 QA pairs
│   └── results/                  # Evaluation results
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- API Keys:
  - OpenRouter API key ([get one here](https://openrouter.ai/keys))
  - SerpAPI key ([get one here](https://serpapi.com/manage-api-key))
  - OpenWeatherMap API key ([get one here](https://openweathermap.org/api)) - optional, for weather tool

### Installation

1. **Clone and navigate to the project**
   ```bash
   cd houston-v1
   ```

2. **Set up Python backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENROUTER_API_KEY=your_openrouter_key
   SERPAPI_API_KEY=your_serpapi_key
   OPENWEATHERMAP_API_KEY=your_openweathermap_key  # optional
   ```

4. **Set up frontend**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start the backend** (from `backend/` directory)
   ```bash
   source venv/bin/activate
   python app.py
   ```
   Backend runs at `http://localhost:8000` with hot reload enabled

2. **Start the frontend** (in another terminal, from `frontend/` directory)
   ```bash
   npm run dev
   ```
   Frontend runs at `http://localhost:3000`

3. **Open the dashboard**
   Navigate to `http://localhost:3000` in your browser

## Usage

### Chat Interface
1. Type a question in the chat input
2. Press Enter or click Send
3. View the response and token usage
4. Click "X tools used" to see tool details
5. Token counter in header shows cumulative usage

### Running Evaluation
1. Navigate to the Evaluation tab
2. Click "Run Evaluation"
3. Wait for completion (30 questions, runs in parallel batches)
4. View metrics, charts, and detailed per-question results
5. Click "Refresh" to reload latest results

### Example Questions by Tool

| Tool | Example Question |
|------|------------------|
| Calculator | "What is 25% of 80 plus 15% of 120?" |
| Search | "What is the current population of Japan?" |
| Wikipedia | "Tell me about the Great Wall of China" |
| Weather | "What's the weather in New York?" |
| Code Executor | "Write Python code to find prime numbers from 1 to 20" |
| Unit Converter | "Convert 100 km/h to meters per second" |
| DateTime | "What day of the week was January 1, 2000?" |

## API Endpoints

### Chat
- `POST /api/chat` - Send a message
  ```json
  { "query": "What is 2 + 2?", "conversation_id": "optional-uuid" }
  ```
  Response includes `usage` with token counts

### Token Usage
- `GET /api/usage` - Get cumulative token statistics
- `POST /api/usage/reset` - Reset token counters

### Evaluation
- `POST /api/evaluation/run` - Start evaluation (runs in background)
- `GET /api/evaluation/status` - Check progress
- `GET /api/evaluation/results` - Get latest results

### Conversations
- `GET /api/conversations` - List all
- `GET /api/conversations/{id}` - Get one
- `DELETE /api/conversations/{id}` - Delete one

### Health
- `GET /api/health` - Health check

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
- `MODEL_NAME`: LLM model (default: `google/gemini-2.5-flash`)
- `MAX_TOKENS`: Maximum response tokens (default: 4096)
- `TEMPERATURE`: Response randomness (default: 0.7)

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key for LLM access |
| `SERPAPI_API_KEY` | Yes | SerpAPI key for web search |
| `OPENWEATHERMAP_API_KEY` | No | OpenWeatherMap key for weather tool |

## Development

### Hot Reload
The backend automatically reloads when you save changes to Python files.

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
                   "parameters": {
                       "type": "object",
                       "properties": { ... },
                       "required": [...]
                   }
               }
           }

       def execute(self, **kwargs):
           return {"success": True, "result": ...}
   ```

2. Register in `backend/chatbot/tools/__init__.py`:
   ```python
   from chatbot.tools.my_tool import MyTool
   AVAILABLE_TOOLS["my_tool"] = MyTool()
   ```

3. Update system prompt in `config.py` to describe the new tool

### Running Evaluation from CLI
```bash
cd backend
python -m evaluation.evaluator --dataset ../data/evaluation_dataset.json
```

## Troubleshooting

**"API key not found"**
- Ensure `.env` file exists in project root with valid keys
- Restart the backend after adding keys

**"CORS error in browser"**
- Verify backend is running on port 8000
- Check that frontend is accessing `http://localhost:8000`

**"Wikipedia 403 error"**
- This was fixed by adding proper User-Agent headers
- If persists, restart the backend

**"Tool execution failed"**
- Check API keys are valid and have quota
- Review backend logs for detailed errors

## License

MIT License
