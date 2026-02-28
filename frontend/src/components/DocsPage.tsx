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
                            v26.02.28-002 (Fully Integrated Compliance & PDF Generation)
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
                        <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm md:col-span-2">
                            <h4 className="font-bold text-xl mb-3 flex items-center gap-2">
                                <span className="w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.8)]"></span> Orchestrator
                            </h4>
                            <p className="text-foreground/90 leading-relaxed mb-4">
                                The core routing mechanism for the entire Multi-Agent architecture. It receives all top-level inputs (text, voice, or systemic triggers) and uses an LLM to determine intent.
                            </p>
                            <ul className="list-disc pl-5 space-y-2 text-muted-foreground text-sm">
                                <li><strong>State Management:</strong> Maintains the global context across sub-agents using LangGraph's state dictionary.</li>
                                <li><strong>Dynamic Routing:</strong> Evaluates incoming prompts to decide the agent route: <code>email</code>, <code>compliance</code>, <code>pdf</code>, <code>num2text</code>/<code>text2num</code>, or <code>unknown</code> (UI navigation/banter).</li>
                                <li><strong>Instance Scaling:</strong> Uses 6 distinct LLM instances natively orchestrated to segregate responsibilities (routing, translation, extraction, compliance explanation, PO writing).</li>
                            </ul>
                        </Card>

                        <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm md:col-span-2">
                            <h4 className="font-bold text-xl mb-3 flex items-center gap-2">
                                <span className="w-3 h-3 rounded-full bg-sky-500 shadow-[0_0_10px_rgba(14,165,233,0.8)]"></span> Email Agent
                            </h4>
                            <p className="text-foreground/90 leading-relaxed mb-4">
                                An autonomous inbox processor designed to transform unstructured conversational emails into formatted procurement data.
                            </p>
                            <ul className="list-disc pl-5 space-y-2 text-muted-foreground text-sm">
                                <li><strong>Information Extraction:</strong> Uses an LLM constrained by Pydantic schemas to pull out `item_name`, `quantity`, and temporal requirements (e.g., "Need in 5 days").</li>
                                <li><strong>Database Linking:</strong> Hooks the extracted text to precise Database records using text matching, fetching unit costs and associating reliable vendor profiles.</li>
                                <li><strong>Mathematical Priority:</strong> Automatically calculates Urgency Priority (High/Medium/Low) strictly based on the requested temporal delivery windows.</li>
                            </ul>
                        </Card>

                        <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm md:col-span-2">
                            <h4 className="font-bold text-xl mb-3 flex items-center gap-2">
                                <span className="w-3 h-3 rounded-full bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.8)]"></span> Compliance Agent
                            </h4>
                            <p className="text-foreground/90 leading-relaxed mb-4">
                                The gatekeeper of corporate policy. Before any purchase order can be drafted, this agent verifies that the proposed order meets all legal and internal thresholds, running on a dataset of extracted emails.
                            </p>
                            <ul className="list-disc pl-5 space-y-2 text-muted-foreground text-sm">
                                <li><strong>Gatekeeper Logic (3 Rules):</strong> Enforces Inventory Capacity limits (<code>max_capacity</code>), Department Budget constraints (<code>limit_amount</code>), and Policy regulations (<code>max_single_order_amount</code>, vendor approval rating).</li>
                                <li><strong>LLM Explainer:</strong> Processes rule-based pass/fail outcomes into natural, reader-friendly prose, translating technical "Failed on vendor_score &lt; 70" into actionable plain English recommendations (e.g., "Consider switching to an approved vendor").</li>
                                <li><strong>Automated Drafting:</strong> Successfully compliant emails automatically generate <code>DRAFT</code> status entries in the <code>orders</code> table.</li>
                            </ul>
                        </Card>

                        <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm md:col-span-2">
                            <h4 className="font-bold text-xl mb-3 flex items-center gap-2">
                                <span className="w-3 h-3 rounded-full bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.8)]"></span> Order & PDF Agent
                            </h4>
                            <p className="text-foreground/90 leading-relaxed mb-4">
                                The execution arm of the system. Transitions valid DRAFT orders into legally binding, printable Purchase Order PDFs.
                            </p>
                            <ul className="list-disc pl-5 space-y-2 text-muted-foreground text-sm">
                                <li><strong>LLM Letter Drafting:</strong> Generates context-aware formal textual PO bodies utilizing specific database inputs (items, units, vendor names).</li>
                                <li><strong>Fpdf2 PDF Generation:</strong> Uses the <code>fpdf2</code> library to compile structured graphical PDF documents (Header, Summary Tables, Formal Body, Footers).</li>
                                <li><strong>Unicode Sanitization:</strong> Employs intelligent character cleaning strings (e.g., swapping em dashes `—` for hyphens) to ensure absolute stability under strict Helvetica font encoding formats.</li>
                            </ul>
                        </Card>

                        <Card className="p-6 bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm md:col-span-2">
                            <h4 className="font-bold text-xl mb-3 flex items-center gap-2">
                                <span className="w-3 h-3 rounded-full bg-teal-500 shadow-[0_0_10px_rgba(20,184,166,0.8)]"></span> Forecast Agent (WIP)
                            </h4>
                            <p className="text-foreground/90 leading-relaxed mb-4">
                                A proactive analytical agent that works strictly in the background to prevent supply chain bottlenecks.
                            </p>
                            <ul className="list-disc pl-5 space-y-2 text-muted-foreground text-sm">
                                <li><strong>Inventory Monitoring:</strong> Continuously polls the `inventory` table against the `min_qty` limits.</li>
                                <li><strong>Predictive Analytics:</strong> Uses historical order velocity to predict when an item will stock out based on current `qty_on_hand`.</li>
                                <li><strong>Autonomous Drafting:</strong> When a stock-out is predicted, it autonomously prepares a "Restock Draft" email and queues it for the Orchestrator to notify the user.</li>
                            </ul>
                        </Card>
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

                    {/* Chat Commands & Routing */}
                    <section className="space-y-4">
                        <div className="flex items-center gap-2 text-indigo-500">
                            <Bot className="h-6 w-6" />
                            <h3 className="text-2xl font-semibold text-foreground">Chat Commands & Routing</h3>
                        </div>
                        <p className="text-muted-foreground">
                            The intelligent Orchestrator categorizes prompt intents and explicitly routes to matching pipelines.
                        </p>

                        <div className="overflow-hidden rounded-lg border border-white/20 dark:border-white/10 shadow-sm bg-white/40 dark:bg-black/40 backdrop-blur-sm">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-black/5 dark:bg-white/5 border-b border-white/20 dark:border-white/10">
                                    <tr>
                                        <th className="px-4 py-3 font-semibold text-foreground">User Query Example</th>
                                        <th className="px-4 py-3 font-semibold text-foreground">Agent Route</th>
                                        <th className="px-4 py-3 font-semibold text-foreground">Pipeline Execution Pattern</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/10">
                                    <tr>
                                        <td className="px-4 py-3 font-mono text-xs">"analyze emails"</td>
                                        <td className="px-4 py-3"><span className="px-2 py-1 bg-sky-500/10 text-sky-600 rounded">email</span></td>
                                        <td className="px-4 py-3 text-muted-foreground">Fetches unanalyzed emails → AI extract → Database Lookup → Runs full compliance → Creates DRAFT</td>
                                    </tr>
                                    <tr>
                                        <td className="px-4 py-3 font-mono text-xs">"run compliance checks"</td>
                                        <td className="px-4 py-3"><span className="px-2 py-1 bg-rose-500/10 text-rose-600 rounded">compliance</span></td>
                                        <td className="px-4 py-3 text-muted-foreground">Iterates ALL historical `email_analysis` records → Re-runs gatekeeper → Creates DRAFTs</td>
                                    </tr>
                                    <tr>
                                        <td className="px-4 py-3 font-mono text-xs">"generate pdf for order 14"</td>
                                        <td className="px-4 py-3"><span className="px-2 py-1 bg-amber-500/10 text-amber-600 rounded">pdf</span></td>
                                        <td className="px-4 py-3 text-muted-foreground">Extracts integer order ID via Regex → Generates LLM narrative → Builds Helvetica PDF → Updates DB path</td>
                                    </tr>
                                    <tr>
                                        <td className="px-4 py-3 font-mono text-xs">"show high priority emails"</td>
                                        <td className="px-4 py-3"><span className="px-2 py-1 bg-gray-500/10 text-gray-600 rounded">unknown</span></td>
                                        <td className="px-4 py-3 text-muted-foreground">Orchestrator generates Client UI Action → Fires <code>redirect</code> to Emails tab + <code>filter: High</code></td>
                                    </tr>
                                    <tr>
                                        <td className="px-4 py-3 font-mono text-xs">"42" / "forty two"</td>
                                        <td className="px-4 py-3"><span className="px-2 py-1 bg-blue-500/10 text-blue-600 rounded">num2text</span> / <span className="px-2 py-1 bg-blue-500/10 text-blue-600 rounded">text2num</span></td>
                                        <td className="px-4 py-3 text-muted-foreground">Trigger pure demonstration conversational agents for simple text/integer transformations.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </section>

                    {/* Key Endpoints */}
                    <section className="space-y-4">
                        <div className="flex items-center gap-2 text-green-500">
                            <Network className="h-6 w-6" />
                            <h3 className="text-2xl font-semibold text-foreground">Interactive Procurement APIs</h3>
                        </div>
                        <p className="text-muted-foreground">
                            The system decouples extraction from downstream pipelines, allowing user-gated execution via these endpoints:
                        </p>
                        <div className="grid gap-4">
                            <Card className="p-5 flex gap-4 items-start bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10">
                                <div>
                                    <h4 className="font-mono font-semibold text-blue-500">POST /procurement/{"{email_id}"}/compliance</h4>
                                    <p className="text-sm text-foreground/90 mt-1">
                                        Runs the gatekeeper rules against an already extracted email record. Updates the `compliance_status` flag to either `Passed` or `Failed` and saves a plain-english explanation.
                                    </p>
                                </div>
                            </Card>
                            <Card className="p-5 flex gap-4 items-start bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10">
                                <div>
                                    <h4 className="font-mono font-semibold text-green-500">POST /procurement/{"{email_id}"}/order</h4>
                                    <p className="text-sm text-foreground/90 mt-1">
                                        Initiates actual purchase order creation. Only executes if the row's `compliance_status` is `Passed`. Drops a record in the `orders` table and triggers local PDF file generation.
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
                                    id, email_id, priority, summary, item_id, item_name, item_quantity, item_unit_price, vendor_id, vendor_name, vendor_email, vendor_phone, total_cost, compliance_status, compliance_explanation, order_id
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
                                    id, item_id, qty, vendor_id, amount, status, pdf_path, created_at
                                </p>
                            </Card>
                        </div>
                    </section>

                    <div className="h-20" /> {/* Bottom spacer */}
                </div>
            </ScrollArea >
        </div >
    );
}
