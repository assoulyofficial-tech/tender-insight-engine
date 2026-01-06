import { format } from "date-fns";
import { cn } from "@/lib/utils";

type Tender = {
  id: string;
  reference_tender: string | null;
  subject: string | null;
  issuing_institution: string | null;
  status: string;
  scrape_date: string;
  submission_deadline_date: string | null;
};

type TenderListProps = {
  tenders: Tender[];
  isLoading: boolean;
  selectedId: string | null;
  onSelect: (id: string) => void;
};

const statusColors: Record<string, string> = {
  SCRAPED: "bg-accent/20 text-accent",
  LISTED: "bg-primary/20 text-primary",
  ANALYZED: "bg-success/20 text-success",
  ERROR: "bg-destructive/20 text-destructive",
};

export function TenderList({
  tenders,
  isLoading,
  selectedId,
  onSelect,
}: TenderListProps) {
  if (isLoading) {
    return (
      <div className="p-4">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="h-16 bg-secondary/50 rounded mb-2 animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (tenders.length === 0) {
    return (
      <div className="p-4 text-center text-muted-foreground text-sm">
        <p>NO TENDERS FOUND</p>
        <p className="text-xs mt-1 opacity-50">Run the scraper to fetch data</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-border">
      {tenders.map((tender) => (
        <button
          key={tender.id}
          onClick={() => onSelect(tender.id)}
          className={cn(
            "w-full text-left p-3 hover:bg-secondary/50 transition-colors",
            selectedId === tender.id && "bg-secondary"
          )}
        >
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <p className="text-xs font-mono text-primary truncate">
                {tender.reference_tender || "NO-REF"}
              </p>
              <p className="text-sm text-foreground truncate mt-0.5">
                {tender.subject || "No subject"}
              </p>
              <p className="text-xs text-muted-foreground truncate mt-0.5">
                {tender.issuing_institution || "Unknown institution"}
              </p>
            </div>
            <div className="flex flex-col items-end gap-1">
              <span
                className={cn(
                  "text-[10px] px-1.5 py-0.5 rounded font-medium",
                  statusColors[tender.status] || "bg-muted text-muted-foreground"
                )}
              >
                {tender.status}
              </span>
              {tender.submission_deadline_date && (
                <span className="text-[10px] text-muted-foreground">
                  ⏱ {format(new Date(tender.submission_deadline_date), "dd/MM")}
                </span>
              )}
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}
