'use client';

import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { apiService } from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, FileText, Clock, Tag } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { MarkdownContent } from '@/components/ui/markdown-content';

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

interface DocumentDetailPageProps {
  params: { id: string };
}

function DocumentDetailPage({ params }: DocumentDetailPageProps) {
  const router = useRouter();
  const documentId = params.id;

  const { data: document, isLoading, error } = useQuery({
    queryKey: ['document', documentId],
    queryFn: () => apiService.getDocument(documentId),
    enabled: !!documentId,
  });

  const { data: sections = [] } = useQuery({
    queryKey: ['document-sections', documentId],
    queryFn: () => apiService.getDocumentSections(documentId),
    enabled: !!documentId,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-muted rounded w-1/4 mb-4"></div>
            <div className="h-12 bg-muted rounded w-3/4 mb-6"></div>
            <div className="space-y-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="h-4 bg-muted rounded w-full"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="min-h-screen bg-background">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <Button variant="ghost" onClick={() => router.back()} className="mb-6">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <Card>
            <CardContent className="pt-6">
              <p className="text-destructive">
                Error loading document: {error?.message || 'Document not found'}
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };


  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" onClick={() => router.push('/')} size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Home
              </Button>
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                <span className="font-medium text-muted-foreground">Documentation</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">
                {sections.length} sections
              </Badge>
              <Badge variant="outline">
                v{document.version}
              </Badge>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto flex">
        {/* Sidebar */}
        <aside className="w-64 min-h-screen border-r bg-card/50 p-6">
          <div className="space-y-4">
            <div>
              <h3 className="font-medium text-sm text-muted-foreground uppercase tracking-wide mb-3">
                Document Info
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span>Updated {formatDate(document.updated_at)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Tag className="h-4 w-4 text-muted-foreground" />
                  <span>{document.sections_count} sections</span>
                </div>
              </div>
            </div>

            {sections.length > 0 && (
              <div>
                <h3 className="font-medium text-sm text-muted-foreground uppercase tracking-wide mb-3">
                  Table of Contents
                </h3>
                <nav className="space-y-1">
                  {sections.slice(0, 10).map((section, index) => (
                    <a
                      key={section.id}
                      href={`#section-${index}`}
                      className="block text-sm text-muted-foreground hover:text-foreground transition-colors py-1 px-2 rounded hover:bg-muted/50"
                    >
                      {section.title.length > 40 
                        ? `${section.title.substring(0, 40)}...` 
                        : section.title}
                    </a>
                  ))}
                  {sections.length > 10 && (
                    <span className="text-xs text-muted-foreground px-2">
                      +{sections.length - 10} more sections
                    </span>
                  )}
                </nav>
              </div>
            )}
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8">
          <article className="max-w-4xl">
            {/* Document metadata */}
            <div className="mb-6 pb-6 border-b">
              <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                <span>{document.metadata?.sourceURL || document.file_path}</span>
              </div>
            </div>

            {/* Document content */}
            <div className="space-y-6">
              {document.content ? (
                <MarkdownContent content={document.content} />
              ) : (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No content available for this document.</p>
                </div>
              )}
            </div>

            {/* Document sections */}
            {sections.length > 0 && (
              <div className="mt-12 pt-8 border-t">
                <h2 className="text-2xl font-semibold mb-6">Document Sections</h2>
                <div className="grid gap-4">
                  {sections.slice(0, 5).map((section, index) => (
                    <Card key={section.id} id={`section-${index}`} className="hover:shadow-md transition-shadow">
                      <CardHeader>
                        <CardTitle className="text-lg">{section.title}</CardTitle>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>Lines {section.line_start}-{section.line_end}</span>
                          <Badge variant="outline">{section.section_type}</Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <pre className="whitespace-pre-wrap text-sm bg-muted/50 p-4 rounded max-h-48 overflow-y-auto">
                          {section.content.substring(0, 500)}
                          {section.content.length > 500 && '...'}
                        </pre>
                      </CardContent>
                    </Card>
                  ))}
                  {sections.length > 5 && (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      +{sections.length - 5} more sections available
                    </p>
                  )}
                </div>
              </div>
            )}
          </article>
        </main>
      </div>
    </div>
  );
}

export default function DocumentDetail({ params }: DocumentDetailPageProps) {
  return <DocumentDetailPage params={params} />;
}