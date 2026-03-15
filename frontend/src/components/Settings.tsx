import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Moon, Sun, Bot } from "lucide-react"
import { useEffect, useState } from "react"

export function Settings() {
    const [theme, setTheme] = useState<"light" | "dark">(
        () => (localStorage.getItem("vite-ui-theme") as "light" | "dark") || "light"
    )

    const [models, setModels] = useState<Record<string, string>>({})
    const [loadingModels, setLoadingModels] = useState(true)
    const [errorMsg, setErrorMsg] = useState<string | null>(null)

    const AVAILABLE_MODELS = ["mistral", "llama3.1", "gemma3:4b"]
    const AGENT_LABELS: Record<string, string> = {
        orchestrator: "Orchestrator Agent",
        email: "Email Extraction Agent",
        compliance: "Compliance Agent",
        po: "Order / PDF Agent",
        forecast: "Forecast Agent"
    }

    useEffect(() => {
        const root = window.document.documentElement
        root.classList.remove("light", "dark")
        root.classList.add(theme)
        localStorage.setItem("vite-ui-theme", theme)
    }, [theme])

    useEffect(() => {
        let isMounted = true;
        const fetchModels = async () => {
            try {
                const res = await fetch("http://localhost:8000/settings/models");
                if (!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                const data = await res.json();
                if (isMounted) {
                    if (data.status === "success") {
                        setModels(data.models);
                    } else {
                        setErrorMsg("Invalid data received from server.");
                    }
                    setLoadingModels(false);
                }
            } catch (err: any) {
                console.error("Failed to load models:", err);
                if (isMounted) {
                    setErrorMsg(err.message || "Failed to connect to backend server.");
                    setLoadingModels(false);
                }
            }
        };
        fetchModels();
        return () => { isMounted = false; };
    }, [])

    const toggleTheme = (checked: boolean) => {
        setTheme(checked ? "dark" : "light")
    }

    const handleModelChange = async (agentName: string, newModel: string) => {
        // Optimistic update
        setModels(prev => ({...prev, [agentName]: newModel}))
        setErrorMsg(null)
        
        try {
            const res = await fetch("http://localhost:8000/settings/models", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ agent_name: agentName, model_name: newModel })
            })
            if (!res.ok) {
                 throw new Error("Failed to update on server")
            }
        } catch(err: any) {
            console.error("Failed to update model:", err)
            setErrorMsg("Failed to save changes. Make sure backend is running.")
        }
    }

    return (
        <div className="p-6 max-w-4xl mx-auto w-full space-y-6">
            <h2 className="text-3xl font-bold tracking-tight">Settings</h2>

            <Card className="bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                <CardHeader>
                    <CardTitle>Appearance</CardTitle>
                    <CardDescription>
                        Customize how the application looks properly.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex items-center justify-between space-x-2">
                        <Label htmlFor="dark-mode" className="flex flex-col space-y-1">
                            <span>Dark Mode</span>
                            <span className="font-normal text-xs text-muted-foreground">
                                Switch between light and dark themes.
                            </span>
                        </Label>
                        <div className="flex items-center space-x-2">
                            <Sun className="h-4 w-4 text-muted-foreground" />
                            <Switch
                                id="dark-mode"
                                checked={theme === "dark"}
                                onCheckedChange={toggleTheme}
                            />
                            <Moon className="h-4 w-4 text-muted-foreground" />
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card className="bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Bot className="h-5 w-5 text-indigo-500" />
                        Agent LLM Models
                    </CardTitle>
                    <CardDescription>
                        Dynamically choose the underlying LLM for each autonomous agent.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {loadingModels ? (
                        <div className="text-sm text-muted-foreground animate-pulse">Loading configurations...</div>
                    ) : errorMsg ? (
                        <div className="text-sm font-semibold text-red-500 bg-red-500/10 p-4 rounded-md border border-red-500/20">
                            {errorMsg}
                        </div>
                    ) : (
                        <div className="grid gap-4 md:grid-cols-2">
                            {Object.entries(AGENT_LABELS).map(([agentKey, agentLabel]) => (
                                <div key={agentKey} className="flex flex-col space-y-2 p-4 rounded-lg bg-black/5 dark:bg-white/5 border border-black/10 dark:border-white/10">
                                    <Label className="font-semibold text-sm">{agentLabel}</Label>
                                    <select
                                        className="h-10 px-3 py-2 bg-white dark:bg-black border border-gray-300 dark:border-gray-700 rounded-md text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-foreground"
                                        value={models[agentKey] || "mistral"}
                                        onChange={(e) => handleModelChange(agentKey, e.target.value)}
                                    >
                                        {AVAILABLE_MODELS.map(model => (
                                            <option key={model} value={model}>{model}</option>
                                        ))}
                                    </select>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>

            <Card className="bg-white/40 dark:bg-black/40 border-white/20 dark:border-white/10 backdrop-blur-sm">
                <CardHeader>
                    <CardTitle>About</CardTitle>
                    <CardDescription>
                        Application information
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="text-sm text-muted-foreground">
                        <p>Multi-Agentic Procurement System</p>
                        <p>Work in Progress</p>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
