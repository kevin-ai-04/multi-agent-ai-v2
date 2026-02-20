import { useState } from 'react'
import { Sidebar } from "@/components/Sidebar"
import { ChatInterface, Message } from "@/components/ChatInterface"
import { Settings } from "@/components/Settings"
import { EmailPage } from "@/components/EmailPage"
import { Dashboard } from "@/components/Dashboard"
import { DocsPage } from "@/components/DocsPage"
import "@/index.css"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { ChevronDown, Inbox, Send, File, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"

function App() {
    // Agent Configuration State
    const [agentAEnabled, setAgentAEnabled] = useState(true)
    const [agentBEnabled, setAgentBEnabled] = useState(true)

    // UI State
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
    const [activeView, setActiveView] = useState<"home" | "emails" | "settings" | "dashboard" | "docs">("home")
    const [emailFolder, setEmailFolder] = useState("inbox")

    // Chat Session State (Lifted for persistence)
    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState("")
    const [isLoading, setIsLoading] = useState(false)

    const folderMap: Record<string, string> = {
        inbox: "Inbox",
        sent: "Sent",
        drafts: "Drafts",
        trash: "Trash"
    }

    return (
        <div className="flex h-screen w-full overflow-hidden mesh-gradient text-foreground transition-colors duration-500">
            <Sidebar
                agentAEnabled={agentAEnabled}
                setAgentAEnabled={setAgentAEnabled}
                agentBEnabled={agentBEnabled}
                setAgentBEnabled={setAgentBEnabled}
                activeView={activeView}
                setActiveView={setActiveView}
                isCollapsed={isSidebarCollapsed}
                setIsCollapsed={setIsSidebarCollapsed}
            />

            <main className="flex-1 flex flex-col h-full overflow-hidden transition-all duration-300">
                <header className="h-14 border-b border-white/10 flex items-center px-6 bg-background/50 backdrop-blur-sm sticky top-0 z-10 justify-between">
                    <div className="flex items-center gap-2">
                        {activeView === 'emails' ? (
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent hover:bg-transparent hover:text-blue-500 p-0 h-auto flex items-center gap-2">
                                        {folderMap[emailFolder]}
                                        <ChevronDown className="h-5 w-5 text-blue-500" />
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="start" className="w-48 glass border-white/20">
                                    <DropdownMenuItem onClick={() => setEmailFolder("inbox")} className="gap-2 cursor-pointer">
                                        <Inbox className="h-4 w-4" /> Inbox
                                    </DropdownMenuItem>
                                    <DropdownMenuItem onClick={() => setEmailFolder("sent")} className="gap-2 cursor-pointer">
                                        <Send className="h-4 w-4" /> Sent
                                    </DropdownMenuItem>
                                    <DropdownMenuItem onClick={() => setEmailFolder("drafts")} className="gap-2 cursor-pointer">
                                        <File className="h-4 w-4" /> Drafts
                                    </DropdownMenuItem>
                                    <DropdownMenuItem onClick={() => setEmailFolder("trash")} className="gap-2 cursor-pointer text-red-400 focus:text-red-400">
                                        <Trash2 className="h-4 w-4" /> Trash
                                    </DropdownMenuItem>
                                </DropdownMenuContent>
                            </DropdownMenu>
                        ) : (
                            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                                {activeView === 'home' && 'Multi-Agent Number Converter'}
                                {activeView === 'dashboard' && 'Neural Dashboard'}
                                {activeView === 'docs' && 'Documentation'}
                                {activeView === 'settings' && 'Settings'}
                            </h1>
                        )}
                    </div>
                </header>

                <div className="flex-1 overflow-hidden relative flex">
                    {/* Main Content Area */}
                    <div className={`flex-1 overflow-hidden h-full relative transition-all duration-300 ${activeView === 'home' ? 'bg-transparent' : ''}`}>

                        {/* Home View (Chat Full Screen) */}
                        {activeView === 'home' && (
                            <ChatInterface
                                agentAEnabled={agentAEnabled}
                                agentBEnabled={agentBEnabled}
                                messages={messages}
                                setMessages={setMessages}
                                input={input}
                                setInput={setInput}
                                isLoading={isLoading}
                                setIsLoading={setIsLoading}
                            />
                        )}

                        {/* Dashboard View */}
                        {activeView === 'dashboard' && <Dashboard messages={messages} isLoading={isLoading} />}

                        {/* Email View */}
                        {activeView === 'emails' && <EmailPage folder={emailFolder} />}

                        {/* Docs View */}
                        {activeView === 'docs' && <DocsPage />}

                        {/* Settings View */}
                        {activeView === 'settings' && (
                            <div className="h-full overflow-auto">
                                <Settings />
                            </div>
                        )}
                    </div>

                    {/* Persistent Side Chat (Visible only on 'emails' view) */}
                    {activeView === 'emails' && (
                        <div className="w-[450px] border-l border-white/10 bg-white/20 dark:bg-black/20 backdrop-blur-lg flex flex-col transition-all duration-300">
                            <div className="p-3 border-b border-white/10 bg-white/10 dark:bg-black/10 backdrop-blur-md">
                                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Orchestrator</span>
                            </div>
                            <div className="flex-1 overflow-hidden">
                                <ChatInterface
                                    agentAEnabled={agentAEnabled}
                                    agentBEnabled={agentBEnabled}
                                    messages={messages}
                                    setMessages={setMessages}
                                    input={input}
                                    setInput={setInput}
                                    isLoading={isLoading}
                                    setIsLoading={setIsLoading}
                                />
                            </div>
                        </div>
                    )}
                </div>
            </main>
        </div>
    )
}

export default App
