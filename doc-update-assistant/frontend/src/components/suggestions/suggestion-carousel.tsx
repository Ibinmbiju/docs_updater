import React, { useState } from 'react';
import { Suggestion } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight, CheckCircle, XCircle, Clock, GitBranch } from 'lucide-react';
import { formatRelativeTime, getStatusColor, formatConfidence, getConfidenceColor } from '@/lib/utils';
import { GitHubStyleDiffViewer } from './github-style-diff-viewer';

interface SuggestionCarouselProps {
  suggestions: Suggestion[];
  onSuggestionApprove?: (id: string) => void;
  onSuggestionReject?: (id: string) => void;
  className?: string;
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'approved':
      return <CheckCircle className="h-4 w-4 text-green-600" />;
    case 'rejected':
      return <XCircle className="h-4 w-4 text-red-600" />;
    case 'merged':
      return <GitBranch className="h-4 w-4 text-purple-600" />;
    default:
      return <Clock className="h-4 w-4 text-yellow-600" />;
  }
};

export function SuggestionCarousel({ 
  suggestions, 
  onSuggestionApprove, 
  onSuggestionReject,
  className = ""
}: SuggestionCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!suggestions || suggestions.length === 0) {
    return (
      <Card className={`text-center py-12 ${className}`}>
        <CardContent>
          <p className="text-muted-foreground">No suggestions available</p>
        </CardContent>
      </Card>
    );
  }

  const currentSuggestion = suggestions[currentIndex];

  const goToPrevious = () => {
    setCurrentIndex((prev) => prev === 0 ? suggestions.length - 1 : prev - 1);
  };

  const goToNext = () => {
    setCurrentIndex((prev) => prev === suggestions.length - 1 ? 0 : prev + 1);
  };

  const handleApprove = () => {
    onSuggestionApprove?.(currentSuggestion.id);
  };

  const handleReject = () => {
    onSuggestionReject?.(currentSuggestion.id);
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Carousel Navigation Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={goToPrevious}
            disabled={suggestions.length <= 1}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">
              Suggestion {currentIndex + 1} of {suggestions.length}
            </span>
            <div className="flex gap-1">
              {suggestions.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentIndex(index)}
                  className={`w-2 h-2 rounded-full transition-colors ${
                    index === currentIndex 
                      ? 'bg-primary' 
                      : 'bg-gray-300 hover:bg-gray-400'
                  }`}
                />
              ))}
            </div>
          </div>
          
          <Button
            variant="outline"
            size="sm"
            onClick={goToNext}
            disabled={suggestions.length <= 1}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        {/* Action Buttons */}
        {currentSuggestion.status === 'pending' && (
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="default"
              onClick={handleApprove}
              className="bg-green-600 hover:bg-green-700"
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Approve
            </Button>
            <Button
              size="sm"
              variant="destructive"
              onClick={handleReject}
            >
              <XCircle className="h-4 w-4 mr-2" />
              Reject
            </Button>
          </div>
        )}
      </div>

      {/* Suggestion Details */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                {getStatusIcon(currentSuggestion.status)}
                <CardTitle className="text-xl">{currentSuggestion.title}</CardTitle>
              </div>
              <p className="text-muted-foreground mb-3">
                {currentSuggestion.description}
              </p>
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <Badge className={getStatusColor(currentSuggestion.status)}>
                    {currentSuggestion.status}
                  </Badge>
                  <Badge variant="outline" className="capitalize">
                    {currentSuggestion.suggestion_type}
                  </Badge>
                </div>
                <span className="text-muted-foreground">
                  Confidence: 
                  <span className={`ml-1 font-medium ${getConfidenceColor(currentSuggestion.confidence_score)}`}>
                    {formatConfidence(currentSuggestion.confidence_score)}
                  </span>
                </span>
                <span className="text-muted-foreground">
                  {formatRelativeTime(currentSuggestion.created_at)}
                </span>
              </div>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          {currentSuggestion.reasoning && (
            <div className="mb-4 p-3 bg-blue-50 border-l-4 border-blue-400 rounded-r">
              <p className="text-sm text-blue-800 italic">
                <strong>AI Reasoning:</strong> {currentSuggestion.reasoning}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* GitHub-Style Diff Viewer */}
      <GitHubStyleDiffViewer
        original={currentSuggestion.original_content}
        suggested={currentSuggestion.suggested_content}
        diffHunks={currentSuggestion.diff_hunks}
        title="Proposed Changes"
      />
    </div>
  );
}