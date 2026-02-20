import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"

import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { cn } from "@/lib/utils"
import { Bot, ChevronLeft, ChevronRight, Home, Settings as SettingsIcon, Mail, LayoutDashboard, Book, Database } from "lucide-react"

import { NavItem } from "./NavItem"

interface SidebarProps {
    agentAEnabled: boolean;
    setAgentAEnabled: (enabled: boolean) => void;
    agentBEnabled: boolean;
    setAgentBEnabled: (enabled: boolean) => void;
    activeView: "home" | "emails" | "settings" | "dashboard" | "docs" | "database";
    setActiveView: (view: "home" | "emails" | "settings" | "dashboard" | "docs" | "database") => void;
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

    return (
        <div className={cn(
            "relative flex flex-col h-full transition-all duration-300 z-20",
            "bg-white/40 dark:bg-black/40 backdrop-blur-xl border-r border-white/20 dark:border-white/10",
            isCollapsed ? "w-20" : "w-72"
        )}>
            {/* Toggle Button */}
            <Button
                variant="ghost"
                size="icon"
                className="absolute -right-3 top-8 z-30 h-6 w-6 rounded-full border border-white/20 bg-white/50 dark:bg-black/50 shadow-md backdrop-blur-sm hover:bg-primary hover:text-white transition-colors"
                onClick={toggleCollapse}
            >
                {isCollapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
            </Button>

            {/* Header / Logo */}
            <div className={cn("flex items-center h-20 px-6 mb-2", isCollapsed ? "justify-center" : "")}>
                <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
                    <Bot className="h-6 w-6 text-white" />
                </div>
                {!isCollapsed && (
                    <div className="ml-3 flex flex-col">
                        <span className="font-bold text-lg leading-none tracking-tight">Procurement<span className="text-primary">Console</span></span>
                        <span className="text-[10px] text-muted-foreground uppercase tracking-widest font-semibold mt-1">v26.02.19-001</span>
                    </div>
                )}
            </div>

            {/* Navigation */}
            <ScrollArea className="flex-1 py-4 px-3">
                <nav className="space-y-2">
                    <NavItem
                        view="home"
                        icon={Home}
                        label="Home"
                        activeView={activeView}
                        setActiveView={setActiveView}
                        isCollapsed={isCollapsed}
                    />
                    <NavItem
                        view="dashboard"
                        icon={LayoutDashboard}
                        label="Dashboard"
                        activeView={activeView}
                        setActiveView={setActiveView}
                        isCollapsed={isCollapsed}
                    />
                    <NavItem
                        view="emails"
                        icon={Mail}
                        label="Emails"
                        activeView={activeView}
                        setActiveView={setActiveView}
                        isCollapsed={isCollapsed}
                    />
                    <NavItem
                        view="docs"
                        icon={Book}
                        label="Docs"
                        activeView={activeView}
                        setActiveView={setActiveView}
                        isCollapsed={isCollapsed}
                    />
                    <NavItem
                        view="database"
                        icon={Database}
                        label="Database"
                        activeView={activeView}
                        setActiveView={setActiveView}
                        isCollapsed={isCollapsed}
                    />
                    <NavItem
                        view="settings"
                        icon={SettingsIcon}
                        label="Settings"
                        activeView={activeView}
                        setActiveView={setActiveView}
                        isCollapsed={isCollapsed}
                    />
                </nav>
            </ScrollArea>

            {/* Footer / Agent Controls */}
            <div className="p-4 mt-auto">
                <Popover>
                    <PopoverTrigger asChild>
                        <Button
                            variant="outline"
                            className={cn(
                                "w-full border-white/20 dark:border-white/10 bg-white/50 dark:bg-black/50 hover:bg-primary/10 hover:border-primary/50 transition-all duration-300",
                                isCollapsed ? "px-0 justify-center aspect-square" : "justify-between h-12"
                            )}
                        >
                            {isCollapsed ? <Bot className="h-5 w-5" /> : (
                                <>
                                    <span className="flex items-center font-medium">
                                        <Bot className="mr-2 h-4 w-4" />
                                        Agents
                                    </span>
                                    <ChevronRight className="h-4 w-4 opacity-50" />
                                </>
                            )}
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent side="right" className="w-80 ml-4 glass border-white/20 p-0 overflow-hidden">
                        <div className="p-4 bg-blue-500/10 border-b border-white/10">
                            <h4 className="font-semibold leading-none">Agent Status</h4>
                            <p className="text-xs text-muted-foreground mt-1">Active Neural Modules</p>
                        </div>
                        <div className="p-4 grid gap-4">
                            <div className="flex items-center justify-between">
                                <Label htmlFor="agent-a" className="font-medium">Num2Text</Label>
                                <Switch id="agent-a" checked={agentAEnabled} onCheckedChange={setAgentAEnabled} />
                            </div>
                            <div className="flex items-center justify-between">
                                <Label htmlFor="agent-b" className="font-medium">Text2Num</Label>
                                <Switch id="agent-b" checked={agentBEnabled} onCheckedChange={setAgentBEnabled} />
                            </div>
                        </div>
                    </PopoverContent>
                </Popover>
            </div>
        </div>
    )
}
