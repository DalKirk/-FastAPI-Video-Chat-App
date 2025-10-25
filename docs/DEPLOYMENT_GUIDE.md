# Complete AI Chat System - Deployment Guide

## ?? Quick Start

### Backend Setup (5 minutes)

1. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

2. **Set Environment Variables**
Create a `.env` file in the root directory:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

3. **Update main.py**
Add the chat router to your FastAPI app:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.chat import router as chat_router

app = FastAPI(
    title="FastAPI Video Chat with AI",
    version="2.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the AI chat router
app.include_router(chat_router)

# Your existing routes...
```

4. **Run the Backend**
```bash
uvicorn main:app --reload --port 8000
```

5. **Verify Backend**
```bash
# Health check
curl http://localhost:8000/api/v1/chat/health

# Expected response:
# {
#   "status": "healthy",
#   "claude_enabled": true,
#   "services": {
#     "context_analyzer": "ready",
#     "format_selector": "ready",
#     "response_formatter": "ready"
#   }
# }
```

### Frontend Setup (5 minutes)

1. **Install Node Modules**
```bash
cd frontend
npm install
```

2. **Configure API URL**
Create `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:8000
```

3. **Create App.jsx**
```jsx
import React from 'react';
import ChatInterface from './components/Chat/ChatInterface';
import './styles/chat.css';

function App() {
  return (
    <div className="App">
      <ChatInterface />
    </div>
  );
}

export default App;
```

4. **Run the Frontend**
```bash
npm run dev
```

5. **Open Browser**
Navigate to: `http://localhost:3000`

## ?? File Checklist

### Backend Files ?
- [x] `app/models/chat_models.py` - Data models
- [x] `services/context_analyzer.py` - Context detection
- [x] `services/format_selector.py` - Format selection
- [x] `services/response_formatter.py` - Markdown formatting
- [x] `services/ai_service.py` - Main orchestrator
- [x] `api/routes/chat.py` - API endpoints
- [x] `utils/claude_client.py` - Claude AI integration
- [x] `utils/streaming_ai_endpoints.py` - Streaming support

### Frontend Files ?
- [x] `frontend/src/components/Chat/ChatInterface.jsx`
- [x] `frontend/src/components/Chat/MessageDisplay.jsx`
- [x] `frontend/src/components/Chat/CodeBlock.jsx`
- [x] `frontend/src/components/Markdown/MarkdownRenderer.jsx`
- [x] `frontend/src/services/api.js`
- [x] `frontend/src/utils/markdown-config.js`
- [x] `frontend/src/styles/chat.css`
- [x] `frontend/package.json`

### Documentation ?
- [x] `docs/AI_CHAT_INTEGRATION.md`
- [x] `docs/FRONTEND_INTEGRATION.md`

## ?? Testing

### Test Backend Endpoints

```bash
# 1. Health check
curl http://localhost:8000/api/v1/chat/health

# 2. Send a chat message
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I use FastAPI?",
    "conversation_history": []
  }'

# 3. Test streaming endpoint
curl http://localhost:8000/ai/stream/health
```

### Test Frontend

1. **Open Developer Console** (F12)
2. **Send a message** in the chat
3. **Check Network tab** - Should see:
   - POST to `/api/v1/chat`
   - 200 OK response
   - Response with `content`, `format_type`, `metadata`

4. **Test different message types**:
   - Casual: "Hey, what's up?"
   - Technical: "How do I create a FastAPI endpoint?"
   - Code request: "Show me a Python function example"
   - Structured: "What are the steps to deploy?"

## ?? Customization

### Adjust AI Behavior

Edit `services/context_analyzer.py`:
```python
def _is_technical_query(self, text: str) -> bool:
    technical_keywords = [
        'python', 'javascript', 'fastapi',
        # Add your domain-specific terms here
        'react', 'docker', 'kubernetes',
    ]
    # ...
```

### Change Format Rules

Edit `services/format_selector.py`:
```python
FormatType.CONVERSATIONAL: {
    'use_headers': False,
    'use_lists': 'minimal',
    'use_bold': 'minimal',
    'paragraph_style': 'short',  # Adjust this
    'greeting': True,
    'sign_off': True,
}
```

### Customize Styling

Edit `frontend/src/styles/chat.css`:
```css
:root {
  --primary-color: #2196F3;      /* Change primary color */
  --user-message-bg: #2196F3;    /* User message bubble */
  --ai-message-bg: white;        /* AI message bubble */
}
```

## ?? Production Deployment

### Backend (Railway/Render/AWS)

1. **Update CORS origins**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",
        "http://localhost:3000"  # Keep for local dev
    ],
    # ...
)
```

2. **Set production environment variables**:
```env
ANTHROPIC_API_KEY=your_production_key
ENVIRONMENT=production
```

3. **Deploy**:
```bash
# For Railway
railway up

# For Render
git push render main

# For AWS/Docker
docker build -t fastapi-chat .
docker run -p 8000:8000 fastapi-chat
```

### Frontend (Vercel/Netlify)

1. **Update API URL**:
```env
REACT_APP_API_URL=https://your-backend-domain.com
```

2. **Build**:
```bash
npm run build
```

3. **Deploy**:
```bash
# For Vercel
vercel --prod

# For Netlify
netlify deploy --prod
```

## ?? Troubleshooting

### Backend Issues

**Issue**: "Claude AI is not configured"
```bash
# Check environment variable
echo $ANTHROPIC_API_KEY

# Or in Python:
python -c "import os; print(os.getenv('ANTHROPIC_API_KEY'))"
```

**Issue**: CORS errors
```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check middleware order in main.py
# CORS middleware should be added BEFORE routes
```

**Issue**: Import errors
```bash
# Verify all services are in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use relative imports
from services.ai_service import AIService
```

### Frontend Issues

**Issue**: "Failed to fetch"
```javascript
// Check API URL in console
console.log(process.env.REACT_APP_API_URL);

// Verify backend is running
fetch('http://localhost:8000/api/v1/chat/health')
  .then(r => r.json())
  .then(console.log);
```

**Issue**: Markdown not rendering
```jsx
// Import CSS
import './styles/chat.css';

// Check markdown-config.js exports
import { remarkPlugins } from './utils/markdown-config';
console.log(remarkPlugins);
```

**Issue**: Code highlighting not working
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## ?? Monitoring

### Backend Logging

Add to `main.py`:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
```

### Frontend Analytics

Add to `ChatInterface.jsx`:
```jsx
useEffect(() => {
  // Track message sent
  analytics.track('message_sent', {
    format_type: response.format_type,
    message_length: inputValue.length,
  });
}, [messages]);
```

## ?? Security Checklist

- [ ] API key stored in environment variables (not committed)
- [ ] CORS configured for production domains only
- [ ] Input validation on backend (Pydantic models)
- [ ] XSS protection (rehype-sanitize in frontend)
- [ ] Rate limiting enabled
- [ ] HTTPS in production
- [ ] Content Security Policy headers

## ?? Performance Optimization

### Backend
- Use async/await throughout
- Enable response caching for common queries
- Implement connection pooling for Claude API
- Add Redis for session storage

### Frontend
- Code splitting with React.lazy()
- Memoize message components
- Debounce user input
- Virtual scrolling for long conversations

## ?? Next Features

1. **Message History Persistence**
   - Database integration (PostgreSQL/MongoDB)
   - User sessions

2. **Advanced Features**
   - Voice input/output
   - File upload and analysis
   - Multi-language support
   - Message reactions/ratings

3. **Admin Dashboard**
   - Usage analytics
   - User management
   - API key rotation

## ?? Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [React Markdown](https://github.com/remarkjs/react-markdown)
- [Deployment Guide](./AI_CHAT_INTEGRATION.md)

## ? Final Checklist

Before going live:

- [ ] Backend health check returns healthy
- [ ] Frontend connects to backend
- [ ] Messages send and receive correctly
- [ ] Markdown renders properly
- [ ] Code blocks have syntax highlighting
- [ ] Different format types work (conversational, technical, etc.)
- [ ] Error handling works gracefully
- [ ] Mobile responsive
- [ ] Production environment variables set
- [ ] CORS configured correctly
- [ ] SSL/HTTPS enabled

## ?? You're Ready!

Your AI chat system is complete and production-ready. The system will:

1. **Analyze context** - Understand user intent and conversation tone
2. **Select format** - Choose the best response structure
3. **Generate content** - Use Claude AI for intelligent responses
4. **Apply formatting** - Add proper markdown and styling
5. **Render beautifully** - Display with syntax highlighting and responsive design

Enjoy your new AI-powered chat system! ??
