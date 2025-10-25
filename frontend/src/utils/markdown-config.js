/**
 * Markdown rendering configuration
 * Used by MarkdownRenderer component
 */

import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize from 'rehype-sanitize';

/**
 * Remark plugins for markdown processing
 * - remarkGfm: GitHub Flavored Markdown support (tables, strikethrough, task lists)
 */
export const remarkPlugins = [remarkGfm];

/**
 * Rehype plugins for HTML processing
 * - rehypeRaw: Allow raw HTML in markdown
 * - rehypeSanitize: Sanitize HTML to prevent XSS attacks
 */
export const rehypePlugins = [rehypeRaw, rehypeSanitize];

/**
 * Supported programming languages for syntax highlighting
 */
export const supportedLanguages = [
  'javascript',
  'typescript',
  'python',
  'java',
  'csharp',
  'cpp',
  'c',
  'go',
  'rust',
  'ruby',
  'php',
  'swift',
  'kotlin',
  'scala',
  'r',
  'sql',
  'bash',
  'shell',
  'powershell',
  'json',
  'yaml',
  'xml',
  'html',
  'css',
  'scss',
  'markdown',
  'plaintext',
];

/**
 * Detect language from code block class name
 * @param {string} className - The class name from code element
 * @returns {string} - Detected language or 'plaintext'
 */
export const detectLanguage = (className = '') => {
  const match = /language-(\w+)/.exec(className);
  const lang = match ? match[1].toLowerCase() : '';
  
  if (supportedLanguages.includes(lang)) {
    return lang;
  }
  
  return 'plaintext';
};

/**
 * Format type configurations
 * Maps format types to styling preferences
 */
export const formatTypeConfig = {
  conversational: {
    maxWidth: '700px',
    fontSize: '16px',
    lineHeight: '1.6',
    color: '#333',
  },
  structured: {
    maxWidth: '800px',
    fontSize: '15px',
    lineHeight: '1.7',
    color: '#2c3e50',
  },
  code_focused: {
    maxWidth: '900px',
    fontSize: '14px',
    lineHeight: '1.5',
    color: '#24292e',
  },
  empathetic: {
    maxWidth: '650px',
    fontSize: '16px',
    lineHeight: '1.8',
    color: '#444',
  },
  balanced: {
    maxWidth: '750px',
    fontSize: '15px',
    lineHeight: '1.65',
    color: '#333',
  },
};

/**
 * Get CSS variables for a specific format type
 * @param {string} formatType - The format type
 * @returns {Object} - CSS properties object
 */
export const getFormatTypeStyles = (formatType = 'balanced') => {
  return formatTypeConfig[formatType] || formatTypeConfig.balanced;
};

export default {
  remarkPlugins,
  rehypePlugins,
  supportedLanguages,
  detectLanguage,
  formatTypeConfig,
  getFormatTypeStyles,
};
