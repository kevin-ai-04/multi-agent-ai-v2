import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Moon, Sun } from "lucide-react"
import { useEffect, useState } from "react"

export function Settings() {
    const [theme, setTheme] = useState<"light" | "dark">(
        () => (localStorage.getItem("vite-ui-theme") as "light" | "dark") || "light"
    )

    useEffect(() => {
        const root = window.document.documentElement
        root.classList.remove("light", "dark")
        root.classList.add(theme)
        localStorage.setItem("vite-ui-theme", theme)
    }, [theme])

    const toggleTheme = (checked: boolean) => {
        setTheme(checked ? "dark" : "light")
    }

    return (
        <div className="p-6 max-w-4xl mx-auto w-full space-y-6">
            <h2 className="text-3xl font-bold tracking-tight">Settings</h2>

            <Card>
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

            <Card>
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
