import React, { useState, useMemo } from 'react';
import { DiffHunk } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Eye, SplitSquareHorizontal, Copy, Check } from 'lucide-react';

interface GitHubStyleDiffViewerProps {
  original: string;
  suggested: string;
  diffHunks: DiffHunk[];
  title?: string;
  className?: string;
}

interface DiffLine {
  type: 'add' | 'remove' | 'context';
  content: string;
  oldLineNumber?: number;
  newLineNumber?: number;
}

export function GitHubStyleDiffViewer({ 
  original, 
  suggested, 
  diffHunks, 
  title = 'Proposed Changes',
  className = ""
}: GitHubStyleDiffViewerProps) {
  const [viewMode, setViewMode] = useState<'unified' | 'split'>('unified');
  const [copiedContent, setCopiedContent] = useState<'original' | 'suggested' | null>(null);

  // Generate diff lines for unified view
  const diffLines = useMemo(() => {
    const lines: DiffLine[] = [];
    const originalLines = original.split('\n');
    const suggestedLines = suggested.split('\n');
    
    // Simple line-by-line diff algorithm
    let originalIndex = 0;
    let suggestedIndex = 0;
    
    while (originalIndex < originalLines.length || suggestedIndex < suggestedLines.length) {
      const originalLine = originalLines[originalIndex];
      const suggestedLine = suggestedLines[suggestedIndex];
      
      if (originalIndex >= originalLines.length) {
        // Only suggested lines left
        lines.push({
          type: 'add',
          content: suggestedLine,
          newLineNumber: suggestedIndex + 1
        });
        suggestedIndex++;
      } else if (suggestedIndex >= suggestedLines.length) {
        // Only original lines left
        lines.push({
          type: 'remove',
          content: originalLine,
          oldLineNumber: originalIndex + 1
        });
        originalIndex++;
      } else if (originalLine === suggestedLine) {
        // Lines are the same
        lines.push({
          type: 'context',
          content: originalLine,
          oldLineNumber: originalIndex + 1,
          newLineNumber: suggestedIndex + 1
        });
        originalIndex++;
        suggestedIndex++;
      } else {
        // Lines are different - mark as removed and added
        lines.push({
          type: 'remove',
          content: originalLine,
          oldLineNumber: originalIndex + 1
        });
        lines.push({
          type: 'add',
          content: suggestedLine,
          newLineNumber: suggestedIndex + 1
        });
        originalIndex++;
        suggestedIndex++;
      }
    }
    
    return lines;
  }, [original, suggested]);

  const stats = useMemo(() => {
    const additions = diffLines.filter(line => line.type === 'add').length;
    const deletions = diffLines.filter(line => line.type === 'remove').length;
    return { additions, deletions };
  }, [diffLines]);

  const copyToClipboard = async (content: string, type: 'original' | 'suggested') => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedContent(type);
      setTimeout(() => setCopiedContent(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const renderUnifiedView = () => {
    return (
      <div className="font-mono text-sm">
        {diffLines.map((line, index) => {
          const lineClass = {
            add: 'bg-green-50 border-l-4 border-green-500',
            remove: 'bg-red-50 border-l-4 border-red-500',
            context: 'bg-gray-50 border-l-4 border-transparent'
          }[line.type];

          const textClass = {
            add: 'text-green-800',
            remove: 'text-red-800',
            context: 'text-gray-700'
          }[line.type];

          const prefix = {
            add: '+',
            remove: '-',
            context: ' '
          }[line.type];

          const prefixClass = {
            add: 'text-green-600 bg-green-100',
            remove: 'text-red-600 bg-red-100',
            context: 'text-gray-400 bg-gray-100'
          }[line.type];

          return (
            <div key={index} className={`flex ${lineClass} hover:bg-opacity-80 transition-colors`}>
              {/* Line numbers */}
              <div className="flex">
                <span className="w-12 text-gray-400 text-right pr-2 select-none bg-gray-50 border-r">
                  {line.oldLineNumber || ''}
                </span>
                <span className="w-12 text-gray-400 text-right pr-2 select-none bg-gray-50 border-r">
                  {line.newLineNumber || ''}
                </span>
              </div>
              
              {/* Prefix */}
              <span className={`w-6 text-center ${prefixClass} border-r select-none`}>
                {prefix}
              </span>
              
              {/* Content */}
              <span className={`flex-1 px-2 py-1 whitespace-pre-wrap ${textClass}`}>
                {line.content || ' '}
              </span>
            </div>
          );
        })}
      </div>
    );
  };

  const renderSplitView = () => {
    const originalLines = original.split('\n');
    const suggestedLines = suggested.split('\n');
    
    return (
      <div className="grid grid-cols-2 gap-1 h-96 overflow-hidden">
        {/* Original (Previous Version) */}
        <div className="border rounded-l-md overflow-hidden">
          <div className="bg-red-50 text-red-800 px-3 py-2 text-sm font-medium border-b flex items-center justify-between">
            <span>Previous Version</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(original, 'original')}
              className="h-6 w-6 p-0"
            >
              {copiedContent === 'original' ? 
                <Check className="h-3 w-3 text-green-600" /> : 
                <Copy className="h-3 w-3" />
              }
            </Button>
          </div>
          <div className="overflow-y-auto h-full">
            <div className="font-mono text-sm">
              {originalLines.map((line, index) => {
                const isChanged = suggestedLines[index] !== line;
                return (
                  <div 
                    key={index} 
                    className={`flex ${isChanged ? 'bg-red-50' : 'bg-gray-50'} hover:bg-opacity-80`}
                  >
                    <span className="w-8 text-gray-400 text-right pr-2 select-none bg-gray-100 border-r">
                      {index + 1}
                    </span>
                    <span className={`flex-1 px-2 py-1 whitespace-pre-wrap ${
                      isChanged ? 'text-red-800' : 'text-gray-700'
                    }`}>
                      {line || ' '}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Suggested (New Version) */}
        <div className="border rounded-r-md overflow-hidden">
          <div className="bg-green-50 text-green-800 px-3 py-2 text-sm font-medium border-b flex items-center justify-between">
            <span>Suggested Version</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(suggested, 'suggested')}
              className="h-6 w-6 p-0"
            >
              {copiedContent === 'suggested' ? 
                <Check className="h-3 w-3 text-green-600" /> : 
                <Copy className="h-3 w-3" />
              }
            </Button>
          </div>
          <div className="overflow-y-auto h-full">
            <div className="font-mono text-sm">
              {suggestedLines.map((line, index) => {
                const isChanged = originalLines[index] !== line;
                return (
                  <div 
                    key={index} 
                    className={`flex ${isChanged ? 'bg-green-50' : 'bg-gray-50'} hover:bg-opacity-80`}
                  >
                    <span className="w-8 text-gray-400 text-right pr-2 select-none bg-gray-100 border-r">
                      {index + 1}
                    </span>
                    <span className={`flex-1 px-2 py-1 whitespace-pre-wrap ${
                      isChanged ? 'text-green-800' : 'text-gray-700'
                    }`}>
                      {line || ' '}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <CardTitle className="text-lg">{title}</CardTitle>
            <div className="flex gap-2">
              <Badge variant="outline" className="text-green-600 bg-green-50">
                +{stats.additions}
              </Badge>
              <Badge variant="outline" className="text-red-600 bg-red-50">
                -{stats.deletions}
              </Badge>
              <Badge variant="secondary">
                {Math.abs(stats.additions - stats.deletions)} net changes
              </Badge>
            </div>
          </div>
          
          <div className="flex gap-2">
            <Button
              variant={viewMode === 'unified' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('unified')}
            >
              <Eye className="h-4 w-4 mr-1" />
              Unified
            </Button>
            <Button
              variant={viewMode === 'split' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('split')}
            >
              <SplitSquareHorizontal className="h-4 w-4 mr-1" />
              Split
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        <div className="border-t">
          {viewMode === 'unified' ? (
            <div className="max-h-96 overflow-y-auto">
              {renderUnifiedView()}
            </div>
          ) : (
            renderSplitView()
          )}
        </div>
      </CardContent>
    </Card>
  );
}