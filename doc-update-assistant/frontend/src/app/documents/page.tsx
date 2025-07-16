'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { apiService } from '@/services/api';
import { Document, AppError } from '@/types';
import { DocumentNav } from '@/components/documents/document-nav';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { FileText, ArrowLeft } from 'lucide-react';

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

function DocumentsPage() {
  const router = useRouter();
  // Fetch documents
  const { data: documents = [], isLoading, error } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      console.log('DOCUMENTS DEBUG: Starting to fetch documents...');
      try {
        const result = await apiService.getDocuments();
        console.log('DOCUMENTS DEBUG: Fetched documents:', result.length);
        return result;
      } catch (error) {
        console.error('DOCUMENTS DEBUG: Error fetching documents:', error);
        throw error;
      }
    },
  });

  console.log('DOCUMENTS DEBUG: Query state:', { isLoading, error, documentsCount: documents.length });

  const handleDocumentSelect = (document: Document) => {
    router.push(`/documents/${document.id}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
          <p className="mt-4 text-lg">Loading documents...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">Error Loading Documents</h1>
          <p className="mt-2 text-gray-600">{getErrorMessage(error)}</p>
          <Button onClick={() => window.location.reload()} className="mt-4">
            Retry
          </Button>
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
              <Button variant="ghost" size="sm" onClick={() => router.push('/')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div className="flex items-center gap-2">
                <FileText className="h-6 w-6 text-primary" />
                <h1 className="text-xl font-bold">Documents</h1>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">
                {documents.length} documents loaded
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 h-[calc(100vh-140px)]">
        <Card className="h-full flex flex-col shadow-sm">
          <CardHeader className="pb-3 border-b bg-slate-50/50 rounded-t-lg">
            <CardTitle className="flex items-center gap-2 text-lg">
              <FileText className="h-5 w-5" />
              All Documents ({documents.length})
            </CardTitle>
            <CardDescription>
              Browse through all available documentation
            </CardDescription>
          </CardHeader>
          
          <CardContent className="flex-1 p-0 overflow-hidden">
            {error && (
              <div className="p-4 border-b bg-red-50">
                <p className="text-destructive text-sm">
                  Error loading documents: {getErrorMessage(error)}
                </p>
              </div>
            )}

            {isLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full"></div>
              </div>
            ) : documents.length === 0 ? (
              <div className="text-center text-muted-foreground h-full flex items-center justify-center">
                <div>
                  <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>No documents available</p>
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
      </main>
    </div>
  );
}

export default DocumentsPage;