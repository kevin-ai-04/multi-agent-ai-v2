import { useState } from 'react'
import { Sidebar } from "@/components/Sidebar"
import { ChatInterface } from "@/components/ChatInterface"
import "@/index.css"

function App() {
    const [agentAEnabled, setAgentAEnabled] = useState(true)
    const [agentBEnabled, setAgentBEnabled] = useState(true)

    return (
        <div className="flex h-screen w-full overflow-hidden bg-background">
            <aside className="w-80 hidden md:block border-r">
                <Sidebar
                    agentAEnabled={agentAEnabled}
                    setAgentAEnabled={setAgentAEnabled}
                    agentBEnabled={agentBEnabled}
                    setAgentBEnabled={setAgentBEnabled}
                />
            </aside>
            <main className="flex-1 flex flex-col h-full">
                <header className="h-14 border-b flex items-center px-6 bg-white/50 backdrop-blur-sm sticky top-0 z-10 justify-between">
                    <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                        Multi-Agent Number Converter
                    </h1>
                </header>
                <div className="flex-1 overflow-hidden relative">
                    <ChatInterface
                        agentAEnabled={agentAEnabled}
                        agentBEnabled={agentBEnabled}
                    />
                </div>
            </main>
        </div>
    )
}

export default App
