import { Document } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatRelativeTime, getFileLanguage } from '@/lib/utils';
import { FileText, Code, Type } from 'lucide-react';

interface DocumentCardProps {
  document: Document;
  onClick: () => void;
}

const getDocumentIcon = (filePath: string) => {
  const language = getFileLanguage(filePath);
  switch (language) {
    case 'markdown':
      return <FileText className="h-5 w-5" />;
    case 'javascript':
    case 'typescript':
    case 'python':
      return <Code className="h-5 w-5" />;
    default:
      return <Type className="h-5 w-5" />;
  }
};

export function DocumentCard({ document, onClick }: DocumentCardProps) {
  return (
    <Card
      className="cursor-pointer transition-all hover:shadow-md hover:border-primary/50"
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {getDocumentIcon(document.file_path)}
            <CardTitle className="text-lg truncate">{document.name}</CardTitle>
          </div>
          <Badge variant="outline" className="text-xs">
            v{document.version}
          </Badge>
        </div>
        <CardDescription className="truncate">
          {document.file_path}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>{document.sections_count} sections</span>
          <span>{formatRelativeTime(document.updated_at)}</span>
        </div>
        {document.content && (
          <p className="mt-2 text-sm text-muted-foreground line-clamp-2">
            {document.content.substring(0, 100)}...
          </p>
        )}
      </CardContent>
    </Card>
  );
}