import { Suggestion, SuggestionFilters } from '@/types';
import { SuggestionCard } from './suggestion-card';
import { SuggestionCarousel } from './suggestion-carousel';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Lightbulb, Filter, Grid3X3, LayoutList } from 'lucide-react';
import { useState } from 'react';

interface SuggestionListProps {
  suggestions: Suggestion[];
  onSuggestionSelect: (suggestion: Suggestion) => void;
  onSuggestionApprove?: (id: string) => void;
  onSuggestionReject?: (id: string) => void;
  filters?: SuggestionFilters;
  onFiltersChange?: (filters: SuggestionFilters) => void;
  loading?: boolean;
}

export function SuggestionList({ 
  suggestions, 
  onSuggestionSelect,
  onSuggestionApprove,
  onSuggestionReject,
  filters,
  onFiltersChange,
  loading 
}: SuggestionListProps) {
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState<'carousel' | 'list'>('carousel');

  if (loading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-muted rounded w-3/4"></div>
              <div className="h-3 bg-muted rounded w-1/2"></div>
            </CardHeader>
            <CardContent>
              <div className="h-3 bg-muted rounded w-full mb-2"></div>
              <div className="h-3 bg-muted rounded w-2/3"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (suggestions.length === 0) {
    return (
      <Card className="text-center py-12">
        <CardContent>
          <Lightbulb className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <CardTitle className="text-lg mb-2">No suggestions found</CardTitle>
          <p className="text-muted-foreground">
            Generate suggestions by analyzing documents or adjust your filters.
          </p>
        </CardContent>
      </Card>
    );
  }

  const statusCounts = suggestions.reduce((acc, suggestion) => {
    acc[suggestion.status] = (acc[suggestion.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="space-y-6">
      {/* Header with stats and filters */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold">
            {suggestions.length} Suggestions
          </h2>
          <div className="flex gap-2">
            {Object.entries(statusCounts).map(([status, count]) => (
              <Badge key={status} variant="outline" className="text-xs">
                {status}: {count}
              </Badge>
            ))}
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button
            variant={viewMode === 'carousel' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('carousel')}
          >
            <LayoutList className="h-4 w-4 mr-2" />
            Carousel
          </Button>
          <Button
            variant={viewMode === 'list' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('list')}
          >
            <Grid3X3 className="h-4 w-4 mr-2" />
            List
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Filter Suggestions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Status</label>
                <select
                  className="w-full p-2 border rounded-md text-sm"
                  value={filters?.status || ''}
                  onChange={(e) => onFiltersChange?.({ 
                    ...filters, 
                    status: e.target.value as any || undefined 
                  })}
                >
                  <option value="">All Statuses</option>
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="rejected">Rejected</option>
                  <option value="merged">Merged</option>
                </select>
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">Type</label>
                <select
                  className="w-full p-2 border rounded-md text-sm"
                  value={filters?.suggestion_type || ''}
                  onChange={(e) => onFiltersChange?.({ 
                    ...filters, 
                    suggestion_type: e.target.value as any || undefined 
                  })}
                >
                  <option value="">All Types</option>
                  <option value="update">Update</option>
                  <option value="add">Add</option>
                  <option value="delete">Delete</option>
                  <option value="move">Move</option>
                </select>
              </div>
              
              <div>
                <label className="text-sm font-medium mb-2 block">Limit</label>
                <select
                  className="w-full p-2 border rounded-md text-sm"
                  value={filters?.limit || 20}
                  onChange={(e) => onFiltersChange?.({ 
                    ...filters, 
                    limit: parseInt(e.target.value) 
                  })}
                >
                  <option value={10}>10 per page</option>
                  <option value={20}>20 per page</option>
                  <option value={50}>50 per page</option>
                  <option value={100}>100 per page</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Suggestions display */}
      {viewMode === 'carousel' ? (
        <SuggestionCarousel
          suggestions={suggestions}
          onSuggestionApprove={onSuggestionApprove}
          onSuggestionReject={onSuggestionReject}
        />
      ) : (
        <div className="space-y-4">
          {suggestions.map((suggestion) => (
            <SuggestionCard
              key={suggestion.id}
              suggestion={suggestion}
              onClick={() => onSuggestionSelect(suggestion)}
              onApprove={onSuggestionApprove}
              onReject={onSuggestionReject}
            />
          ))}
        </div>
      )}
    </div>
  );
}