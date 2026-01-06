import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { format } from "date-fns";
import { Button } from "@/components/ui/button";
import { AskAI } from "@/components/AskAI";

type Tender = {
  id: string;
  reference_url: string;
  reference_tender: string | null;
  subject: string | null;
  issuing_institution: string | null;
  tender_type: string | null;
  status: string;
  scrape_date: string;
  submission_deadline_date: string | null;
  submission_deadline_time: string | null;
  total_estimated_value: number | null;
  keywords_fr: string[];
};

type TenderDetailProps = {
  tender: Tender;
};

export function TenderDetail({ tender }: TenderDetailProps) {
  const [activeTab, setActiveTab] = useState<"info" | "documents" | "ask">("info");

  const { data: documents } = useQuery({
    queryKey: ["tender-documents", tender.id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("tender_documents")
        .select("*")
        .eq("tender_id", tender.id);
      if (error) throw error;
      return data;
    },
  });

  const { data: lots } = useQuery({
    queryKey: ["tender-lots", tender.id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("tender_lots")
        .select("*")
        .eq("tender_id", tender.id)
        .order("lot_number");
      if (error) throw error;
      return data;
    },
  });

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-border p-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs text-primary font-mono">
              {tender.reference_tender || "NO-REF"}
            </p>
            <h2 className="text-lg font-medium mt-1">{tender.subject || "No subject"}</h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              {tender.issuing_institution}
            </p>
          </div>
          <a
            href={tender.reference_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-primary hover:underline"
          >
            VIEW SOURCE →
          </a>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mt-4">
          {(["info", "documents", "ask"] as const).map((tab) => (
            <Button
              key={tab}
              variant={activeTab === tab ? "default" : "outline"}
              size="sm"
              onClick={() => setActiveTab(tab)}
              className="text-xs uppercase"
            >
              {tab === "ask" ? "Ask AI" : tab}
            </Button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === "info" && (
          <div className="space-y-6">
            {/* Key Info Grid */}
            <div className="grid grid-cols-2 gap-4">
              <InfoCard label="TYPE" value={tender.tender_type || "—"} />
              <InfoCard label="STATUS" value={tender.status} />
              <InfoCard
                label="DEADLINE"
                value={
                  tender.submission_deadline_date
                    ? `${format(new Date(tender.submission_deadline_date), "dd/MM/yyyy")} ${tender.submission_deadline_time || ""}`
                    : "—"
                }
              />
              <InfoCard
                label="ESTIMATED VALUE"
                value={
                  tender.total_estimated_value
                    ? `${tender.total_estimated_value.toLocaleString()} MAD`
                    : "—"
                }
              />
              <InfoCard
                label="SCRAPED"
                value={format(new Date(tender.scrape_date), "dd/MM/yyyy")}
              />
            </div>

            {/* Keywords */}
            {tender.keywords_fr && tender.keywords_fr.length > 0 && (
              <div>
                <p className="text-xs text-muted-foreground mb-2">KEYWORDS</p>
                <div className="flex flex-wrap gap-1">
                  {tender.keywords_fr.map((kw, i) => (
                    <span
                      key={i}
                      className="text-xs bg-secondary px-2 py-0.5 rounded"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Lots */}
            {lots && lots.length > 0 && (
              <div>
                <p className="text-xs text-muted-foreground mb-2">
                  LOTS ({lots.length})
                </p>
                <div className="space-y-2">
                  {lots.map((lot) => (
                    <div
                      key={lot.id}
                      className="bg-secondary/50 rounded p-3 text-sm"
                    >
                      <div className="flex justify-between">
                        <span className="text-primary">Lot {lot.lot_number}</span>
                        {lot.lot_estimated_value && (
                          <span className="text-muted-foreground">
                            {lot.lot_estimated_value.toLocaleString()} MAD
                          </span>
                        )}
                      </div>
                      <p className="mt-1">{lot.lot_subject}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "documents" && (
          <div className="space-y-3">
            {documents && documents.length > 0 ? (
              documents.map((doc) => (
                <div
                  key={doc.id}
                  className="bg-secondary/50 rounded p-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-primary font-mono">
                      {doc.document_type}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {doc.page_count} pages • {doc.extraction_method}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {doc.original_filename}
                  </p>
                  {doc.extracted_text && (
                    <pre className="mt-2 text-xs bg-background p-2 rounded max-h-40 overflow-auto whitespace-pre-wrap">
                      {doc.extracted_text.slice(0, 500)}...
                    </pre>
                  )}
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground text-center py-8">
                No documents extracted yet.
                <br />
                <span className="text-xs">Run the extraction pipeline.</span>
              </p>
            )}
          </div>
        )}

        {activeTab === "ask" && <AskAI tenderId={tender.id} />}
      </div>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-secondary/30 rounded p-3">
      <p className="text-[10px] text-muted-foreground">{label}</p>
      <p className="text-sm font-mono mt-0.5">{value}</p>
    </div>
  );
}
