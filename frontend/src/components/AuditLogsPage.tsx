import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Activity, Clock, Server, FileText, Trash2, Edit } from "lucide-react"
import { cn } from "@/lib/utils"

interface AuditLog {
    id: number;
    action: string;
    entity_type: string;
    entity_id: string | null;
    details: any;
    user_id: string;
    timestamp: string;
}

export function AuditLogsPage() {
    const [logs, setLogs] = useState<AuditLog[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchLogs()
    }, [])

    const fetchLogs = async () => {
        setIsLoading(true)
        setError(null)
        try {
            const res = await fetch('http://localhost:8000/audit_logs')
            if (!res.ok) throw new Error('Failed to fetch audit logs')
            const data = await res.json()
            setLogs(data.logs || [])
        } catch (err: any) {
            setError(err.message)
        } finally {
            setIsLoading(false)
        }
    }

    const getActionIcon = (action: string) => {
        switch (action) {
            case 'CREATE': return <FileText className="h-4 w-4 text-green-500" />;
            case 'UPDATE': return <Edit className="h-4 w-4 text-blue-500" />;
            case 'DELETE_ALL': return <Trash2 className="h-4 w-4 text-red-500" />;
            case 'MANUAL_COMPLIANCE_CHECK': return <Activity className="h-4 w-4 text-purple-500" />;
            default: return <Server className="h-4 w-4 text-gray-500" />;
        }
    }
    
    const getActionColor = (action: string) => {
         switch (action) {
            case 'CREATE': return 'bg-green-500/10 text-green-500 border-green-500/20';
            case 'UPDATE': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
            case 'DELETE_ALL': return 'bg-red-500/10 text-red-500 border-red-500/20';
            case 'MANUAL_COMPLIANCE_CHECK': return 'bg-purple-500/10 text-purple-500 border-purple-500/20';
            default: return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
        }
    }

    return (
        <div className="h-full flex flex-col p-6 overflow-hidden">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">System Audit Logs</h2>
                    <p className="text-muted-foreground mt-1">Review critical system events and data changes.</p>
                </div>
            </div>

            <Card className="flex-1 overflow-hidden flex flex-col glass border-white/20">
                <CardHeader className="bg-white/5 border-b border-white/10 pb-4">
                    <CardTitle className="text-xl flex items-center gap-2">
                        <Activity className="h-5 w-5 text-blue-500" />
                        Event Trail
                    </CardTitle>
                    <CardDescription>Chronological list of all logged system actions.</CardDescription>
                </CardHeader>
                <CardContent className="flex-1 p-0 overflow-hidden">
                    {isLoading ? (
                        <div className="flex justify-center items-center h-48">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                        </div>
                    ) : error ? (
                        <div className="p-8 text-center text-red-500 bg-red-500/10 rounded-lg m-6 border border-red-500/20 flex flex-col items-center">
                            <Trash2 className="h-8 w-8 mb-2 opacity-80" />
                            <p className="font-semibold">Error Loading Logs</p>
                            <p className="text-sm opacity-80 mt-1">{error}</p>
                        </div>
                    ) : logs.length === 0 ? (
                        <div className="flex flex-col justify-center items-center h-48 text-muted-foreground">
                            <Activity className="h-10 w-10 mb-2 opacity-20" />
                            <p>No audit logs found.</p>
                        </div>
                    ) : (
                        <ScrollArea className="h-full w-full">
                            <Table>
                                <TableHeader className="bg-black/5 dark:bg-white/5 sticky top-0 z-10 backdrop-blur-md">
                                    <TableRow className="border-white/10 hover:bg-transparent">
                                        <TableHead className="w-[180px]">Timestamp</TableHead>
                                        <TableHead>Action</TableHead>
                                        <TableHead>Entity</TableHead>
                                        <TableHead>User</TableHead>
                                        <TableHead>Details</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {logs.map((log) => (
                                        <TableRow key={log.id} className="border-white/5 hover:bg-white/5 transition-colors">
                                            <TableCell className="font-mono text-xs whitespace-nowrap text-muted-foreground">
                                                <div className="flex items-center gap-1.5">
                                                    <Clock className="h-3 w-3" />
                                                    {new Date(log.timestamp + "Z").toLocaleString()}
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <Badge variant="outline" className={cn("flex w-fit items-center gap-1 text-[10px] font-semibold uppercase tracking-wider", getActionColor(log.action))}>
                                                    {getActionIcon(log.action)}
                                                    {log.action}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>
                                                <div className="flex flex-col">
                                                    <span className="font-medium text-sm capitalize">{log.entity_type}</span>
                                                    {log.entity_id && (
                                                        <span className="text-xs text-muted-foreground font-mono">ID: {log.entity_id}</span>
                                                    )}
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <Badge variant="secondary" className="bg-secondary/50 text-secondary-foreground text-xs">
                                                    {log.user_id}
                                                </Badge>
                                            </TableCell>
                                            <TableCell className="max-w-[400px]">
                                                {log.details ? (
                                                    <div className="bg-black/10 dark:bg-black/30 rounded p-2 overflow-x-auto text-xs font-mono text-muted-foreground border border-white/5">
                                                        <pre className="whitespace-pre-wrap">{JSON.stringify(log.details, null, 2)}</pre>
                                                    </div>
                                                ) : (
                                                    <span className="text-muted-foreground text-sm italic">No details</span>
                                                )}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </ScrollArea>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
