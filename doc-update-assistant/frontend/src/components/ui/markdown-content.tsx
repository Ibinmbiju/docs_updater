import React from 'react';

interface MarkdownContentProps {
  content: string;
  className?: string;
}

export function MarkdownContent({ content, className = '' }: MarkdownContentProps) {
  // Process content for better display
  const processContent = (content: string) => {
    let processed = content
      .replace(/\[Skip to content\].*?\n\n/, '')
      .replace(/```md-code__content/g, '```bash')
      .replace(/\\\n/g, '\n');
    
    return processed;
  };

  const renderContent = (text: string) => {
    const processed = processContent(text);
    const lines = processed.split('\n');
    const elements: React.ReactNode[] = [];
    let currentSection: React.ReactNode[] = [];
    let inCodeBlock = false;
    let codeBlockContent: string[] = [];
    let codeBlockLanguage = '';

    const flushCurrentSection = () => {
      if (currentSection.length > 0) {
        elements.push(
          <div key={elements.length} className="mb-6">
            {currentSection}
          </div>
        );
        currentSection = [];
      }
    };

    lines.forEach((line, index) => {
      // Handle code blocks
      if (line.startsWith('```')) {
        if (inCodeBlock) {
          // End code block
          inCodeBlock = false;
          currentSection.push(
            <div key={`code-${index}`} className="my-4">
              <pre className="bg-muted/50 p-4 rounded-lg overflow-x-auto border">
                <code className="text-sm">{codeBlockContent.join('\n')}</code>
              </pre>
            </div>
          );
          codeBlockContent = [];
          codeBlockLanguage = '';
        } else {
          // Start code block
          inCodeBlock = true;
          codeBlockLanguage = line.replace('```', '');
        }
        return;
      }

      if (inCodeBlock) {
        codeBlockContent.push(line);
        return;
      }

      // Handle headers
      if (line.startsWith('# ')) {
        flushCurrentSection();
        elements.push(
          <h1 key={`h1-${index}`} className="text-4xl font-bold mb-6 text-foreground border-b pb-4">
            {line.replace('# ', '')}
          </h1>
        );
      } else if (line.startsWith('## ')) {
        flushCurrentSection();
        elements.push(
          <h2 key={`h2-${index}`} className="text-2xl font-semibold mb-4 mt-8 text-foreground border-b pb-2">
            {line.replace('## ', '')}
          </h2>
        );
      } else if (line.startsWith('### ')) {
        currentSection.push(
          <h3 key={`h3-${index}`} className="text-xl font-medium mb-3 mt-6 text-foreground">
            {line.replace('### ', '')}
          </h3>
        );
      } else if (line.startsWith('#### ')) {
        currentSection.push(
          <h4 key={`h4-${index}`} className="text-lg font-medium mb-2 mt-4 text-foreground">
            {line.replace('#### ', '')}
          </h4>
        );
      } else if (line.trim() === '') {
        // Empty line - add spacing
        if (currentSection.length > 0) {
          currentSection.push(<br key={`br-${index}`} />);
        }
      } else {
        // Regular content
        // Handle links
        const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
        const processedLine = line.replace(linkRegex, (match, text, url) => {
          return `<a href="${url}" class="text-primary hover:underline" target="_blank" rel="noopener noreferrer">${text}</a>`;
        });

        // Handle inline code
        const codeRegex = /`([^`]+)`/g;
        const finalLine = processedLine.replace(codeRegex, (match, code) => {
          return `<code class="bg-muted px-1.5 py-0.5 rounded text-sm font-mono">${code}</code>`;
        });

        currentSection.push(
          <p 
            key={`p-${index}`} 
            className="text-muted-foreground leading-relaxed mb-2"
            dangerouslySetInnerHTML={{ __html: finalLine }}
          />
        );
      }
    });

    flushCurrentSection();
    return elements;
  };

  return (
    <div className={`prose prose-lg max-w-none ${className}`}>
      {renderContent(content)}
    </div>
  );
}