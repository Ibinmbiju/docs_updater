'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { Document, Suggestion } from '@/types';
import { DocumentNav } from '@/components/documents/document-nav';
import { SuggestionList } from '@/components/suggestions/suggestion-list';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { FileText, Lightbulb, Search, Sparkles } from 'lucide-react';
import { useRouter } from 'next/navigation';

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

function Dashboard() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [generateQuery, setGenerateQuery] = useState('');

  // Fetch documents
  const { data: documents = [], isLoading: documentsLoading, error: documentsError } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      try {
        const result = await apiService.getDocuments();
        return result;
      } catch (error) {
        console.error('Error fetching documents:', error);
        throw error;
      }
    },
  });

  // Fetch suggestions
  const { data: suggestions = [], isLoading: suggestionsLoading } = useQuery({
    queryKey: ['suggestions'],
    queryFn: async () => {
      const result = await apiService.getSuggestions({ limit: 5 });
      return result;
    },
  });

  // Generate suggestions mutation
  const generateSuggestionsMutation = useMutation({
    mutationFn: async (query: string) => {
      const result = await apiService.generateSuggestions({ query, limit: 5 });
      return result;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['suggestions'] });
      setGenerateQuery('');
    },
    onError: (error) => {
      console.error('Error generating suggestions:', error);
    }
  });

  // Approve suggestion mutation
  const approveSuggestionMutation = useMutation({
    mutationFn: (id: string) => apiService.approveSuggestion(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suggestions'] });
    },
  });

  // Reject suggestion mutation
  const rejectSuggestionMutation = useMutation({
    mutationFn: (id: string) => apiService.rejectSuggestion(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suggestions'] });
    },
  });

  const handleGenerateSuggestions = () => {
    if (generateQuery.trim()) {
      generateSuggestionsMutation.mutate(generateQuery.trim());
    }
  };

  const handleDocumentSelect = (document: Document) => {
    router.push(`/documents/${document.id}`);
  };

  const handleSuggestionSelect = (suggestion: Suggestion) => {
    router.push(`/suggestions/${suggestion.id}`);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-bold">Doc Assist</h1>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => router.push('/documents')}>
                <FileText className="h-4 w-4 mr-2" />
                Documents
              </Button>
              <Button variant="outline" onClick={() => router.push('/suggestions')}>
                <Lightbulb className="h-4 w-4 mr-2" />
                Suggestions
              </Button>
              <Button variant="outline" onClick={() => router.push('/search')}>
                <Search className="h-4 w-4 mr-2" />
                Search
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        {/* Main Content - Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-140px)]">
          {/* Left Column - Documents List */}
          <div className="lg:col-span-1">
            <Card className="h-full flex flex-col shadow-sm">
              <CardHeader className="pb-3 border-b bg-slate-50/50 rounded-t-lg">
                <CardTitle className="flex items-center gap-2 text-base">
                  <FileText className="h-4 w-4" />
                  Documents ({documents.length})
                </CardTitle>
                <CardDescription className="text-sm">
                  Browse and select documents to view
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 p-0 overflow-hidden">
                {documentsLoading ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full"></div>
                  </div>
                ) : documentsError ? (
                  <div className="text-center text-destructive h-full flex items-center justify-center">
                    <div>
                      <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>Error loading documents</p>
                      <p className="text-xs mt-1">{getErrorMessage(documentsError)}</p>
                    </div>
                  </div>
                ) : documents.length === 0 ? (
                  <div className="text-center text-muted-foreground h-full flex items-center justify-center">
                    <div>
                      <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>No documents loaded</p>
                    </div>
                  </div>
                ) : (
                  <div className="h-full overflow-y-auto scrollbar-thin scroll-smooth will-change-scroll">
                    <div className="p-4">
                      <DocumentNav
                        documents={documents}
                        onDocumentSelect={handleDocumentSelect}
                        loading={false}
                      />
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Suggestions Generation and List */}
          <div className="lg:col-span-2">
            <div className="h-full flex flex-col gap-4">
              {/* Generate Suggestions Card - Fixed Height */}
              <Card className="flex-shrink-0 shadow-sm">
                <CardHeader className="pb-3 border-b bg-slate-50/50 rounded-t-lg">
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Sparkles className="h-4 w-4" />
                    Generate Suggestions
                  </CardTitle>
                  <CardDescription className="text-sm">
                    Describe what needs to be updated in your documentation
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-4">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Describe what needs to be updated (e.g., 'Update API endpoints for v2.0')..."
                      value={generateQuery}
                      onChange={(e) => setGenerateQuery(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleGenerateSuggestions()}
                      className="flex-1"
                    />
                    <Button 
                      onClick={handleGenerateSuggestions}
                      disabled={generateSuggestionsMutation.isPending || !generateQuery.trim()}
                      size="sm"
                    >
                      {generateSuggestionsMutation.isPending ? 'Generating...' : 'Generate'}
                    </Button>
                  </div>
                  {generateSuggestionsMutation.error && (
                    <p className="text-xs text-destructive mt-2">
                      Error: {getErrorMessage(generateSuggestionsMutation.error)}
                    </p>
                  )}
                  {generateSuggestionsMutation.isSuccess && (
                    <p className="text-xs text-green-600 mt-2">
                      {generateSuggestionsMutation.data?.total_suggestions > 0 
                        ? `Suggestions generated successfully! (${generateSuggestionsMutation.data.total_suggestions} suggestions)`
                        : "No suggestions generated. Try a different query or check if documents are loaded."
                      }
                    </p>
                  )}
                </CardContent>
              </Card>

              {/* Recent Suggestions Card - Scrollable */}
              <Card className="flex-1 flex flex-col shadow-sm">
                <CardHeader className="pb-3 border-b bg-slate-50/50 rounded-t-lg">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Lightbulb className="h-4 w-4" />
                      Recent Suggestions ({suggestions.length})
                    </CardTitle>
                    <Button variant="outline" size="sm" onClick={() => router.push('/suggestions')}>
                      View All
                    </Button>
                  </div>
                  <CardDescription className="text-sm">
                    Latest AI-generated documentation suggestions
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-1 p-0 overflow-hidden">
                  {suggestionsLoading ? (
                    <div className="flex items-center justify-center h-full">
                      <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full"></div>
                    </div>
                  ) : suggestions.length === 0 ? (
                    <div className="text-center text-muted-foreground h-full flex items-center justify-center">
                      <div>
                        <Lightbulb className="h-12 w-12 mx-auto mb-2 opacity-50" />
                        <p>No suggestions yet</p>
                        <p className="text-sm">Generate suggestions to see them here</p>
                      </div>
                    </div>
                  ) : (
                    <div className="h-full overflow-y-auto scrollbar-thin scroll-smooth will-change-scroll">
                      <div className="p-4">
                        <SuggestionList
                          suggestions={suggestions}
                          onSuggestionSelect={handleSuggestionSelect}
                          onSuggestionApprove={(id) => approveSuggestionMutation.mutate(id)}
                          onSuggestionReject={(id) => rejectSuggestionMutation.mutate(id)}
                          loading={false}
                        />
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;