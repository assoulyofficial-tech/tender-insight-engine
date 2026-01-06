import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send } from "lucide-react";

type AskAIProps = {
  tenderId: string;
};

export function AskAI({ tenderId }: AskAIProps) {
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || isLoading) return;

    const userMessage = question.trim();
    setQuestion("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    // TODO: Integrate with DeepSeek API via Python backend
    // For now, show placeholder
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "AI response will be integrated with the Python backend. Connect your DeepSeek API key and run the backend server.",
        },
      ]);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-auto space-y-3">
        {messages.length === 0 ? (
          <div className="text-center text-muted-foreground text-sm py-8">
            <p>Ask questions about this tender</p>
            <p className="text-xs mt-1 opacity-50">
              Supports French & Moroccan Darija
            </p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              key={i}
              className={`p-3 rounded text-sm ${
                msg.role === "user"
                  ? "bg-primary/10 text-primary ml-8"
                  : "bg-secondary mr-8"
              }`}
            >
              <p className="text-[10px] text-muted-foreground mb-1 uppercase">
                {msg.role}
              </p>
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          ))
        )}
        {isLoading && (
          <div className="bg-secondary p-3 rounded mr-8">
            <p className="text-[10px] text-muted-foreground mb-1">ASSISTANT</p>
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" />
              <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce delay-100" />
              <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce delay-200" />
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
        <Textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask about this tender..."
          className="resize-none h-20 bg-secondary border-border"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <Button
          type="submit"
          disabled={!question.trim() || isLoading}
          size="icon"
          className="h-20 w-12"
        >
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  );
}
