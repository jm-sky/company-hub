import { AlertCircle, CheckCircle } from "lucide-react";
import { Badge } from "./badge";

export function StatusBadge({ status, label }: { status: string, label: string }) {
  return (
    <Badge variant={status === "success" ? "success" : "outline"} className="text-xs flex items-center gap-2">
      {status === "success" ? <CheckCircle className="size-4" /> : <AlertCircle className="size-4" />}
      {label}
    </Badge>
  )
}
