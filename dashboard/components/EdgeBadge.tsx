import { Badge } from "@/components/ui/badge";
import { formatPercent } from "@/lib/utils";

interface EdgeBadgeProps {
  edge: number;
}

export function EdgeBadge({ edge }: EdgeBadgeProps) {
  const getVariant = () => {
    if (edge >= 0.3) return "default";
    if (edge >= 0.1) return "secondary";
    if (edge >= 0) return "outline";
    return "destructive";
  };

  const getColorClass = () => {
    if (edge >= 0.3) return "bg-purple-600 text-white hover:bg-purple-700";
    if (edge >= 0.1) return "bg-blue-600 text-white hover:bg-blue-700";
    if (edge >= 0) return "border-purple-600 text-purple-600";
    return "";
  };

  return (
    <Badge variant={getVariant()} className={getColorClass()}>
      {formatPercent(edge)}
    </Badge>
  );
}
