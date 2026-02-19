import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"

interface SidebarProps {
    agentAEnabled: boolean;
    setAgentAEnabled: (enabled: boolean) => void;
    agentBEnabled: boolean;
    setAgentBEnabled: (enabled: boolean) => void;
}

export function Sidebar({
    agentAEnabled,
    setAgentAEnabled,
    agentBEnabled,
    setAgentBEnabled
}: SidebarProps) {
    return (
        <Card className="h-full border-r rounded-none shadow-none">
            <CardHeader>
                <CardTitle className="text-xl font-bold">System Control</CardTitle>
            </CardHeader>
            <Separator />
            <CardContent className="pt-6 space-y-6">
                <div className="flex items-center justify-between space-x-2">
                    <Label htmlFor="agent-a" className="flex flex-col">
                        <span className="font-medium">Num2Text Agent</span>
                        <span className="text-xs text-muted-foreground">Converts digits to words</span>
                    </Label>
                    <Switch id="agent-a" checked={agentAEnabled} onCheckedChange={setAgentAEnabled} />
                </div>

                <div className="flex items-center justify-between space-x-2">
                    <Label htmlFor="agent-b" className="flex flex-col">
                        <span className="font-medium">Text2Num Agent</span>
                        <span className="text-xs text-muted-foreground">Converts words to digits</span>
                    </Label>
                    <Switch id="agent-b" checked={agentBEnabled} onCheckedChange={setAgentBEnabled} />
                </div>
            </CardContent>
        </Card>
    )
}
