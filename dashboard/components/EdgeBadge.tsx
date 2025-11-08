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
    if (edge >= 0.3) return "bg-green-600 text-white hover:bg-green-700";
    if (edge >= 0.1) return "bg-blue-600 text-white hover:bg-blue-700";
    if (edge >= 0) return "border-green-600 text-green-600";
    return "";
  };

  return (
    <Badge variant={getVariant()} className={getColorClass()}>
      {formatPercent(edge)}
    </Badge>
  );
}
