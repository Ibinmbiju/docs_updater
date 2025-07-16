import { Document } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, ExternalLink, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface DocumentNavProps {
  documents: Document[];
  onDocumentSelect: (document: Document) => void;
  loading?: boolean;
}

export function DocumentNav({ documents, onDocumentSelect, loading }: DocumentNavProps) {
  if (loading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="animate-pulse p-4 border rounded-lg">
            <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-muted rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <Card className="text-center py-12">
        <CardContent>
          <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <CardTitle className="text-lg mb-2">No documents available</CardTitle>
          <p className="text-muted-foreground">
            Documents will appear here when loaded from the backend.
          </p>
        </CardContent>
      </Card>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  // Group documents by category/prefix for better organization
  const groupedDocs = documents.reduce((acc, doc) => {
    const category = doc.name.includes(' - ') ? doc.name.split(' - ')[1] || 'General' : 'General';
    if (!acc[category]) acc[category] = [];
    acc[category].push(doc);
    return acc;
  }, {} as Record<string, Document[]>);

  return (
    <div className="space-y-4">
      {Object.entries(groupedDocs).map(([category, categoryDocs]) => (
        <div key={category}>
          <div className="sticky top-0 bg-background/95 backdrop-blur-sm pb-2 mb-3 border-b">
            <h3 className="font-medium text-sm text-muted-foreground uppercase tracking-wide">
              {category}
            </h3>
          </div>
          <div className="space-y-1.5">
            {categoryDocs.map((document) => (
              <div
                key={document.id}
                className="group border rounded-md hover:shadow-sm transition-all hover:border-primary/30 bg-card hover:bg-accent/5 cursor-pointer"
                onClick={() => onDocumentSelect(document)}
              >
                <div className="p-3">
                  <div className="flex items-start gap-3">
                    <FileText className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                    
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-sm text-foreground group-hover:text-primary transition-colors truncate leading-tight">
                        {document.name.replace(` - ${category}`, '')}
                      </h4>
                      
                      <div className="flex items-center gap-3 mt-1.5 text-xs text-muted-foreground">
                        <Badge variant="secondary" className="text-xs px-1.5 py-0.5 h-5">
                          {document.sections_count}
                        </Badge>
                        
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatDate(document.updated_at)}
                        </span>
                        
                        <span className="text-xs bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded">
                          v{document.version}
                        </span>
                      </div>

                      {document.metadata?.sourceURL && (
                        <div className="mt-2">
                          <a
                            href={document.metadata.sourceURL}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-muted-foreground hover:text-primary flex items-center gap-1 w-fit"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <ExternalLink className="h-3 w-3" />
                            Source
                          </a>
                        </div>
                      )}
                    </div>
                    
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="opacity-0 group-hover:opacity-100 transition-opacity h-7 w-7 p-0 flex-shrink-0"
                      onClick={(e) => {
                        e.stopPropagation();
                        onDocumentSelect(document);
                      }}
                    >
                      <span className="text-xs">→</span>
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}