import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { cn } from "@/lib/utils"
import { Bot, ChevronLeft, ChevronRight, Home, Settings as SettingsIcon } from "lucide-react"

interface SidebarProps {
    agentAEnabled: boolean;
    setAgentAEnabled: (enabled: boolean) => void;
    agentBEnabled: boolean;
    setAgentBEnabled: (enabled: boolean) => void;
    activeView: "home" | "settings";
    setActiveView: (view: "home" | "settings") => void;
    isCollapsed: boolean;
    setIsCollapsed: (collapsed: boolean) => void;
}

export function Sidebar({
    agentAEnabled,
    setAgentAEnabled,
    agentBEnabled,
    setAgentBEnabled,
    activeView,
    setActiveView,
    isCollapsed,
    setIsCollapsed
}: SidebarProps) {

    const toggleCollapse = () => setIsCollapsed(!isCollapsed);

    const NavItem = ({ view, icon: Icon, label }: { view: "home" | "settings", icon: any, label: string }) => (
        <TooltipProvider delayDuration={0}>
            <Tooltip>
                <TooltipTrigger asChild>
                    <Button
                        variant={activeView === view ? "secondary" : "ghost"}
                        className={cn(
                            "w-full justify-start h-12 mb-1",
                            isCollapsed ? "justify-center px-2" : "px-4"
                        )}
                        onClick={() => setActiveView(view)}
                    >
                        <Icon className={cn("h-5 w-5", isCollapsed ? "mr-0" : "mr-3")} />
                        {!isCollapsed && <span>{label}</span>}
                    </Button>
                </TooltipTrigger>
                {isCollapsed && <TooltipContent side="right">{label}</TooltipContent>}
            </Tooltip>
        </TooltipProvider>
    );

    return (
        <div className={cn(
            "relative flex flex-col h-full bg-card border-r transition-all duration-300",
            isCollapsed ? "w-16" : "w-64"
        )}>
            {/* Toggle Button */}
            <Button
                variant="ghost"
                size="icon"
                className="absolute -right-3 top-6 z-20 h-6 w-6 rounded-full border bg-background shadow-md hover:bg-accent"
                onClick={toggleCollapse}
            >
                {isCollapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
            </Button>

            {/* Header / Logo */}
            <div className={cn("flex items-center h-14 border-b px-4", isCollapsed ? "justify-center" : "")}>
                <Bot className="h-6 w-6 text-primary" />
                {!isCollapsed && <span className="ml-2 font-bold truncate">Agent System</span>}
            </div>

            {/* Navigation */}
            <ScrollArea className="flex-1 py-4">
                <nav className="px-2 space-y-1">
                    <NavItem view="home" icon={Home} label="Home" />
                    <NavItem view="settings" icon={SettingsIcon} label="Settings" />
                </nav>
            </ScrollArea>

            {/* Footer / Agent Controls */}
            <div className="p-2 border-t mt-auto">
                <Popover>
                    <PopoverTrigger asChild>
                        <Button variant="outline" className={cn("w-full", isCollapsed ? "px-0 justify-center" : "justify-between")}>
                            {isCollapsed ? <Bot className="h-4 w-4" /> : (
                                <>
                                    <span className="flex items-center">
                                        <Bot className="mr-2 h-4 w-4" />
                                        Agent Controls
                                    </span>
                                    <ChevronRight className="h-4 w-4 opacity-50" />
                                </>
                            )}
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent side="right" className="w-80 ml-2">
                        <div className="grid gap-4">
                            <div className="space-y-2">
                                <h4 className="font-medium leading-none">Agent Configuration</h4>
                                <p className="text-sm text-muted-foreground">Manage active agents.</p>
                            </div>
                            <div className="grid gap-2">
                                <div className="flex items-center justify-between">
                                    <Label htmlFor="agent-a">Num2Text Agent</Label>
                                    <Switch id="agent-a" checked={agentAEnabled} onCheckedChange={setAgentAEnabled} />
                                </div>
                                <div className="flex items-center justify-between">
                                    <Label htmlFor="agent-b">Text2Num Agent</Label>
                                    <Switch id="agent-b" checked={agentBEnabled} onCheckedChange={setAgentBEnabled} />
                                </div>
                            </div>
                        </div>
                    </PopoverContent>
                </Popover>
            </div>
        </div>
    )
}
