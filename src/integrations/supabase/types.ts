export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.1"
  }
  public: {
    Tables: {
      tender_analysis: {
        Row: {
          analysis_cost: number | null
          analysis_data: Json
          created_at: string
          id: string
          model_used: string | null
          tender_id: string
          tokens_used: number | null
        }
        Insert: {
          analysis_cost?: number | null
          analysis_data?: Json
          created_at?: string
          id?: string
          model_used?: string | null
          tender_id: string
          tokens_used?: number | null
        }
        Update: {
          analysis_cost?: number | null
          analysis_data?: Json
          created_at?: string
          id?: string
          model_used?: string | null
          tender_id?: string
          tokens_used?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "tender_analysis_tender_id_fkey"
            columns: ["tender_id"]
            isOneToOne: false
            referencedRelation: "tenders"
            referencedColumns: ["id"]
          },
        ]
      }
      tender_chats: {
        Row: {
          ai_response: string | null
          created_at: string
          detected_language: string | null
          id: string
          tender_id: string
          user_message: string
        }
        Insert: {
          ai_response?: string | null
          created_at?: string
          detected_language?: string | null
          id?: string
          tender_id: string
          user_message: string
        }
        Update: {
          ai_response?: string | null
          created_at?: string
          detected_language?: string | null
          id?: string
          tender_id?: string
          user_message?: string
        }
        Relationships: [
          {
            foreignKeyName: "tender_chats_tender_id_fkey"
            columns: ["tender_id"]
            isOneToOne: false
            referencedRelation: "tenders"
            referencedColumns: ["id"]
          },
        ]
      }
      tender_documents: {
        Row: {
          created_at: string
          document_type: Database["public"]["Enums"]["document_type"]
          extracted_text: string | null
          extraction_method: string | null
          id: string
          is_annex_override: boolean | null
          original_filename: string | null
          page_count: number | null
          source_date: string | null
          tender_id: string
        }
        Insert: {
          created_at?: string
          document_type: Database["public"]["Enums"]["document_type"]
          extracted_text?: string | null
          extraction_method?: string | null
          id?: string
          is_annex_override?: boolean | null
          original_filename?: string | null
          page_count?: number | null
          source_date?: string | null
          tender_id: string
        }
        Update: {
          created_at?: string
          document_type?: Database["public"]["Enums"]["document_type"]
          extracted_text?: string | null
          extraction_method?: string | null
          id?: string
          is_annex_override?: boolean | null
          original_filename?: string | null
          page_count?: number | null
          source_date?: string | null
          tender_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "tender_documents_tender_id_fkey"
            columns: ["tender_id"]
            isOneToOne: false
            referencedRelation: "tenders"
            referencedColumns: ["id"]
          },
        ]
      }
      tender_lots: {
        Row: {
          caution_provisoire: number | null
          created_at: string
          id: string
          lot_estimated_value: number | null
          lot_number: number
          lot_subject: string | null
          tender_id: string
        }
        Insert: {
          caution_provisoire?: number | null
          created_at?: string
          id?: string
          lot_estimated_value?: number | null
          lot_number: number
          lot_subject?: string | null
          tender_id: string
        }
        Update: {
          caution_provisoire?: number | null
          created_at?: string
          id?: string
          lot_estimated_value?: number | null
          lot_number?: number
          lot_subject?: string | null
          tender_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "tender_lots_tender_id_fkey"
            columns: ["tender_id"]
            isOneToOne: false
            referencedRelation: "tenders"
            referencedColumns: ["id"]
          },
        ]
      }
      tenders: {
        Row: {
          created_at: string
          deadline_source: string | null
          deadline_source_date: string | null
          error_message: string | null
          folder_opening_location: string | null
          id: string
          issuing_institution: string | null
          keywords_ar: string[] | null
          keywords_en: string[] | null
          keywords_fr: string[] | null
          reference_tender: string | null
          reference_url: string
          scrape_date: string
          scraped_at: string
          status: Database["public"]["Enums"]["tender_status"]
          subject: string | null
          submission_deadline_date: string | null
          submission_deadline_time: string | null
          tender_type: Database["public"]["Enums"]["tender_type"] | null
          total_estimated_value: number | null
          updated_at: string
        }
        Insert: {
          created_at?: string
          deadline_source?: string | null
          deadline_source_date?: string | null
          error_message?: string | null
          folder_opening_location?: string | null
          id?: string
          issuing_institution?: string | null
          keywords_ar?: string[] | null
          keywords_en?: string[] | null
          keywords_fr?: string[] | null
          reference_tender?: string | null
          reference_url: string
          scrape_date: string
          scraped_at?: string
          status?: Database["public"]["Enums"]["tender_status"]
          subject?: string | null
          submission_deadline_date?: string | null
          submission_deadline_time?: string | null
          tender_type?: Database["public"]["Enums"]["tender_type"] | null
          total_estimated_value?: number | null
          updated_at?: string
        }
        Update: {
          created_at?: string
          deadline_source?: string | null
          deadline_source_date?: string | null
          error_message?: string | null
          folder_opening_location?: string | null
          id?: string
          issuing_institution?: string | null
          keywords_ar?: string[] | null
          keywords_en?: string[] | null
          keywords_fr?: string[] | null
          reference_tender?: string | null
          reference_url?: string
          scrape_date?: string
          scraped_at?: string
          status?: Database["public"]["Enums"]["tender_status"]
          subject?: string | null
          submission_deadline_date?: string | null
          submission_deadline_time?: string | null
          tender_type?: Database["public"]["Enums"]["tender_type"] | null
          total_estimated_value?: number | null
          updated_at?: string
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      search_tenders: {
        Args: { search_query: string }
        Returns: {
          created_at: string
          deadline_source: string | null
          deadline_source_date: string | null
          error_message: string | null
          folder_opening_location: string | null
          id: string
          issuing_institution: string | null
          keywords_ar: string[] | null
          keywords_en: string[] | null
          keywords_fr: string[] | null
          reference_tender: string | null
          reference_url: string
          scrape_date: string
          scraped_at: string
          status: Database["public"]["Enums"]["tender_status"]
          subject: string | null
          submission_deadline_date: string | null
          submission_deadline_time: string | null
          tender_type: Database["public"]["Enums"]["tender_type"] | null
          total_estimated_value: number | null
          updated_at: string
        }[]
        SetofOptions: {
          from: "*"
          to: "tenders"
          isOneToOne: false
          isSetofReturn: true
        }
      }
    }
    Enums: {
      document_type: "AVIS" | "RC" | "CPS" | "ANNEXE" | "OTHER"
      tender_status: "SCRAPED" | "LISTED" | "ANALYZED" | "ERROR"
      tender_type: "AOON" | "AOOI"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      document_type: ["AVIS", "RC", "CPS", "ANNEXE", "OTHER"],
      tender_status: ["SCRAPED", "LISTED", "ANALYZED", "ERROR"],
      tender_type: ["AOON", "AOOI"],
    },
  },
} as const
