'use client';

import React, { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { apiService } from '@/services/api';
import { Suggestion, SuggestionFilters } from '@/types';
import { SuggestionList } from '@/components/suggestions/suggestion-list';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Lightbulb, ArrowLeft, Sparkles } from 'lucide-react';

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

// Debounce hook
function useDebouncedValue<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  React.useEffect(() => {
    const handler = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);
  return debounced;
}

function SuggestionsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [generateQuery, setGenerateQuery] = useState('');
  const [filters, setFilters] = useState<SuggestionFilters>({});
  const debouncedFilters = useDebouncedValue(filters, 200);

  // Fetch suggestions
  const { data: suggestions = [], isLoading, error } = useQuery({
    queryKey: ['suggestions', debouncedFilters],
    queryFn: () => apiService.getSuggestions(debouncedFilters),
    placeholderData: keepPreviousData,
  });

  // Generate suggestions mutation
  const generateSuggestionsMutation = useMutation({
    mutationFn: (query: string) => apiService.generateSuggestions({ query, limit: 10 }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suggestions'] });
      setGenerateQuery('');
    },
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

  const handleSuggestionSelect = (suggestion: Suggestion) => {
    router.push(`/suggestions/${suggestion.id}`);
  };

  const handleFiltersChange = (newFilters: SuggestionFilters) => {
    setFilters(newFilters);
  };

  // Memoize SuggestionList to avoid unnecessary re-renders
  const MemoizedSuggestionList = useMemo(() => React.memo(SuggestionList), []);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b bg-card shadow-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => router.push('/')}
              className="flex items-center gap-1">
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back
            </Button>
            <div className="flex items-center gap-2">
              <Lightbulb className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-bold">Suggestions</h1>
            </div>
          </div>
          <div className="flex items-center gap-2 mt-2 md:mt-0">
            <span className="text-sm text-muted-foreground">
              {suggestions.length} suggestions
            </span>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 h-[calc(100vh-140px)]">
        <div className="h-full flex flex-col gap-4 max-w-6xl mx-auto">
          {/* Generate Suggestions Section - Fixed Height */}
          <Card className="flex-shrink-0 shadow-sm">
            <CardHeader className="pb-3 border-b bg-slate-50/50 rounded-t-lg">
              <CardTitle className="flex items-center gap-2 text-base">
                <Sparkles className="h-4 w-4" />
                Generate New Suggestions
              </CardTitle>
              <CardDescription className="text-sm">
                Describe what needs to be updated in your documentation and AI will generate specific suggestions.
              </CardDescription>
            </CardHeader>
            <CardContent className="p-4">
              <div className="flex flex-col gap-2 md:flex-row md:gap-4">
                <Input
                  placeholder="Describe what needs to be updated (e.g., 'Update API endpoints for v2.0' or 'Add authentication examples')..."
                  value={generateQuery}
                  onChange={(e) => setGenerateQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleGenerateSuggestions()}
                  className="flex-1 min-w-0"
                />
                <Button 
                  onClick={handleGenerateSuggestions}
                  disabled={generateSuggestionsMutation.isPending || !generateQuery.trim()}
                  className="w-full md:w-auto"
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

          {/* Suggestions List - Scrollable */}
          <Card className="flex-1 flex flex-col shadow-sm">
            <CardHeader className="pb-3 border-b bg-slate-50/50 rounded-t-lg">
              <CardTitle className="flex items-center gap-2 text-base">
                <Lightbulb className="h-4 w-4" />
                All Suggestions ({suggestions.length})
              </CardTitle>
              <CardDescription className="text-sm">
                Browse and manage all documentation suggestions
              </CardDescription>
            </CardHeader>
            
            <CardContent className="flex-1 p-0 overflow-hidden">
              {error && (
                <div className="p-4 border-b bg-red-50">
                  <p className="text-destructive text-sm">
                    Error loading suggestions: {getErrorMessage(error)}
                  </p>
                </div>
              )}

              {isLoading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full"></div>
                </div>
              ) : suggestions.length === 0 ? (
                <div className="text-center text-muted-foreground h-full flex items-center justify-center">
                  <div>
                    <Lightbulb className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>No suggestions available</p>
                    <p className="text-sm">Generate suggestions to see them here</p>
                  </div>
                </div>
              ) : (
                <div className="h-full overflow-y-auto scrollbar-thin scroll-smooth will-change-scroll">
                  <div className="p-4">
                    <MemoizedSuggestionList
                      suggestions={suggestions}
                      onSuggestionSelect={handleSuggestionSelect}
                      onSuggestionApprove={(id) => approveSuggestionMutation.mutate(id)}
                      onSuggestionReject={(id) => rejectSuggestionMutation.mutate(id)}
                      filters={filters}
                      onFiltersChange={handleFiltersChange}
                      loading={false}
                    />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

export default SuggestionsPage;