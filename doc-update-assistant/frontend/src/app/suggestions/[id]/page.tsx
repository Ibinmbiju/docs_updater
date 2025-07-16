'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { apiService } from '@/services/api';
import { GitHubStyleDiffViewer } from '@/components/suggestions/github-style-diff-viewer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { formatRelativeTime, getStatusColor, formatConfidence, getConfidenceColor } from '@/lib/utils';
import { ArrowLeft, CheckCircle, XCircle, GitBranch, Clock, User, Calendar } from 'lucide-react';

// Helper function to safely get error message
const getErrorMessage = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  if (error && typeof error === 'object' && 'message' in error) {
    return String((error as any).message);
  }
  return 'Unknown error occurred';
};

interface SuggestionDetailPageProps {
  params: { id: string };
}

function SuggestionDetailPage({ params }: SuggestionDetailPageProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { id } = params;

  // Fetch suggestion
  const { data: suggestion, isLoading, error } = useQuery({
    queryKey: ['suggestion', id],
    queryFn: () => apiService.getSuggestion(id),
  });

  // Fetch suggestion diff
  const { data: diffData } = useQuery({
    queryKey: ['suggestion-diff', id],
    queryFn: () => apiService.getSuggestionDiff(id),
    enabled: !!suggestion,
  });

  // Approve suggestion mutation
  const approveMutation = useMutation({
    mutationFn: () => apiService.approveSuggestion(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suggestion', id] });
      queryClient.invalidateQueries({ queryKey: ['suggestions'] });
    },
  });

  // Reject suggestion mutation
  const rejectMutation = useMutation({
    mutationFn: () => apiService.rejectSuggestion(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suggestion', id] });
      queryClient.invalidateQueries({ queryKey: ['suggestions'] });
    },
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'rejected':
        return <XCircle className="h-5 w-5 text-red-600" />;
      case 'merged':
        return <GitBranch className="h-5 w-5 text-purple-600" />;
      default:
        return <Clock className="h-5 w-5 text-yellow-600" />;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-1/4"></div>
            <div className="h-32 bg-muted rounded"></div>
            <div className="h-64 bg-muted rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !suggestion) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <Card>
            <CardContent className="pt-6">
              <p className="text-destructive">
                Error loading suggestion: {error?.message || 'Not found'}
              </p>
              <Button 
                variant="outline" 
                className="mt-4"
                onClick={() => router.push('/suggestions')}
              >
                Back to Suggestions
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => router.push('/suggestions')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Suggestions
              </Button>
              <div className="flex items-center gap-2">
                {getStatusIcon(suggestion.status)}
                <h1 className="text-xl font-bold truncate">{suggestion.title}</h1>
              </div>
            </div>
            <div className="flex gap-2">
              {suggestion.status === 'pending' && (
                <>
                  <Button
                    onClick={() => approveMutation.mutate()}
                    disabled={approveMutation.isPending}
                    className="flex items-center gap-2"
                  >
                    <CheckCircle className="h-4 w-4" />
                    {approveMutation.isPending ? 'Approving...' : 'Approve'}
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={() => rejectMutation.mutate()}
                    disabled={rejectMutation.isPending}
                    className="flex items-center gap-2"
                  >
                    <XCircle className="h-4 w-4" />
                    {rejectMutation.isPending ? 'Rejecting...' : 'Reject'}
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 space-y-6">
        {/* Suggestion Overview */}
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="space-y-2">
                <CardTitle className="text-xl">{suggestion.title}</CardTitle>
                <CardDescription className="text-base">
                  {suggestion.description}
                </CardDescription>
              </div>
              <div className="flex flex-col gap-2 ml-4">
                <Badge className={getStatusColor(suggestion.status)}>
                  {suggestion.status}
                </Badge>
                <Badge variant="outline" className="capitalize">
                  {suggestion.suggestion_type}
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Confidence:</span>
                <span className={`font-medium ${getConfidenceColor(suggestion.confidence_score)}`}>
                  {formatConfidence(suggestion.confidence_score)}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span>{formatRelativeTime(suggestion.created_at)}</span>
              </div>
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-muted-foreground" />
                <span>{suggestion.created_by}</span>
              </div>
              {suggestion.reviewed_by && (
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">Reviewed by:</span>
                  <span>{suggestion.reviewed_by}</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* AI Reasoning */}
        {suggestion.reasoning && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">AI Reasoning</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed italic text-muted-foreground">
                "{suggestion.reasoning}"
              </p>
            </CardContent>
          </Card>
        )}

        {/* Diff Statistics */}
        {diffData && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Change Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded"></div>
                  <span>+{diffData.stats.additions} additions</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded"></div>
                  <span>-{diffData.stats.deletions} deletions</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-500 rounded"></div>
                  <span>{diffData.stats.changes} hunks</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* GitHub-Style Diff Viewer */}
        <GitHubStyleDiffViewer
          original={suggestion.original_content}
          suggested={suggestion.suggested_content}
          diffHunks={suggestion.diff_hunks}
          title="Proposed Changes"
        />

        {/* Metadata */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Additional Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-medium mb-2">Document ID</h4>
              <p className="text-sm text-muted-foreground font-mono">
                {suggestion.document_id}
              </p>
            </div>
            <div>
              <h4 className="font-medium mb-2">Section ID</h4>
              <p className="text-sm text-muted-foreground font-mono">
                {suggestion.section_id}
              </p>
            </div>
            {suggestion.affected_sections.length > 0 && (
              <div>
                <h4 className="font-medium mb-2">Affected Sections</h4>
                <div className="flex flex-wrap gap-2">
                  {suggestion.affected_sections.map((sectionId, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {sectionId}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

export default function SuggestionDetail({ params }: SuggestionDetailPageProps) {
  return <SuggestionDetailPage params={params} />;
}