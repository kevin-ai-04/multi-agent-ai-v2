import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Brain, Activity, Terminal, ArrowRight, CheckCircle2, Clock, AlertCircle, Calculator, Type, Mail, Shield, ShoppingCart, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Message } from "./ChatInterface";

interface DashboardProps {
    messages: Message[];
    isLoading: boolean;
}

interface Agent {
    id: string;
    key: string; // Used for matching logs
    name: string;
    role: string;
    status: "active" | "idle" | "thinking" | "error";
    icon: any;
    color: string;
    description: string;
    thoughts: string[];
    capabilities: string[];
}

const initialAgents: Agent[] = [
    {
        id: "orch-01",
        key: "Orchestrator",
        name: "Orchestrator",
        role: "System Coordinator",
        status: "idle",
        icon: Brain,
        color: "from-purple-500 to-indigo-600",
        description: "Central neural unit responsible for breaking down user requests and delegating sub-tasks to specialized agents.",
        thoughts: ["System initialized.", "Waiting for input..."],
        capabilities: ["Intent Classification", "Task Delegation", "Context Management"]
    },
    {
        id: "agent-email-05",
        key: "Email Agent",
        name: "Email Agent",
        role: "Communication",
        status: "idle",
        icon: Mail,
        color: "from-sky-500 to-blue-600",
        description: "Handles incoming and outgoing email communications, extracting orders or vendor queries.",
        thoughts: ["Model loaded.", "Monitoring inbox..."],
        capabilities: ["Email Parsing", "Supplier Search", "Cost Calculation"]
    },
    {
        id: "agent-comp-06",
        key: "Compliance Agent",
        name: "Compliance Agent",
        role: "Policy Enforcer",
        status: "idle",
        icon: Shield,
        color: "from-rose-500 to-red-600",
        description: "Checks procurement requests against company policies, budget limits, and vendor restrictions.",
        thoughts: ["Policies loaded.", "Ready for validation."],
        capabilities: ["Policy Check", "Budget Approval"]
    },
    {
        id: "agent-order-07",
        key: "Order Agent",
        name: "Order Agent",
        role: "Order Management",
        status: "idle",
        icon: ShoppingCart,
        color: "from-amber-500 to-yellow-600",
        description: "Processes and tracks purchase orders, managing interactions with the inventory system.",
        thoughts: ["System connected.", "Awaiting orders."],
        capabilities: ["Order Creation", "Status Tracking"]
    },
    {
        id: "agent-forecast-08",
        key: "Forecast Agent",
        name: "Forecast Agent",
        role: "Predictive Analytics",
        status: "idle",
        icon: TrendingUp,
        color: "from-teal-500 to-emerald-600",
        description: "Analyzes historical data to predict future inventory needs and suggest restock timelines.",
        thoughts: ["Data models loaded.", "Ready for analysis."],
        capabilities: ["Trend Prediction", "Demand Forecasting"]
    },
    // {
    //     id: "agent-a-02",
    //     key: "Agent A",
    //     name: "Agent A (Num2Text)",
    //     role: "Numeric Converter",
    //     status: "idle",
    //     icon: Type,
    //     color: "from-blue-500 to-cyan-500",
    //     description: "Specialized language model trained to convert numeric input (123) into natural language text (one hundred twenty-three).",
    //     thoughts: ["Model loaded.", "Standing by."],
    //     capabilities: ["Number Parsing", "Language Generation"]
    // },
    // {
    //     id: "agent-b-03",
    //     key: "Agent B",
    //     name: "Agent B (Text2Num)",
    //     role: "Semantic Parser",
    //     status: "idle",
    //     icon: Calculator,
    //     color: "from-green-500 to-emerald-600",
    //     description: "Specialized in extracting numeric values from natural language text and converting them to integer format.",
    //     thoughts: ["Model loaded.", "Standing by."],
    //     capabilities: ["Semantic Analysis", "Pattern Matching"]
    // },
    {
        id: "sys-04",
        key: "System",
        name: "System Monitor",
        role: "Infrastructure",
        status: "active",
        icon: Activity,
        color: "from-orange-500 to-red-500",
        description: "Continuously monitors system health, API latency, and resource usage across the agent swarm.",
        thoughts: ["CPU: Normal", "Memory: Optimal", "Network: Stable"],
        capabilities: ["Health Checks", "Resource Monitoring", "Alerting"]
    }
];

export function Dashboard({ messages, isLoading }: DashboardProps) {
    const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
    const [agents, setAgents] = useState<Agent[]>(initialAgents);
    const [uptime, setUptime] = useState("0h 0m 0s");

    // Real-time uptime ticker
    useEffect(() => {
        const startTime = performance.timeOrigin; // Browser tab open time

        const updateTicker = () => {
            const now = performance.now() + performance.timeOrigin;
            const diff = now - startTime;

            const hours = Math.floor(diff / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);

            setUptime(`${hours}h ${minutes}m ${seconds}s`);
        };

        const interval = setInterval(updateTicker, 1000);
        updateTicker(); // Initial call

        return () => clearInterval(interval);
    }, []);

    // Update Agent Status and Thoughts based on live messages
    useEffect(() => {
        if (messages.length === 0 && !isLoading) return;

        setAgents(prevAgents => {
            const newAgents = [...prevAgents];

            // Get the latest message with steps
            const lastMessage = messages[messages.length - 1];
            const steps = lastMessage?.steps || [];

            return newAgents.map(agent => {
                const updatedAgent = { ...agent };

                // 1. Update Status based on global loading state
                if (agent.key === "Orchestrator") {
                    updatedAgent.status = isLoading ? "thinking" : "active";
                } else if (agent.key === "System") {
                    updatedAgent.status = "active";
                } else {
                    // For worker agents, check if they were involved in the last turn
                    const engaged = steps.some(step => step.includes(agent.key));
                    if (isLoading) {
                        updatedAgent.status = "idle"; // Reset while orchestrator thinks
                    } else {
                        updatedAgent.status = engaged ? "active" : "idle";
                    }
                }

                // 2. Parse thoughts from steps
                // Filter steps that belong to this agent
                const relevantSteps = steps.filter(step => step.includes(agent.key));

                if (relevantSteps.length > 0) {
                    // Clean up the prefix "Agent Name: "
                    const cleanThoughts = relevantSteps.map(step => {
                        const parts = step.split(": ");
                        return parts.length > 1 ? parts[1] : step;
                    });
                    updatedAgent.thoughts = cleanThoughts;
                } else if (isLoading && agent.key === "Orchestrator") {
                    updatedAgent.thoughts = ["Analyzing request...", "Determining route..."];
                }

                return updatedAgent;
            });
        });

    }, [messages, isLoading]);


    return (
        <div className="h-full flex flex-col bg-transparent overflow-hidden">
            <ScrollArea className="flex-1 p-6">
                <div className="max-w-7xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-8"
                    >
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent mb-2">
                            Neural Dashboard
                        </h1>
                        <p className="text-muted-foreground">Real-time telemetry of the active agent swarm.</p>
                    </motion.div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4 gap-6">
                        {agents.map((agent, index) => (
                            <motion.div
                                key={agent.id}
                                layoutId={`card-${agent.id}`}
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: index * 0.1 }}
                                onClick={() => setSelectedAgent(agent)}
                                className="group relative cursor-pointer h-full"
                            >
                                {/* Dynamic Glow Background */}
                                <div className={`absolute -inset-0.5 bg-gradient-to-r ${agent.color} rounded-xl opacity-20 group-hover:opacity-60 blur transition duration-500`} />

                                <Card className="relative h-full bg-white/60 dark:bg-black/40 backdrop-blur-xl border-black/5 dark:border-white/10 overflow-hidden hover:bg-white/80 dark:hover:bg-black/60 transition-colors shadow-sm">
                                    <CardHeader>
                                        <div className="flex justify-between items-start mb-2">
                                            <div className={`p-3 rounded-lg bg-gradient-to-br ${agent.color} bg-opacity-10 dark:bg-opacity-20`}>
                                                <agent.icon className="w-6 h-6 text-white" />
                                            </div>
                                            <StatusBadge status={agent.status} />
                                        </div>
                                        <CardTitle className="text-xl text-foreground">{agent.name}</CardTitle>
                                        <CardDescription className="text-muted-foreground">{agent.role}</CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        <p className="text-sm text-muted-foreground/80 line-clamp-3 mb-4 h-10">
                                            {agent.description}
                                        </p>
                                        <div className="flex items-center text-xs text-blue-600 dark:text-blue-400 font-medium group-hover:translate-x-1 transition-transform mt-4">
                                            View Logs <ArrowRight className="w-3 h-3 ml-1" />
                                        </div>
                                    </CardContent>

                                    {/* Animated Activity Line */}
                                    {agent.status === 'thinking' && (
                                        <motion.div
                                            className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent w-full"
                                            animate={{ x: ['-100%', '100%'] }}
                                            transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                                        />
                                    )}
                                </Card>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </ScrollArea>

            {/* Expanded Modal Overlay */}
            <AnimatePresence>
                {selectedAgent && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setSelectedAgent(null)}
                            className="absolute inset-0 bg-white/40 dark:bg-black/60 backdrop-blur-sm"
                        />

                        <motion.div
                            layoutId={`card-${selectedAgent.id}`}
                            className="relative w-full max-w-2xl bg-white dark:bg-black/90 border border-black/5 dark:border-white/10 rounded-2xl shadow-2xl overflow-hidden z-10 flex flex-col max-h-[85vh]"
                        >
                            {/* Header */}
                            <div className={`relative p-8 overflow-hidden`}>
                                <div className={`absolute inset-0 bg-gradient-to-br ${selectedAgent.color} opacity-10`} />

                                <div className="relative z-10 flex items-start justify-between">
                                    <div className="flex items-center gap-4">
                                        <div className={`p-4 rounded-xl bg-gradient-to-br ${selectedAgent.color} shadow-lg shadow-black/5 dark:shadow-black/20`}>
                                            <selectedAgent.icon className="w-8 h-8 text-white" />
                                        </div>
                                        <div>
                                            <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-br from-gray-900 to-gray-600 dark:from-white dark:to-white/70">
                                                {selectedAgent.name}
                                            </h2>
                                            <p className="text-lg text-muted-foreground">{selectedAgent.role}</p>
                                        </div>
                                    </div>
                                    <StatusBadge status={selectedAgent.status} size="lg" />
                                </div>
                            </div>

                            <ScrollArea className="flex-1">
                                <div className="p-8 space-y-8">
                                    {/* Capabilities */}
                                    <div>
                                        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2">
                                            <Brain className="w-4 h-4" /> Attributes
                                        </h3>
                                        <div className="flex flex-wrap gap-2">
                                            {selectedAgent.capabilities.map((cap) => (
                                                <Badge key={cap} variant="secondary" className="bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 text-foreground border-black/5 dark:border-white/10 px-3 py-1">
                                                    {cap}
                                                </Badge>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Live Thoughts Terminal */}
                                    <div>
                                        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2">
                                            <Terminal className="w-4 h-4" /> Live Logs
                                        </h3>
                                        <div className="bg-gray-50 dark:bg-black/50 rounded-lg border border-black/5 dark:border-white/10 p-4 font-mono text-sm shadow-inner min-h-[150px]">
                                            {selectedAgent.thoughts.map((thought, i) => (
                                                <motion.div
                                                    key={i}
                                                    initial={{ opacity: 0, x: -10 }}
                                                    animate={{ opacity: 1, x: 0 }}
                                                    transition={{ delay: i * 0.1 }}
                                                    className="mb-2 flex items-start gap-3 last:mb-0"
                                                >
                                                    <span className="text-blue-500/50 select-none">{`>`}</span>
                                                    <span className={i === selectedAgent.thoughts.length - 1 ? 'text-blue-600 dark:text-cyan-400 font-medium' : 'text-gray-500 dark:text-gray-400'}>
                                                        {thought}
                                                    </span>
                                                </motion.div>
                                            ))}
                                            <motion.div
                                                animate={{ opacity: [0, 1, 0] }}
                                                transition={{ repeat: Infinity, duration: 0.8 }}
                                                className="w-2 h-4 bg-blue-500/50 dark:bg-cyan-500/50 mt-1"
                                            />
                                        </div>
                                    </div>

                                    <div className="text-xs text-muted-foreground pt-4 border-t border-black/5 dark:border-white/5 flex justify-between">
                                        <span>Agent ID: <span className="font-mono text-blue-500 dark:text-blue-400/70">{selectedAgent.id}</span></span>
                                        <span>Uptime: {uptime}</span>
                                    </div>
                                </div>
                            </ScrollArea>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}

function StatusBadge({ status, size = "sm" }: { status: string, size?: "sm" | "lg" }) {
    const config = {
        active: { color: "bg-green-500", label: "Active", icon: CheckCircle2, text: "text-green-600 dark:text-green-400", bg: "bg-green-500/10" },
        thinking: { color: "bg-cyan-500", label: "Thinking", icon: Activity, text: "text-cyan-600 dark:text-cyan-400", bg: "bg-cyan-500/10" },
        idle: { color: "bg-gray-400", label: "Idle", icon: Clock, text: "text-gray-500 dark:text-gray-400", bg: "bg-gray-500/10" },
        error: { color: "bg-red-500", label: "Error", icon: AlertCircle, text: "text-red-600 dark:text-red-400", bg: "bg-red-500/10" }
    }[status] || { color: "bg-gray-500", label: "Unknown", icon: Clock, text: "text-gray-500", bg: "bg-gray-500/10" };

    return (
        <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-transparent ${config.bg} ${status === 'thinking' ? 'animate-pulse' : ''} ${size === 'lg' ? 'px-4 py-1.5' : ''}`}>
            <div className={`relative flex items-center justify-center`}>
                <div className={`w-2 h-2 rounded-full ${config.color} ${status === 'active' ? 'shadow-[0_0_8px_rgba(34,197,94,0.6)]' : ''}`} />
                {status === 'thinking' && <div className={`absolute w-3 h-3 rounded-full ${config.color} opacity-30 animate-ping`} />}
            </div>
            <span className={`text-xs font-medium ${config.text} ${size === 'lg' ? 'text-sm' : ''}`}>{config.label}</span>
        </div>
    );
}
