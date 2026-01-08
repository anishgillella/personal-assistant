# Personal Assistant: LLM-Powered Question-Answering Chatbot

An intelligent, tool-enabled conversational chatbot built with advanced LLM capabilities, comprehensive evaluation metrics, and an interactive web dashboard for real-time interaction and performance analysis.

## Overview

This project implements a sophisticated question-answering agent that leverages:
- **LLM-powered conversation** with function calling capabilities
- **Multi-tool integration** for enhanced reasoning and information retrieval
- **Rigorous evaluation framework** with quality metrics
- **Interactive web dashboard** for live chatbot interaction and analytics

## Features

### 🤖 Core Chatbot Capabilities
- **Function Calling**: Multi-tool integration for expanded LLM capabilities
- **Contextual Reasoning**: Maintains conversation history for coherent interactions
- **General-Purpose QA**: Answers open-ended questions across diverse domains
- **Tool-Augmented Generation**: Integrates external data sources for accurate responses

### 📊 Evaluation Framework
- **Quality Metrics**: Comprehensive evaluation of chatbot responses
- **Dataset-Driven**: Systematic evaluation against a curated question-answer dataset
- **Metric Selection**: Carefully chosen metrics for meaningful performance assessment
- **Detailed Reporting**: Structured evaluation results and insights

### 🎨 Web Dashboard
- **Live Chat Interface**: Real-time interaction with the chatbot
- **Performance Analytics**: Visualize evaluation metrics and trends
- **Response Analysis**: Detailed breakdown of chatbot responses
- **Conversation History**: Track and review past interactions

## Project Structure

```
.
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── backend/
│   ├── app.py                        # Main Flask/FastAPI application
│   ├── chatbot/
│   │   ├── __init__.py
│   │   ├── agent.py                  # LLM-powered question-answering agent
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── search.py             # Web search or knowledge base tool
│   │   │   ├── calculator.py         # Math/calculation tool
│   │   │   └── ...                   # Additional tools
│   │   └── config.py                 # Agent configuration
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── evaluator.py              # Evaluation logic and metrics
│   │   ├── metrics.py                # Metric implementations
│   │   ├── dataset.py                # Dataset management
│   │   └── results.py                # Results storage and retrieval
│   └── api/
│       ├── __init__.py
│       ├── routes.py                 # API endpoints
│       └── models.py                 # Request/response models
├── frontend/
│   ├── index.html                    # Main dashboard HTML
│   ├── css/
│   │   └── style.css                 # Dashboard styling
│   ├── js/
│   │   ├── chat.js                   # Chat interface logic
│   │   ├── dashboard.js              # Analytics and dashboard logic
│   │   └── api.js                    # API communication
│   └── components/
│       ├── chat-interface.html       # Reusable chat component
│       └── metrics-panel.html        # Metrics display component
├── data/
│   ├── evaluation_dataset.json       # QA pairs for evaluation
│   └── results/                      # Evaluation results storage
└── .gitignore
```

## Getting Started

### Prerequisites
- **Python 3.9+** or **Node.js 16+**
- **LLM API Key** (OpenAI, Anthropic, or Fireworks.AI)
- **Optional**: Additional tool provider API keys (e.g., search API)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/anishgillella/personal-assistant.git
   cd personal-assistant
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Initialize data directory**
   ```bash
   mkdir -p data/results
   ```

### Running the Application

#### Development Mode

1. **Start the backend server**
   ```bash
   python backend/app.py
   ```
   The API will be available at `http://localhost:5000`

2. **Serve the frontend** (in another terminal)
   ```bash
   # Using Python's built-in server
   cd frontend
   python -m http.server 3000
   ```
   The dashboard will be available at `http://localhost:3000`

#### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment instructions.

## Usage

### Interacting with the Chatbot

**Via Web Dashboard:**
1. Open `http://localhost:3000` in your browser
2. Type your question in the chat interface
3. View the chatbot's response and tool usage

**Via API:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?"}'
```

### Running Evaluation

```bash
python -m backend.evaluation.evaluator \
  --dataset data/evaluation_dataset.json \
  --output data/results/evaluation_results.json
```

View results in the dashboard's **Evaluation** tab.

## Chatbot Tools

The chatbot is equipped with the following tools:

### 1. **Search Tool**
   - Performs web searches or knowledge base lookups
   - Returns relevant information for answering questions

### 2. **Calculator Tool**
   - Performs mathematical calculations
   - Supports complex expressions

### 3. **[Additional Tools]**
   - Extensible architecture for adding more tools

Tools are called automatically by the LLM when relevant to the user's query.

## Evaluation Metrics

The evaluation framework measures:

- **Relevance**: How well the response addresses the user's question
- **Accuracy**: Factual correctness of the response
- **Completeness**: Whether all aspects of the question are covered
- **Coherence**: Logical flow and readability
- **Tool Usage**: Appropriate and effective use of available tools

Metrics are computed against a curated evaluation dataset and visualized in the dashboard.

## Architecture

### Backend
- **Framework**: Flask/FastAPI for REST API
- **LLM Integration**: OpenAI, Anthropic, or Fireworks.AI SDKs
- **Async Support**: Async/await for non-blocking operations

### Frontend
- **Framework**: Vanilla JavaScript or Vue.js/React
- **Styling**: Modern CSS with responsive design
- **Real-time Updates**: WebSocket or polling for chat updates

### Data Flow
```
User Query → API Endpoint → LLM Agent → Tool Selection → Tool Execution → Response → Dashboard
```

## Configuration

### LLM Configuration
Edit `backend/chatbot/config.py` to:
- Choose your LLM provider (OpenAI, Anthropic, Fireworks.AI)
- Set model parameters (temperature, max_tokens, etc.)
- Configure system prompts

### Tool Configuration
Register new tools in `backend/chatbot/tools/__init__.py`:
```python
AVAILABLE_TOOLS = {
    "search": SearchTool(),
    "calculator": CalculatorTool(),
    # Add new tools here
}
```

## API Endpoints

### Chat
- **POST** `/api/chat` - Send a message to the chatbot
  - Request: `{ "query": "string", "conversation_id": "string?" }`
  - Response: `{ "response": "string", "tools_used": [], "confidence": number }`

### Evaluation
- **GET** `/api/evaluation/results` - Get latest evaluation results
- **POST** `/api/evaluation/run` - Run evaluation (async)
- **GET** `/api/evaluation/status` - Check evaluation status

### History
- **GET** `/api/conversations` - List conversations
- **GET** `/api/conversations/{id}` - Get conversation details

## Development

### Adding a New Tool

1. Create `backend/chatbot/tools/my_tool.py`:
   ```python
   class MyTool:
       name = "my_tool"
       description = "Description of what this tool does"
       
       def execute(self, **kwargs):
           # Implementation
           pass
   ```

2. Register in `backend/chatbot/tools/__init__.py`

3. The LLM will automatically discover and use it

### Running Tests
```bash
pytest tests/ -v
```

### Code Style
```bash
# Format code
black backend/ frontend/

# Lint
pylint backend/
```

## Troubleshooting

### Common Issues

**"API key not found"**
- Ensure your API key is set in `.env`
- Check that the environment variable is loaded: `echo $OPENAI_API_KEY`

**"Tool execution failed"**
- Check tool dependencies are installed
- Review logs in `logs/` directory

**"Dashboard not loading"**
- Verify backend is running on `http://localhost:5000`
- Check browser console for CORS errors

## Performance Considerations

- **Caching**: Responses are cached to reduce API calls
- **Streaming**: Long responses are streamed to improve perceived performance
- **Evaluation**: Run evaluations during off-peak hours

## Limitations & Future Work

- [ ] Multi-language support
- [ ] Custom model fine-tuning
- [ ] Advanced memory/context management
- [ ] Integration with more external data sources
- [ ] Real-time collaboration features
- [ ] Mobile app

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - See LICENSE file for details

## Contact & Support

For questions or issues:
- Open a GitHub issue
- Contact: [your-email@example.com]

---

**Happy chatting!** 🚀

