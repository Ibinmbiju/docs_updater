import { DiffHunk } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { Eye, SplitSquareHorizontal } from 'lucide-react';

interface DiffViewerProps {
  original: string;
  suggested: string;
  diffHunks: DiffHunk[];
  language?: string;
  title?: string;
}

export function DiffViewer({ 
  original, 
  suggested, 
  diffHunks, 
  language = 'text',
  title = 'Changes'
}: DiffViewerProps) {
  const [viewMode, setViewMode] = useState<'unified' | 'split'>('unified');

  const renderUnifiedDiff = () => {
    return (
      <div className="font-mono text-sm">
        {diffHunks.map((hunk, hunkIndex) => (
          <div key={hunkIndex} className="mb-4">
            {/* Hunk header */}
            <div className="bg-blue-50 text-blue-800 px-3 py-1 text-xs border-l-4 border-blue-400">
              @@ -{hunk.old_start},{hunk.old_count} +{hunk.new_start},{hunk.new_count} @@
            </div>
            
            {/* Context before */}
            {hunk.context_before.map((line, lineIndex) => (
              <div key={`context-before-${lineIndex}`} className="flex">
                <span className="w-12 text-gray-400 text-right pr-2 select-none">
                  {hunk.old_start - hunk.context_before.length + lineIndex}
                </span>
                <span className="w-12 text-gray-400 text-right pr-2 select-none">
                  {hunk.new_start - hunk.context_before.length + lineIndex}
                </span>
                <span className="w-4 text-gray-400 pr-2"> </span>
                <span className="flex-1 whitespace-pre-wrap">{line}</span>
              </div>
            ))}

            {/* Old lines (deletions) */}
            {hunk.old_lines.filter(line => !hunk.new_lines.includes(line)).map((line, lineIndex) => (
              <div key={`old-${lineIndex}`} className="flex bg-red-50">
                <span className="w-12 text-gray-400 text-right pr-2 select-none">
                  {hunk.old_start + lineIndex}
                </span>
                <span className="w-12 text-gray-400 text-right pr-2 select-none"></span>
                <span className="w-4 text-red-600 pr-2">-</span>
                <span className="flex-1 whitespace-pre-wrap text-red-800">{line}</span>
              </div>
            ))}

            {/* New lines (additions) */}
            {hunk.new_lines.filter(line => !hunk.old_lines.includes(line)).map((line, lineIndex) => (
              <div key={`new-${lineIndex}`} className="flex bg-green-50">
                <span className="w-12 text-gray-400 text-right pr-2 select-none"></span>
                <span className="w-12 text-gray-400 text-right pr-2 select-none">
                  {hunk.new_start + lineIndex}
                </span>
                <span className="w-4 text-green-600 pr-2">+</span>
                <span className="flex-1 whitespace-pre-wrap text-green-800">{line}</span>
              </div>
            ))}

            {/* Context after */}
            {hunk.context_after.map((line, lineIndex) => (
              <div key={`context-after-${lineIndex}`} className="flex">
                <span className="w-12 text-gray-400 text-right pr-2 select-none">
                  {hunk.old_start + hunk.old_count + lineIndex}
                </span>
                <span className="w-12 text-gray-400 text-right pr-2 select-none">
                  {hunk.new_start + hunk.new_count + lineIndex}
                </span>
                <span className="w-4 text-gray-400 pr-2"> </span>
                <span className="flex-1 whitespace-pre-wrap">{line}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  };

  const renderSplitDiff = () => {
    const originalLines = original.split('\n');
    const suggestedLines = suggested.split('\n');
    
    return (
      <div className="grid grid-cols-2 gap-4">
        {/* Original */}
        <div className="border rounded-md">
          <div className="bg-red-50 text-red-800 px-3 py-2 text-sm font-medium border-b">
            Original
          </div>
          <div className="p-3 font-mono text-sm max-h-96 overflow-y-auto">
            {originalLines.map((line, index) => (
              <div key={index} className="flex">
                <span className="w-8 text-gray-400 text-right pr-2 select-none">
                  {index + 1}
                </span>
                <span className="flex-1 whitespace-pre-wrap">{line || ' '}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Suggested */}
        <div className="border rounded-md">
          <div className="bg-green-50 text-green-800 px-3 py-2 text-sm font-medium border-b">
            Suggested
          </div>
          <div className="p-3 font-mono text-sm max-h-96 overflow-y-auto">
            {suggestedLines.map((line, index) => (
              <div key={index} className="flex">
                <span className="w-8 text-gray-400 text-right pr-2 select-none">
                  {index + 1}
                </span>
                <span className="flex-1 whitespace-pre-wrap">{line || ' '}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const totalAdditions = diffHunks.reduce((acc, hunk) => 
    acc + hunk.new_lines.filter(line => !hunk.old_lines.includes(line)).length, 0
  );
  
  const totalDeletions = diffHunks.reduce((acc, hunk) => 
    acc + hunk.old_lines.filter(line => !hunk.new_lines.includes(line)).length, 0
  );

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <CardTitle className="text-lg">{title}</CardTitle>
            <div className="flex gap-2">
              <Badge variant="outline" className="text-green-600">
                +{totalAdditions}
              </Badge>
              <Badge variant="outline" className="text-red-600">
                -{totalDeletions}
              </Badge>
              <Badge variant="secondary">
                {diffHunks.length} hunks
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
      <CardContent>
        <div className="border rounded-md overflow-hidden">
          <div className="max-h-96 overflow-y-auto">
            {viewMode === 'unified' ? renderUnifiedDiff() : renderSplitDiff()}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}