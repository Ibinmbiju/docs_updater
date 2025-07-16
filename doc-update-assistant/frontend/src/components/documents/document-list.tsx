import { Document } from '@/types';
import { DocumentCard } from './document-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText } from 'lucide-react';

interface DocumentListProps {
  documents: Document[];
  onDocumentSelect: (document: Document) => void;
  loading?: boolean;
}

export function DocumentList({ documents, onDocumentSelect, loading }: DocumentListProps) {
  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
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

  if (documents.length === 0) {
    return (
      <Card className="text-center py-12">
        <CardContent>
          <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <CardTitle className="text-lg mb-2">No documents loaded</CardTitle>
          <p className="text-muted-foreground">
            Load documents from files or directories to get started.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {documents.map((document) => (
        <DocumentCard
          key={document.id}
          document={document}
          onClick={() => onDocumentSelect(document)}
        />
      ))}
    </div>
  );
}