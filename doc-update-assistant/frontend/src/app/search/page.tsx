'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { apiService } from '@/services/api';
import { DocumentSection } from '@/types';
import { SectionViewer } from '@/components/documents/section-viewer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search as SearchIcon, ArrowLeft, FileText, Code, Type } from 'lucide-react';

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

function SearchPage() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Search sections
  const { data: searchResults, isLoading, error } = useQuery({
    queryKey: ['search', searchQuery],
    queryFn: () => apiService.searchSections({ query: searchQuery, limit: 50 }),
    enabled: !!searchQuery,
  });

  const handleSearch = () => {
    if (query.trim()) {
      setSearchQuery(query.trim());
    }
  };

  const clearSearch = () => {
    setQuery('');
    setSearchQuery('');
  };

  const getSectionIcon = (sectionType: string) => {
    switch (sectionType) {
      case 'code':
        return <Code className="h-4 w-4" />;
      case 'markdown':
        return <FileText className="h-4 w-4" />;
      default:
        return <Type className="h-4 w-4" />;
    }
  };

  const getSectionTypeColor = (sectionType: string) => {
    switch (sectionType) {
      case 'code':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'markdown':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => router.push('/')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div className="flex items-center gap-2">
                <SearchIcon className="h-6 w-6 text-primary" />
                <h1 className="text-xl font-bold">Search</h1>
              </div>
            </div>
            {searchResults && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">
                  {searchResults.total_results} results found
                </span>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Search Section */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <SearchIcon className="h-5 w-5" />
              Search Documentation
            </CardTitle>
            <CardDescription>
              Search across all loaded documents and sections for specific content, keywords, or concepts.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Input
                placeholder="Search for content, keywords, or concepts..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="flex-1"
              />
              <Button 
                onClick={handleSearch}
                disabled={isLoading || !query.trim()}
              >
                {isLoading ? 'Searching...' : 'Search'}
              </Button>
              {searchQuery && (
                <Button variant="outline" onClick={clearSearch}>
                  Clear
                </Button>
              )}
            </div>
            {searchQuery && (
              <p className="text-sm text-muted-foreground mt-2">
                Searching for: <strong>"{searchQuery}"</strong>
              </p>
            )}
          </CardContent>
        </Card>

        {/* Error handling */}
        {error && (
          <Card className="mb-8">
            <CardContent className="pt-6">
              <p className="text-destructive">
                Error performing search: {getErrorMessage(error)}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Search Results */}
        {searchResults && (
          <div className="space-y-6">
            {/* Results Header */}
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">
                Search Results ({searchResults.total_results})
              </h2>
              {searchResults.results.length > 0 && (
                <div className="flex gap-2">
                  {['code', 'markdown', 'text'].map(type => {
                    const count = searchResults.results.filter(r => r.section_type === type).length;
                    if (count === 0) return null;
                    return (
                      <Badge
                        key={type}
                        variant="outline"
                        className={`text-xs ${getSectionTypeColor(type)}`}
                      >
                        {getSectionIcon(type)}
                        <span className="ml-1">{type}: {count}</span>
                      </Badge>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Results List */}
            {searchResults.results.length === 0 ? (
              <Card className="text-center py-12">
                <CardContent>
                  <SearchIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <CardTitle className="text-lg mb-2">No results found</CardTitle>
                  <p className="text-muted-foreground">
                    Try different keywords or check if documents are loaded.
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {searchResults.results.map((section) => (
                  <Card key={section.id} className="overflow-hidden">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            {getSectionIcon(section.section_type)}
                            <CardTitle className="text-lg">{section.title}</CardTitle>
                          </div>
                          <CardDescription className="text-sm truncate">
                            {section.file_path} (Lines {section.line_start}-{section.line_end})
                          </CardDescription>
                        </div>
                        <Badge className={getSectionTypeColor(section.section_type)}>
                          {section.section_type}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="max-h-40 overflow-y-auto">
                        <SectionViewer 
                          section={section} 
                          showLineNumbers={true}
                          highlightSyntax={section.section_type === 'code'}
                        />
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Initial State */}
        {!searchQuery && !isLoading && (
          <Card className="text-center py-12">
            <CardContent>
              <SearchIcon className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <CardTitle className="text-lg mb-2">Search Documentation</CardTitle>
              <p className="text-muted-foreground mb-4">
                Enter keywords or phrases to search across all loaded documents and sections.
              </p>
              <div className="text-sm text-muted-foreground space-y-1">
                <p><strong>Tips:</strong></p>
                <p>• Use specific keywords for better results</p>
                <p>• Search for function names, API endpoints, or concepts</p>
                <p>• Results include content from all section types</p>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}

export default SearchPage;