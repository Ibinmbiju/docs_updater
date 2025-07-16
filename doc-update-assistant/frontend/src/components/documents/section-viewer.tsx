import { DocumentSection } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { getFileLanguage } from '@/lib/utils';

interface SectionViewerProps {
  section: DocumentSection;
  showLineNumbers?: boolean;
  highlightSyntax?: boolean;
}

export function SectionViewer({ 
  section, 
  showLineNumbers = false, 
  highlightSyntax = true 
}: SectionViewerProps) {
  const language = getFileLanguage(section.file_path);

  const renderContent = () => {
    if (section.section_type === 'code' && highlightSyntax) {
      return (
        <pre className="bg-muted p-4 rounded-md overflow-x-auto text-sm">
          <code className={`language-${language}`}>
            {section.content}
          </code>
        </pre>
      );
    }

    const lines = section.content.split('\n');
    
    return (
      <div className="space-y-1">
        {lines.map((line, index) => (
          <div key={index} className="flex text-sm">
            {showLineNumbers && (
              <span className="text-muted-foreground w-8 text-right mr-4 select-none">
                {section.line_start + index}
              </span>
            )}
            <span className="flex-1 whitespace-pre-wrap">{line || ' '}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{section.title}</CardTitle>
          <div className="flex gap-2">
            <Badge variant="outline" className="capitalize">
              {section.section_type}
            </Badge>
            <Badge variant="secondary" className="text-xs">
              Lines {section.line_start}-{section.line_end}
            </Badge>
          </div>
        </div>
        <p className="text-sm text-muted-foreground truncate">
          {section.file_path}
        </p>
      </CardHeader>
      <CardContent>
        <div className="max-h-96 overflow-y-auto">
          {renderContent()}
        </div>
      </CardContent>
    </Card>
  );
}