import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"
import { LucideIcon } from "lucide-react"

interface NavItemProps {
    view: "home" | "emails" | "settings";
    icon: LucideIcon;
    label: string;
    activeView: "home" | "emails" | "settings";
    setActiveView: (view: "home" | "emails" | "settings") => void;
    isCollapsed: boolean;
}

export function NavItem({ view, icon: Icon, label, activeView, setActiveView, isCollapsed }: NavItemProps) {
    const isActive = activeView === view;
    return (
        <TooltipProvider delayDuration={0}>
            <Tooltip>
                <TooltipTrigger asChild>
                    <Button
                        variant="ghost"
                        className={cn(
                            "w-full justify-start h-12 mb-2 transition-all duration-300 relative overflow-hidden",
                            isCollapsed ? "justify-center px-0" : "px-4",
                            isActive
                                ? "bg-gradient-to-r from-blue-500/10 to-cyan-500/10 text-primary border border-blue-500/20 shadow-[0_0_20px_rgba(37,99,235,0.15)] font-semibold"
                                : "text-muted-foreground hover:text-primary hover:bg-primary/5"
                        )}
                        onClick={() => setActiveView(view)}
                    >
                        <Icon className={cn("h-5 w-5 z-10", isCollapsed ? "mr-0" : "mr-3", isActive && "text-primary fill-primary/10")} />
                        {!isCollapsed && <span className="z-10">{label}</span>}
                        {isActive && <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary rounded-r-full" />}
                    </Button>
                </TooltipTrigger>
                {isCollapsed && <TooltipContent side="right" className="glass border-white/20 text-primary font-medium">{label}</TooltipContent>}
            </Tooltip>
        </TooltipProvider>
    );
}
