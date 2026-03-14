import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Switch } from "@/components/ui/switch"
import { cn } from "@/lib/utils"
import { Bot, ChevronLeft, ChevronRight, Home, Settings as SettingsIcon, Mail, LayoutDashboard, Book, Database, PlusCircle, ShoppingCart, TrendingUp } from "lucide-react"
import { NavItem } from "./NavItem"

interface SidebarProps {
    agentNum2TextEnabled: boolean;
    setAgentNum2TextEnabled: (enabled: boolean) => void;
    agentText2NumEnabled: boolean;
    setAgentText2NumEnabled: (enabled: boolean) => void;
    agentEmailEnabled: boolean;
    setAgentEmailEnabled: (enabled: boolean) => void;
    agentComplianceEnabled: boolean;
    setAgentComplianceEnabled: (enabled: boolean) => void;
    agentPdfEnabled: boolean;
    setAgentPdfEnabled: (enabled: boolean) => void;
    agentForecastEnabled: boolean;
    setAgentForecastEnabled: (enabled: boolean) => void;
    activeView: "home" | "emails" | "settings" | "dashboard" | "docs" | "database" | "new_order" | "orders" | "forecast";
    setActiveView: (view: "home" | "emails" | "settings" | "dashboard" | "docs" | "database" | "new_order" | "orders" | "forecast") => void;
    isCollapsed: boolean;
    setIsCollapsed: (collapsed: boolean) => void;
    onNewOrder: () => void;
}

export function Sidebar({
    agentNum2TextEnabled,
    setAgentNum2TextEnabled,
    agentText2NumEnabled,
    setAgentText2NumEnabled,
    agentEmailEnabled,
    setAgentEmailEnabled,
    agentComplianceEnabled,
    setAgentComplianceEnabled,
    agentPdfEnabled,
    setAgentPdfEnabled,
    agentForecastEnabled,
    setAgentForecastEnabled,
    activeView,
    setActiveView,
    isCollapsed,
    setIsCollapsed,
    onNewOrder
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
                        <span className="text-[10px] text-muted-foreground uppercase tracking-widest font-semibold mt-1">v26.03.15-001</span>
                    </div>
                )}
            </div>

            {/* Navigation */}
            <ScrollArea className="flex-1 py-4 px-3">
                <nav className="space-y-2">
                    <Button
                        onClick={onNewOrder}
                        className={cn(
                            "w-full bg-blue-600 hover:bg-blue-500 text-white gap-2 mb-4",
                            isCollapsed ? "px-0 justify-center" : "justify-start px-3"
                        )}
                    >
                        <PlusCircle className="h-5 w-5" />
                        {!isCollapsed && <span>New Order</span>}
                    </Button>
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
                        view="orders"
                        icon={ShoppingCart}
                        label="Orders"
                        activeView={activeView}
                        setActiveView={setActiveView}
                        isCollapsed={isCollapsed}
                    />
                    <NavItem
                        view="forecast"
                        icon={TrendingUp}
                        label="Forecast"
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
                            <h4 className="font-semibold leading-none text-blue-900 dark:text-blue-100">Agent Status</h4>
                            <p className="text-xs text-muted-foreground mt-1">Active Neural Modules</p>
                        </div>
                        <div className="p-4 grid gap-4">
                            <div className="flex items-center justify-between">
                                <label className="text-sm">Num2Text</label>
                                <Switch
                                    checked={agentNum2TextEnabled}
                                    onCheckedChange={setAgentNum2TextEnabled}
                                />
                            </div>
                            <div className="flex items-center justify-between">
                                <label className="text-sm">Text2Num</label>
                                <Switch
                                    checked={agentText2NumEnabled}
                                    onCheckedChange={setAgentText2NumEnabled}
                                />
                            </div>
                            <div className="flex items-center justify-between">
                                <label className="text-sm">Email Analyzer</label>
                                <Switch
                                    checked={agentEmailEnabled}
                                    onCheckedChange={setAgentEmailEnabled}
                                />
                            </div>
                            <div className="flex items-center justify-between">
                                <label className="text-sm">Compliance</label>
                                <Switch
                                    checked={agentComplianceEnabled}
                                    onCheckedChange={setAgentComplianceEnabled}
                                />
                            </div>
                            <div className="flex items-center justify-between">
                                <label className="text-sm">PDF Generator</label>
                                <Switch
                                    checked={agentPdfEnabled}
                                    onCheckedChange={setAgentPdfEnabled}
                                />
                            </div>
                            <div className="flex items-center justify-between">
                                <label className="text-sm">Forecast</label>
                                <Switch
                                    checked={agentForecastEnabled}
                                    onCheckedChange={setAgentForecastEnabled}
                                />
                            </div>
                        </div>
                    </PopoverContent>
                </Popover>
            </div>
        </div>
    )
}
