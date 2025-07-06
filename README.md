# Multi-Agent AI System

A comprehensive multi-agent AI system with a web frontend, FastAPI backend, and intelligent agent routing.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   python start_server.py
   ```

3. **Access the application:**
   - Frontend: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🔧 Issues Fixed

### 1. **Port Mismatch**
- **Problem**: Frontend used port 8000, main.py used port 5000
- **Fix**: Updated `main.py` to use port 8000 consistently

### 2. **Frontend Error Handling**
- **Problem**: Error handling was commented out, no proper error display
- **Fix**: Implemented comprehensive error handling with user-friendly messages

### 3. **Agent Selection**
- **Problem**: Frontend had agent dropdown but no functionality
- **Fix**: Added agent selection with dynamic loading from health endpoint

### 4. **Response Format Inconsistencies**
- **Problem**: Different response formats between endpoints
- **Fix**: Standardized response handling in frontend

### 5. **Context Manager Issues**
- **Problem**: Conflicting method signatures and missing methods
- **Fix**: Unified method signatures with proper type annotations

### 6. **Agent Tool Endpoints**
- **Problem**: Mock implementation instead of real agent execution
- **Fix**: Proper agent execution with error handling

### 7. **Missing MCP Integration**
- **Problem**: MCP servers configured but not integrated
- **Fix**: Added MCP server integration to EnhancedPipeline

## 🏗️ Architecture

### Frontend (`frontend/`)
- **app.js**: Main frontend logic with agent selection and error handling
- **index.html**: Chat interface with agent dropdown
- **styles.css**: Responsive styling

### Backend (`app.py`)
- **FastAPI server** with multiple endpoints
- **Static file serving** for frontend
- **Agent execution** via `/tools/{agent}/run`
- **Enhanced pipeline** via `/ask` endpoint
- **Health monitoring** via `/health` endpoint

### Core Components
- **main.py**: CLI interface and agent routing logic
- **enhanced_pipeline.py**: Advanced pipeline with context management
- **context_manager.py**: Conversation context storage
- **agent_router.py**: Agent execution and error handling
- **tool_registry.py**: Agent registry management

### Agents (`agents/`)
- **healthcare_agent.py**: Medical advice and health information
- **fitness_agent.py**: Exercise and fitness guidance
- **education_agent.py**: Educational content and tutoring
- **finance_agent.py**: Financial advice and planning
- **law_agent.py**: Legal information and guidance
- **travel_agent.py**: Travel planning and recommendations

## 📡 API Endpoints

### Core Endpoints
- `GET /` - Redirects to frontend
- `GET /health` - System health check
- `POST /main_query` - Main query processing
- `POST /ask` - Enhanced pipeline with context

### Agent Endpoints
- `POST /tools/{agent}/run` - Execute agent commands
- `GET /context/{topic}` - Get conversation context

### MCP Endpoints
- `POST /mcp/add-server` - Add MCP server
- `GET /mcp/servers` - List MCP servers

## 🎯 Usage

### Web Interface
1. Open http://localhost:8000
2. Select an agent from the dropdown (or leave as "Auto-select")
3. Type your message and press Enter
4. View the agent's response

### API Usage
```bash
# Health check
curl http://localhost:8000/health

# Send a query
curl -X POST http://localhost:8000/main_query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are some healthy breakfast options?"}'

# Use enhanced pipeline
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Plan a workout routine", "topic": "fitness_agent"}'
```

### CLI Usage
```bash
python main.py
# Then type your queries interactively
```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 8000
   netstat -ano | findstr :8000
   # Kill the process or use a different port
   ```

2. **Database errors**
   ```bash
   # Delete and recreate database
   rm context.db
   python start_server.py
   ```

3. **Agent import errors**
   ```bash
   # Check agent files exist
   ls agents/*_agent.py
   # Ensure all dependencies are installed
   pip install -r requirements.txt
   ```

4. **Frontend not loading**
   - Check browser console for errors
   - Ensure FastAPI server is running
   - Verify static files are mounted correctly

### Health Check
Visit http://localhost:8000/health to see the status of all components:
- Ollama connection
- Database status
- Agent availability
- MCP server status

## 🛠️ Development

### Adding New Agents
1. Create `agents/your_agent.py`
2. Implement required functions
3. Create `agents/your_agent.json` configuration
4. Update tool registry

### Modifying Frontend
- Edit `frontend/app.js` for logic changes
- Edit `frontend/styles.css` for styling
- Edit `frontend/index.html` for structure

### API Extensions
- Add new endpoints in `app.py`
- Update request/response models
- Add proper error handling

## 📝 License

This project is open source and available under the MIT License. 