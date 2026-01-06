import { Database, Loader2 } from "lucide-react";

type StatusBarProps = {
  tenderCount: number;
  isLoading: boolean;
};

export function StatusBar({ tenderCount, isLoading }: StatusBarProps) {
  return (
    <div className="flex items-center gap-4 text-xs text-muted-foreground">
      <div className="flex items-center gap-1.5">
        <Database className="h-3 w-3" />
        <span>{tenderCount} tenders</span>
      </div>
      {isLoading && (
        <div className="flex items-center gap-1.5 text-primary">
          <Loader2 className="h-3 w-3 animate-spin" />
          <span>Loading...</span>
        </div>
      )}
      <div className="flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
        <span>Connected</span>
      </div>
    </div>
  );
}
