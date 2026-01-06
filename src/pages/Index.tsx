import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { TenderList } from "@/components/TenderList";
import { TenderDetail } from "@/components/TenderDetail";
import { SearchBar } from "@/components/SearchBar";
import { StatusBar } from "@/components/StatusBar";

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

const Index = () => {
  const [selectedTenderId, setSelectedTenderId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const { data: tenders, isLoading, error } = useQuery({
    queryKey: ["tenders", searchQuery],
    queryFn: async () => {
      let query = supabase
        .from("tenders")
        .select("*")
        .order("scrape_date", { ascending: false });

      if (searchQuery) {
        query = query.or(
          `subject.ilike.%${searchQuery}%,issuing_institution.ilike.%${searchQuery}%,reference_tender.ilike.%${searchQuery}%`
        );
      }

      const { data, error } = await query.limit(100);
      if (error) throw error;
      return data as Tender[];
    },
  });

  const selectedTender = tenders?.find((t) => t.id === selectedTenderId);

  return (
    <div className="min-h-screen bg-background mono-grid">
      {/* Header */}
      <header className="border-b border-border px-4 py-3">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-primary text-lg">▶</span>
            <h1 className="text-lg font-bold tracking-tight">
              <span className="text-primary">TENDER</span>
              <span className="text-muted-foreground">::</span>
              <span className="text-foreground">AI</span>
            </h1>
          </div>
          <span className="text-xs text-muted-foreground">v1.0</span>
          <div className="flex-1" />
          <StatusBar tenderCount={tenders?.length ?? 0} isLoading={isLoading} />
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-53px)]">
        {/* Left Panel - Tender List */}
        <div className="w-96 border-r border-border flex flex-col">
          <div className="p-3 border-b border-border">
            <SearchBar value={searchQuery} onChange={setSearchQuery} />
          </div>
          <div className="flex-1 overflow-auto">
            {error ? (
              <div className="p-4 text-destructive text-sm">
                Error: {error.message}
              </div>
            ) : (
              <TenderList
                tenders={tenders ?? []}
                isLoading={isLoading}
                selectedId={selectedTenderId}
                onSelect={setSelectedTenderId}
              />
            )}
          </div>
        </div>

        {/* Right Panel - Detail View */}
        <div className="flex-1 overflow-auto">
          {selectedTender ? (
            <TenderDetail tender={selectedTender} />
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <div className="text-center">
                <p className="text-sm">SELECT A TENDER TO VIEW DETAILS</p>
                <p className="text-xs mt-1 opacity-50">← Click on a row</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Index;
