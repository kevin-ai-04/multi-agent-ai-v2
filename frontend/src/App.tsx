import { useState } from 'react'
import { Sidebar } from "@/components/Sidebar"
import { ChatInterface } from "@/components/ChatInterface"
import { Settings } from "@/components/Settings"
import "@/index.css"

function App() {
    const [agentAEnabled, setAgentAEnabled] = useState(true)
    const [agentBEnabled, setAgentBEnabled] = useState(true)
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
    const [activeView, setActiveView] = useState<"home" | "settings">("home")

    return (
        <div className="flex h-screen w-full overflow-hidden bg-background text-foreground">
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
                <header className="h-14 border-b flex items-center px-6 bg-background/50 backdrop-blur-sm sticky top-0 z-10 justify-between">
                    <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                        {activeView === 'home' ? 'Multi-Agent Number Converter' : 'Settings'}
                    </h1>
                </header>

                <div className="flex-1 overflow-hidden relative">
                    <div className={activeView === 'home' ? 'h-full flex flex-col' : 'hidden'}>
                        <ChatInterface
                            agentAEnabled={agentAEnabled}
                            agentBEnabled={agentBEnabled}
                        />
                    </div>
                    <div className={activeView === 'settings' ? 'h-full overflow-auto' : 'hidden'}>
                        <Settings />
                    </div>
                </div>
            </main>
        </div>
    )
}

export default App
