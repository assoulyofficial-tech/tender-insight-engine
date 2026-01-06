import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

type SearchBarProps = {
  value: string;
  onChange: (value: string) => void;
};

export function SearchBar({ value, onChange }: SearchBarProps) {
  return (
    <div className="relative">
      <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input
        type="text"
        placeholder="Search tenders..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="pl-9 bg-secondary border-border text-sm h-9"
      />
    </div>
  );
}
