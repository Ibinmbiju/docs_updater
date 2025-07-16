import { Suggestion } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { formatRelativeTime, getStatusColor, formatConfidence, getConfidenceColor } from '@/lib/utils';
import { CheckCircle, XCircle, Clock, GitBranch } from 'lucide-react';

interface SuggestionCardProps {
  suggestion: Suggestion;
  onClick: () => void;
  onApprove?: (id: string) => void;
  onReject?: (id: string) => void;
  showActions?: boolean;
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

export function SuggestionCard({ 
  suggestion, 
  onClick, 
  onApprove, 
  onReject, 
  showActions = true 
}: SuggestionCardProps) {
  const handleApprove = (e: React.MouseEvent) => {
    e.stopPropagation();
    onApprove?.(suggestion.id);
  };

  const handleReject = (e: React.MouseEvent) => {
    e.stopPropagation();
    onReject?.(suggestion.id);
  };

  return (
    <Card
      className="cursor-pointer transition-all hover:shadow-md hover:border-primary/50"
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              {getStatusIcon(suggestion.status)}
              <CardTitle className="text-lg truncate">{suggestion.title}</CardTitle>
            </div>
            <CardDescription className="line-clamp-2">
              {suggestion.description}
            </CardDescription>
          </div>
          <div className="flex flex-col gap-1 ml-4">
            <Badge className={getStatusColor(suggestion.status)}>
              {suggestion.status}
            </Badge>
            <Badge variant="outline" className="capitalize text-xs">
              {suggestion.suggestion_type}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">
              Confidence: 
              <span className={`ml-1 font-medium ${getConfidenceColor(suggestion.confidence_score)}`}>
                {formatConfidence(suggestion.confidence_score)}
              </span>
            </span>
            <span className="text-muted-foreground">
              {formatRelativeTime(suggestion.created_at)}
            </span>
          </div>

          <div className="text-sm text-muted-foreground">
            <div className="flex items-center gap-4">
              <span>+{suggestion.diff_hunks.reduce((acc, hunk) => acc + hunk.new_lines.length, 0)} additions</span>
              <span>-{suggestion.diff_hunks.reduce((acc, hunk) => acc + hunk.old_lines.length, 0)} deletions</span>
              <span>{suggestion.diff_hunks.length} hunks</span>
            </div>
          </div>

          {suggestion.reasoning && (
            <p className="text-sm text-muted-foreground line-clamp-2 italic">
              "{suggestion.reasoning}"
            </p>
          )}

          {showActions && suggestion.status === 'pending' && (
            <div className="flex gap-2 pt-2">
              <Button
                size="sm"
                variant="default"
                onClick={handleApprove}
                className="flex-1"
              >
                <CheckCircle className="h-4 w-4 mr-1" />
                Approve
              </Button>
              <Button
                size="sm"
                variant="destructive"
                onClick={handleReject}
                className="flex-1"
              >
                <XCircle className="h-4 w-4 mr-1" />
                Reject
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}