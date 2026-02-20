import { ScrollArea } from "@/components/ui/scroll-area";
import { Card } from "@/components/ui/card";
import { Bot, Network, Mail, Database, Terminal } from "lucide-react";

export function DocsPage() {
    return (
        <div className="h-full flex flex-col bg-white/30 dark:bg-black/20 backdrop-blur-md">
            {/* Header */}
            <div className="h-16 border-b border-white/20 px-8 flex items-center bg-white/40 dark:bg-black/40">
                <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                    System Documentation
                </h2>
            </div>

            <ScrollArea className="flex-1 p-8">
                <div className="max-w-4xl mx-auto space-y-8">

                    {/* Introduction */}
                    <div className="space-y-4">
                        <h1 className="text-4xl font-bold tracking-tight text-foreground">
                            Multi-Agent Number Converter
                        </h1>
                        <p className="text-lg text-muted-foreground leading-relaxed">
                            v26.02.19-001
                        </p>
                        <p className="text-muted-foreground leading-relaxed">
                            This system is a sophisticated demonstration of a <strong>Multi-Agent AI Architecture</strong> tailored for procurement and data processing tasks.
                            It utilizes a localized orchestration layer to manage specialized agents, ensuring accuracy, modularity, and offline capability.
                        </p>
                    </div>

                    {/* Architecture Overview */}
                    <section className="space-y-4">
                        <div className="flex items-center gap-2 text-blue-500">
                            <Network className="h-6 w-6" />
                            <h3 className="text-2xl font-semibold text-foreground">System Architecture</h3>
                        </div>
                        <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                            <div className="grid md:grid-cols-2 gap-8">
                                <div>
                                    <h4 className="font-semibold mb-2">Frontend (React + Vite)</h4>
                                    <p className="text-sm text-muted-foreground">
                                        A modern, responsive dashboard built with <strong>React</strong>, <strong>Tailwind CSS</strong>, and <strong>Shadcn UI</strong>.
                                        It features a glassmorphic aesthetic ("Neon Glass") and real-time WebSocket-like state synchronization.
                                    </p>
                                </div>
                                <div>
                                    <h4 className="font-semibold mb-2">Backend (FastAPI + LangGraph)</h4>
                                    <p className="text-sm text-muted-foreground">
                                        Powered by <strong>FastAPI</strong> for high-performance async API endpoints.
                                        The core logic is driven by <strong>LangGraph</strong>, a stateful orchestration library that manages the workflow between different AI agents.
                                    </p>
                                </div>
                            </div>
                        </Card>
                    </section>

                    {/* The Agents */}
                    <section className="space-y-4">
                        <div className="flex items-center gap-2 text-purple-500">
                            <Bot className="h-6 w-6" />
                            <h3 className="text-2xl font-semibold text-foreground">The Agent Swarm</h3>
                        </div>
                        <div className="grid gap-4 md:grid-cols-2">
                            <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-blue-500"></span> Orchestrator
                                </h4>
                                <p className="text-sm text-muted-foreground">
                                    The central brain. It analyzes user input to determine intent. If the input contains numbers that need converting to text, it routes to <strong>Agent A</strong>.
                                    If it detects text that represents numbers, it routes to <strong>Agent B</strong>. For general queries, it responds directly.
                                </p>
                            </Card>

                            <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-green-500"></span> Agent A (Num2Text)
                                </h4>
                                <p className="text-sm text-muted-foreground">
                                    Specialized in converting numeric digits into their written English equivalent.
                                    <br />Example: <code>123</code> &rarr; "one hundred twenty-three".
                                </p>
                            </Card>
                            <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-green-500"></span> Email Agent
                                </h4>
                                <p className="text-sm text-muted-foreground">
                                    Specialized in converting numeric digits into their written English equivalent.
                                    <br />Example: <code>123</code> &rarr; "one hundred twenty-three".
                                </p>
                            </Card>
                            <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-green-500"></span> Procurement Agent
                                </h4>
                                <p className="text-sm text-muted-foreground">
                                    Specialized in converting numeric digits into their written English equivalent.
                                    <br />Example: <code>123</code> &rarr; "one hundred twenty-three".
                                </p>
                            </Card>

                            <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-orange-500"></span> Agent B (Text2Num)
                                </h4>
                                <p className="text-sm text-muted-foreground">
                                    Specialized in converting written English number words into numeric digits.
                                    <br />Example: "fifty-five" &rarr; <code>55</code>.
                                </p>
                            </Card>
                            <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-red-500"></span> Local LLM
                                </h4>
                                <p className="text-sm text-muted-foreground">
                                    All agents are powered by <strong>Ollama</strong> running local models (e.g., Llama 3, Mistral).
                                    This ensures zero data leakage and operation without an internet connection.
                                </p>
                            </Card>
                        </div>
                    </section>

                    {/* Features */}
                    <section className="space-y-4">
                        <div className="flex items-center gap-2 text-amber-500">
                            <Terminal className="h-6 w-6" />
                            <h3 className="text-2xl font-semibold text-foreground">Key Features</h3>
                        </div>
                        <div className="grid gap-4">
                            <Card className="p-5 flex gap-4 items-start bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10">
                                <div className="p-2 rounded-lg bg-blue-500/10 text-blue-500">
                                    <Mail className="h-5 w-5" />
                                </div>
                                <div>
                                    <h4 className="font-semibold">Email Integration</h4>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        Connects to IMAP/SMTP servers to fetch and send emails.
                                        Integrated directly into the workflow, allowing agents to process incoming email data.
                                    </p>
                                </div>
                            </Card>
                            <Card className="p-5 flex gap-4 items-start bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10">
                                <div className="p-2 rounded-lg bg-green-500/10 text-green-500">
                                    <Database className="h-5 w-5" />
                                </div>
                                <div>
                                    <h4 className="font-semibold">Local SQLite Sync</h4>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        Implements a "Local-First" architecture. Emails are fetched from the server and stored in a local <strong>SQLite</strong> database for instant access, search, and offline availability.
                                    </p>
                                </div>
                            </Card>
                            <Card className="p-5 flex gap-4 items-start bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10">
                                <div className="p-2 rounded-lg bg-purple-500/10 text-purple-500">
                                    <Bot className="h-5 w-5" />
                                </div>
                                <div>
                                    <h4 className="font-semibold">Neural Dashboard</h4>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        Visualizes the internal "thought process" of the agents. Watch as the Orchestrator delegates tasks and agents execute their specific logic in real-time.
                                    </p>
                                </div>
                            </Card>
                        </div>
                    </section>

                    <div className="h-20" /> {/* Bottom spacer */}
                </div>
            </ScrollArea>
        </div>
    );
}
