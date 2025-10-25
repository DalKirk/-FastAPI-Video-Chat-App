import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

/**
 * MarkdownRenderer component for rendering AI-formatted responses
 * Supports code blocks with syntax highlighting, tables, and GFM features
 */
const MarkdownRenderer = ({ content, className = '' }) => {
  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
        components={{
          // Custom code block renderer with syntax highlighting
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';
            
            return !inline && language ? (
              <SyntaxHighlighter
                style={vscDarkPlus}
                language={language}
                PreTag="div"
                className="code-block"
                showLineNumbers={true}
                customStyle={{
                  margin: '1em 0',
                  borderRadius: '8px',
                  fontSize: '0.9em',
                }}
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className={`inline-code ${className}`} {...props}>
                {children}
              </code>
            );
          },
          
          // Custom heading renderers
          h1: ({ children }) => (
            <h1 className="markdown-h1">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="markdown-h2">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="markdown-h3">{children}</h3>
          ),
          
          // Custom link renderer (open in new tab for external links)
          a: ({ href, children }) => {
            const isExternal = href?.startsWith('http');
            return (
              <a
                href={href}
                target={isExternal ? '_blank' : '_self'}
                rel={isExternal ? 'noopener noreferrer' : ''}
                className="markdown-link"
              >
                {children}
              </a>
            );
          },
          
          // Custom list renderers
          ul: ({ children }) => (
            <ul className="markdown-ul">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="markdown-ol">{children}</ol>
          ),
          
          // Custom table renderer
          table: ({ children }) => (
            <div className="table-wrapper">
              <table className="markdown-table">{children}</table>
            </div>
          ),
          
          // Custom blockquote renderer
          blockquote: ({ children }) => (
            <blockquote className="markdown-blockquote">
              {children}
            </blockquote>
          ),
          
          // Custom paragraph renderer
          p: ({ children }) => (
            <p className="markdown-paragraph">{children}</p>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;
