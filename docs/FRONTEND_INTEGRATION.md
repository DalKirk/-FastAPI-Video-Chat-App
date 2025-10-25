# Frontend Integration Guide

## Overview

This guide explains how to integrate the AI chat components into your React application.

## Installation

### 1. Install Dependencies

```bash
cd frontend
npm install
```

Required packages:
- `react-markdown`: Markdown rendering
- `react-syntax-highlighter`: Code syntax highlighting
- `remark-gfm`: GitHub Flavored Markdown support
- `rehype-raw`: HTML support in markdown
- `rehype-sanitize`: Security (XSS prevention)

### 2. Project Structure

```
frontend/
??? src/
?   ??? components/
?   ?   ??? Chat/
?   ?   ?   ??? ChatInterface.jsx      # Main chat UI
?   ?   ?   ??? MessageDisplay.jsx     # Individual messages
?   ?   ?   ??? CodeBlock.jsx          # Code highlighting
?   ?   ??? Markdown/
?   ?       ??? MarkdownRenderer.jsx   # Markdown ? HTML
?   ??? services/
?   ?   ??? api.js                     # Backend API calls
?   ??? utils/
?   ?   ??? markdown-config.js         # Markdown config
?   ??? styles/
?       ??? chat.css                   # Component styles
??? package.json
```

## Usage

### Basic Integration

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

### Custom Integration

#### Using Individual Components

```jsx
import MessageDisplay from './components/Chat/MessageDisplay';
import MarkdownRenderer from './components/Markdown/MarkdownRenderer';

// Display a single message
<MessageDisplay
  message="Hello, how can I help?"
  isUser={false}
  formatType="conversational"
  timestamp={new Date().toISOString()}
/>

// Render markdown only
<MarkdownRenderer content="## Hello\n\nThis is **bold**" />
```

#### Using the API Service

```jsx
import { sendChatMessage, checkChatHealth } from './services/api';

// Send a message
const response = await sendChatMessage('How do I use FastAPI?', []);
console.log(response.content);
console.log(response.format_type);
console.log(response.metadata);

// Check service health
const health = await checkChatHealth();
console.log(health.status);
```

## Configuration

### Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

For production:
```env
REACT_APP_API_URL=https://your-api-domain.com
```

### Customizing Styles

#### Method 1: Override CSS Variables

```css
/* In your global CSS */
:root {
  --chat-primary-color: #2196F3;
  --chat-background: #f5f5f5;
  --chat-message-bg: white;
  --chat-user-bg: #2196F3;
  --chat-border-color: #e0e0e0;
}
```

#### Method 2: Custom CSS Classes

```jsx
<ChatInterface className="my-custom-chat" />
```

```css
.my-custom-chat {
  max-width: 1000px;
  border-radius: 12px;
}

.my-custom-chat .message-content {
  border-radius: 16px;
}
```

### Customizing Markdown Rendering

Edit `frontend/src/utils/markdown-config.js`:

```javascript
// Add custom language support
export const supportedLanguages = [
  'javascript',
  'python',
  // Add your languages here
];

// Adjust format type styles
export const formatTypeConfig = {
  conversational: {
    maxWidth: '800px', // Changed from 700px
    fontSize: '18px',  // Changed from 16px
  },
  // ...
};
```

## Features

### 1. Context-Aware Formatting

The chat automatically applies different formatting based on the response type:

- **Conversational**: Casual, short paragraphs
- **Structured**: Headers, lists, organized
- **Code-Focused**: Syntax highlighting, technical
- **Empathetic**: Warm, reassuring tone
- **Balanced**: Mix of all formats

### 2. Code Syntax Highlighting

Supports 25+ programming languages with:
- Line numbers
- Copy-to-clipboard button
- Dark/light theme support
- Language detection

Example:
````markdown
```python
def hello_world():
    print("Hello, World!")
```
````

### 3. Markdown Features

- **Headers**: `#`, `##`, `###`
- **Lists**: Bullet (`-`, `*`) and numbered (`1.`)
- **Links**: `[text](url)`
- **Bold**: `**text**` or `__text__`
- **Italic**: `*text*` or `_text_`
- **Code**: Inline `` `code` `` and blocks ` ``` `
- **Tables**: GitHub-style tables
- **Blockquotes**: `> quote`

### 4. Responsive Design

Automatically adapts to mobile devices:
- Adjustable message widths
- Touch-friendly buttons
- Scrollable message history

## Advanced Usage

### Streaming Responses (Future)

```jsx
import { sendStreamingChatMessage } from './services/api';

const [streamedContent, setStreamedContent] = useState('');

await sendStreamingChatMessage(
  'Tell me a story',
  messages,
  (chunk) => {
    setStreamedContent(prev => prev + chunk);
  }
);
```

### Custom Message Components

```jsx
import MessageDisplay from './components/Chat/MessageDisplay';

// Add custom message types
const MyCustomMessage = ({ message, formatType }) => {
  return (
    <MessageDisplay
      message={message}
      formatType={formatType}
      className="custom-message-style"
    />
  );
};
```

### Integrating with State Management

```jsx
// With Redux
import { useDispatch, useSelector } from 'react-redux';

const ChatWrapper = () => {
  const messages = useSelector(state => state.chat.messages);
  const dispatch = useDispatch();

  const handleSend = async (message) => {
    const response = await sendChatMessage(message, messages);
    dispatch(addMessage(response));
  };

  return <ChatInterface onSend={handleSend} />;
};
```

## Troubleshooting

### Issue: Markdown not rendering

**Solution**: Ensure you've imported the CSS:
```jsx
import './styles/chat.css';
```

### Issue: Code blocks not highlighting

**Solution**: Check that the language is supported:
```javascript
import { supportedLanguages } from './utils/markdown-config';
console.log(supportedLanguages);
```

### Issue: API connection fails

**Solution**: Verify the backend URL in `.env`:
```env
REACT_APP_API_URL=http://localhost:8000
```

Check CORS settings on the backend:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Messages not scrolling

**Solution**: Ensure the messages container has a fixed height:
```css
.chat-messages {
  height: calc(100vh - 200px);
  overflow-y: auto;
}
```

## Performance Tips

1. **Code Splitting**: Lazy load the chat component
```jsx
const ChatInterface = React.lazy(() => import('./components/Chat/ChatInterface'));
```

2. **Memoization**: Use React.memo for message components
```jsx
const MessageDisplay = React.memo(({ message, isUser }) => {
  // ...
});
```

3. **Debounce Input**: Prevent excessive API calls
```jsx
import { debounce } from 'lodash';

const debouncedSend = debounce(handleSend, 300);
```

## Accessibility

The components include:
- ARIA labels for buttons
- Keyboard navigation support
- Screen reader-friendly markup
- Focus management

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari, Chrome Android

## Next Steps

1. Add user authentication
2. Implement message persistence
3. Add file upload support
4. Implement voice input
5. Add message reactions/ratings
6. Multi-language support

## Resources

- [React Markdown Docs](https://github.com/remarkjs/react-markdown)
- [React Syntax Highlighter](https://github.com/react-syntax-highlighter/react-syntax-highlighter)
- [GFM Specification](https://github.github.com/gfm/)
