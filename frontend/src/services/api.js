/**
 * API service for communicating with the FastAPI backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Send a chat message to the AI backend
 * @param {string} message - The user's message
 * @param {Array} conversationHistory - Previous messages in the conversation
 * @returns {Promise<Object>} - The AI response
 */
export const sendChatMessage = async (message, conversationHistory = []) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_history: conversationHistory.map(msg => ({
          username: msg.role === 'user' ? 'User' : 'Assistant',
          content: msg.content,
          timestamp: msg.timestamp || new Date().toISOString(),
        })),
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};

/**
 * Check the health of the chat service
 * @returns {Promise<Object>} - Health status
 */
export const checkChatHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/health`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error checking chat health:', error);
    throw error;
  }
};

/**
 * Send a streaming chat message (for future implementation)
 * @param {string} message - The user's message
 * @param {Array} conversationHistory - Previous messages
 * @param {Function} onChunk - Callback for each chunk of the response
 * @returns {Promise<void>}
 */
export const sendStreamingChatMessage = async (
  message,
  conversationHistory = [],
  onChunk
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/ai/stream/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: conversationHistory.map(msg => ({
          role: msg.role,
          content: msg.content,
        })),
        max_tokens: 2048,
        temperature: 0.7,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'content' && onChunk) {
              onChunk(data.text);
            } else if (data.type === 'done') {
              return;
            } else if (data.type === 'error') {
              throw new Error(data.error);
            }
          } catch (e) {
            console.warn('Failed to parse SSE data:', e);
          }
        }
      }
    }
  } catch (error) {
    console.error('Error in streaming chat:', error);
    throw error;
  }
};

export default {
  sendChatMessage,
  checkChatHealth,
  sendStreamingChatMessage,
};
