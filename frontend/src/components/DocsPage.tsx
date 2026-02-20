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
                            Multi-Agent Procurement Management
                        </h1>
                        <p className="text-lg text-muted-foreground leading-relaxed">
                            v26.02.19-001
                        </p>
                        <p className="text-muted-foreground leading-relaxed">
                            This system is a sophisticated demonstration of a <strong>Multi-Agent AI Architecture</strong> tailored for autonomous procurement workflows.
                            It utilizes a localized orchestration layer to manage specialized agents (Email, Compliance, Orders, Forecasting), ensuring accuracy, policy adherence, and offline capability.
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
                                    The central brain. It delegates tasks to the specialized procurement agents based on the user's overarching goals, compiling their results into actionable summaries.
                                </p>
                            </Card>

                            <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-sky-500"></span> Email Agent (WIP)
                                </h4>
                                <p className="text-sm text-muted-foreground">
                                    Monitors the inbox for new requests or vendor replies. It parses incoming emails to extract crucial details like items, quantities, and vendor information.
                                </p>
                            </Card>

                            <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-rose-500"></span> Compliance Agent (WIP)
                                </h4>
                                <p className="text-sm text-muted-foreground">
                                    Ensures all operations adhere to internal company policies. It cross-references orders against budget constraints and vendor approval scores.
                                </p>
                            </Card>

                            <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-amber-500"></span> Order Agent (WIP)
                                </h4>
                                <p className="text-sm text-muted-foreground">
                                    Generates formal purchase orders and interacts with the internal system to log details, change status, and eventually draft completion PDFs.
                                </p>
                            </Card>

                            <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold text-lg mb-2 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-teal-500"></span> Forecast Agent (WIP)
                                </h4>
                                <p className="text-sm text-muted-foreground">
                                    Uses historical data across the database to predict future material requirements and recommends proactive restocking measures.
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
                                    <h4 className="font-semibold">Local SQLite DB</h4>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        Implements a "Local-First" architecture. The unified <strong>procurement.db</strong> securely stores emails alongside inventory, budgets, vendors, and policies for seamless, offline agent coordination.
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

                    {/* Database Tables */}
                    <section className="space-y-4">
                        <div className="flex items-center gap-2 text-rose-500">
                            <Database className="h-6 w-6" />
                            <h3 className="text-2xl font-semibold text-foreground">Database Schema</h3>
                        </div>
                        <p className="text-muted-foreground">
                            The system relies on a unified <strong>procurement.db</strong> SQLite database. Here's a breakdown of the core tables used by the Agent Swarm:
                        </p>
                        <div className="grid gap-4 md:grid-cols-2">
                            <Card className="p-4 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold flex items-center gap-2 mb-1">
                                    <span className="w-2 h-2 rounded-sm bg-blue-500"></span> emails
                                </h4>
                                <p className="text-sm text-muted-foreground mb-2">
                                    Stores raw email data fetched via IMAP.
                                </p>
                                <p className="text-xs font-mono text-muted-foreground bg-black/5 dark:bg-white/5 p-1 rounded">
                                    id, subject, sender, date, body, folder, is_read, timestamp
                                </p>
                            </Card>

                            <Card className="p-4 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold flex items-center gap-2 mb-1">
                                    <span className="w-2 h-2 rounded-sm bg-blue-500"></span> email_analysis
                                </h4>
                                <p className="text-sm text-muted-foreground mb-2">
                                    Holds structured data extracted by the Email Agent.
                                </p>
                                <p className="text-xs font-mono text-muted-foreground bg-black/5 dark:bg-white/5 p-1 rounded overflow-x-auto whitespace-nowrap">
                                    id, email_id, priority, summary, item_id, item_name, item_unit_price, vendor_id, vendor_name, vendor_email, vendor_phone, total_cost
                                </p>
                            </Card>

                            <Card className="p-4 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold flex items-center gap-2 mb-1">
                                    <span className="w-2 h-2 rounded-sm bg-green-500"></span> items
                                </h4>
                                <p className="text-sm text-muted-foreground mb-2">
                                    Product catalog including pricing and available vendors.
                                </p>
                                <p className="text-xs font-mono text-muted-foreground bg-black/5 dark:bg-white/5 p-1 rounded overflow-x-auto whitespace-nowrap">
                                    item_id, item_name, sku, item_unit_qty, item_unit_price, item_vendor_id
                                </p>
                            </Card>

                            <Card className="p-4 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold flex items-center gap-2 mb-1">
                                    <span className="w-2 h-2 rounded-sm bg-green-500"></span> vendors
                                </h4>
                                <p className="text-sm text-muted-foreground mb-2">
                                    Supplier details and their internal approval scores.
                                </p>
                                <p className="text-xs font-mono text-muted-foreground bg-black/5 dark:bg-white/5 p-1 rounded overflow-x-auto whitespace-nowrap">
                                    vendor_id, vendor_name, vendor_email, vendor_phone, vendor_approved, vendor_score
                                </p>
                            </Card>

                            <Card className="p-4 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold flex items-center gap-2 mb-1">
                                    <span className="w-2 h-2 rounded-sm bg-amber-500"></span> inventory
                                </h4>
                                <p className="text-sm text-muted-foreground mb-2">
                                    Tracks item quantity on hand and warehouse capacity.
                                </p>
                                <p className="text-xs font-mono text-muted-foreground bg-black/5 dark:bg-white/5 p-1 rounded overflow-x-auto whitespace-nowrap">
                                    item_id, qty_on_hand, max_capacity, min_qty
                                </p>
                            </Card>

                            <Card className="p-4 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold flex items-center gap-2 mb-1">
                                    <span className="w-2 h-2 rounded-sm bg-amber-500"></span> budget
                                </h4>
                                <p className="text-sm text-muted-foreground mb-2">
                                    Maps spending limits and used amounts per department per quarter.
                                </p>
                                <p className="text-xs font-mono text-muted-foreground bg-black/5 dark:bg-white/5 p-1 rounded overflow-x-auto whitespace-nowrap">
                                    dept, period, limit_amount, used_amount
                                </p>
                            </Card>

                            <Card className="p-4 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold flex items-center gap-2 mb-1">
                                    <span className="w-2 h-2 rounded-sm bg-purple-500"></span> policies
                                </h4>
                                <p className="text-sm text-muted-foreground mb-2">
                                    Key-value store for internal business rules (e.g. max order amount).
                                </p>
                                <p className="text-xs font-mono text-muted-foreground bg-black/5 dark:bg-white/5 p-1 rounded overflow-x-auto whitespace-nowrap">
                                    key, value
                                </p>
                            </Card>

                            <Card className="p-4 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                                <h4 className="font-bold flex items-center gap-2 mb-1">
                                    <span className="w-2 h-2 rounded-sm bg-purple-500"></span> orders
                                </h4>
                                <p className="text-sm text-muted-foreground mb-2">
                                    Historical ledger of generated purchase orders and their PDF paths.
                                </p>
                                <p className="text-xs font-mono text-muted-foreground bg-black/5 dark:bg-white/5 p-1 rounded overflow-x-auto whitespace-nowrap">
                                    order_id, item_id, qty, vendor_id, total_amount, status, pdf_path, created_at
                                </p>
                            </Card>
                        </div>
                    </section>

                    <div className="h-20" /> {/* Bottom spacer */}
                </div>
            </ScrollArea>
        </div>
    );
}
