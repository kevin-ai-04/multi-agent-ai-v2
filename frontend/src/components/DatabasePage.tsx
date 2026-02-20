import { useState, useEffect } from "react"
import { getTables, getTableData, updateTableRow } from "@/api/client"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Loader2, Database, Edit2, Check, X } from "lucide-react"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { cn } from "@/lib/utils"

export function DatabasePage() {
    const [tables, setTables] = useState<string[]>([])
    const [selectedTable, setSelectedTable] = useState<string | null>(null)
    const [data, setData] = useState<any[]>([])
    const [columns, setColumns] = useState<string[]>([])
    const [isLoadingTables, setIsLoadingTables] = useState(false)
    const [isLoadingData, setIsLoadingData] = useState(false)

    // Editing State
    const [editingRow, setEditingRow] = useState<any | null>(null)
    const [editFormData, setEditFormData] = useState<any>({})
    const [isSaving, setIsSaving] = useState(false)
    const [saveError, setSaveError] = useState<string | null>(null)

    useEffect(() => {
        fetchTables();
    }, []);

    useEffect(() => {
        if (selectedTable) {
            fetchTableData(selectedTable);
        }
    }, [selectedTable]);

    const fetchTables = async () => {
        setIsLoadingTables(true);
        try {
            const res = await getTables();
            setTables(res.tables || []);
            if (res.tables && res.tables.length > 0 && !selectedTable) {
                setSelectedTable(res.tables[0]);
            }
        } catch (error) {
            console.error("Failed to fetch tables:", error);
        } finally {
            setIsLoadingTables(false);
        }
    };

    const fetchTableData = async (tableName: string) => {
        setIsLoadingData(true);
        setData([]);
        setColumns([]);
        try {
            const res = await getTableData(tableName);
            const fetchedData = res.data || [];
            setData(fetchedData);
            if (fetchedData.length > 0) {
                setColumns(Object.keys(fetchedData[0]));
            }
        } catch (error) {
            console.error(`Failed to fetch data for ${tableName}:`, error);
        } finally {
            setIsLoadingData(false);
        }
    };

    const handleEditClick = (row: any) => {
        setEditingRow(row);
        setEditFormData({ ...row }); // copy row to form
        setSaveError(null);
    };

    const handleFormChange = (key: string, value: string) => {
        setEditFormData((prev: Record<string, any>) => ({
            ...prev,
            [key]: value
        }));
    };

    const handleSave = async () => {
        if (!selectedTable || !editingRow) return;
        setIsSaving(true);
        setSaveError(null);
        try {
            await updateTableRow(selectedTable, editingRow, editFormData);
            // Refresh data on success
            await fetchTableData(selectedTable);
            setEditingRow(null); // close dialog
        } catch (error: any) {
            console.error("Failed to save row:", error);
            setSaveError(error.message || "Failed to save changes. Please try again.");
        } finally {
            setIsSaving(false);
        }
    };


    return (
        <div className="flex h-full w-full overflow-hidden">
            {/* Sidebar for choosing tables */}
            <div className="w-64 border-r border-white/10 bg-black/10 backdrop-blur-md flex flex-col items-center pt-6 space-y-2">
                <div className="flex items-center gap-2 mb-4 text-primary px-6 w-full justify-start">
                    <Database className="h-5 w-5" />
                    <h2 className="font-semibold tracking-wide">Schemas</h2>
                </div>

                {isLoadingTables ? (
                    <div className="flex justify-center p-4 w-full"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
                ) : (
                    <ScrollArea className="w-full flex-1 px-4">
                        <div className="space-y-1 w-full flex flex-col items-center">
                            {tables.map(table => (
                                <Button
                                    key={table}
                                    variant="ghost"
                                    className={cn(
                                        "w-full justify-start font-mono text-sm",
                                        selectedTable === table
                                            ? "bg-primary/20 text-primary border border-primary/20"
                                            : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
                                    )}
                                    onClick={() => setSelectedTable(table)}
                                >
                                    {table}
                                </Button>
                            ))}
                        </div>
                    </ScrollArea>
                )}
            </div>

            {/* Main content area for viewing rows */}
            <div className="flex-1 flex flex-col overflow-hidden relative">
                {/* Header block with selected table name */}
                <div className="h-16 border-b border-white/5 bg-black/5 flex items-center px-8">
                    <h1 className="text-xl font-bold font-mono tracking-wider flex items-center gap-3">
                        {selectedTable ? (
                            <>
                                <span className="text-muted-foreground">SELECT * FROM</span>
                                <span className="text-primary">{selectedTable}</span>
                            </>
                        ) : "Select a table"}
                    </h1>
                </div>

                {/* Table Data Viewer */}
                <ScrollArea className="flex-1">
                    <div className="p-8">
                        {isLoadingData ? (
                            <div className="flex flex-col items-center justify-center p-20 text-muted-foreground space-y-4">
                                <Loader2 className="h-8 w-8 animate-spin" />
                                <p>Querying {selectedTable}...</p>
                            </div>
                        ) : data.length === 0 ? (
                            <div className="flex items-center justify-center p-20 text-muted-foreground border border-dashed border-white/10 rounded-xl bg-black/20">
                                No records found in {selectedTable}.
                            </div>
                        ) : (
                            <Card className="glass overflow-hidden border-white/10">
                                <div className="overflow-x-auto relative">
                                    <Table>
                                        <TableHeader className="bg-black/40 hover:bg-black/40 sticky top-0 z-10">
                                            <TableRow className="border-b border-white/10 hover:bg-transparent">
                                                <TableHead className="w-16 sticky left-0 bg-black/40 z-20 backdrop-blur-md border-r border-white/5"></TableHead>
                                                {columns.map(col => (
                                                    <TableHead key={col} className="font-mono text-xs text-white/70 whitespace-nowrap min-w-[120px]">
                                                        {col}
                                                    </TableHead>
                                                ))}
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {data.map((row, i) => (
                                                <TableRow key={i} className="border-b border-white/5 hover:bg-white/5 group">
                                                    <TableCell className="sticky left-0 bg-background/50 group-hover:bg-white/5 backdrop-blur-sm border-r border-white/5 z-10 p-2">
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            className="h-8 w-8 text-muted-foreground hover:text-primary opacity-50 group-hover:opacity-100 transition-opacity"
                                                            onClick={() => handleEditClick(row)}
                                                        >
                                                            <Edit2 className="h-4 w-4" />
                                                        </Button>
                                                    </TableCell>
                                                    {columns.map(col => {
                                                        const val = row[col];
                                                        const isNull = val === null;
                                                        // Truncate long strings for view
                                                        let displayVal = val;
                                                        if (typeof val === 'string' && val.length > 50) {
                                                            displayVal = val.substring(0, 50) + "...";
                                                        }

                                                        return (
                                                            <TableCell key={col} className="font-mono text-sm whitespace-nowrap overflow-hidden text-ellipsis max-w-xs p-3">
                                                                {isNull ? <span className="text-white/20 italic">NULL</span> : displayVal}
                                                            </TableCell>
                                                        )
                                                    })}
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </div>
                            </Card>
                        )}
                    </div>
                    <div className="h-20" />
                </ScrollArea>

                {/* Floating Action / Stats */}
                {data.length > 0 && !isLoadingData && (
                    <div className="absolute bottom-6 right-8 pointer-events-none">
                        <div className="glass px-4 py-2 rounded-full border border-white/20 text-xs font-mono text-muted-foreground shadow-lg backdrop-blur-xl pointer-events-auto">
                            {data.length} row{data.length !== 1 ? 's' : ''} retrieved
                        </div>
                    </div>
                )}
            </div>

            {/* Edit Dialog */}
            <Dialog open={!!editingRow} onOpenChange={(open) => !open && setEditingRow(null)}>
                <DialogContent className="sm:max-w-[600px] glass border-white/20 max-h-[80vh] overflow-hidden flex flex-col p-0">
                    <DialogHeader className="p-6 pb-2">
                        <DialogTitle className="flex items-center gap-2">
                            <Database className="h-5 w-5 text-primary" />
                            Edit Row in <span className="font-mono text-primary">{selectedTable}</span>
                        </DialogTitle>
                        <DialogDescription>
                            Make changes to the selected record. Avoid changing primary keys to prevent constraint errors.
                        </DialogDescription>
                    </DialogHeader>

                    <ScrollArea className="flex-1 px-6">
                        <div className="grid gap-4 py-4 pr-4">
                            {columns.map(col => (
                                <div key={col} className="grid grid-cols-4 items-center gap-4">
                                    <Label htmlFor={`edit-${col}`} className="text-right font-mono text-xs opacity-70 break-all">
                                        {col}
                                    </Label>
                                    <Input
                                        id={`edit-${col}`}
                                        value={editFormData[col] === null ? '' : editFormData[col]}
                                        onChange={(e) => handleFormChange(col, e.target.value)}
                                        className="col-span-3 font-mono text-sm bg-black/20 border-white/10"
                                        placeholder={editingRow && editingRow[col] === null ? "NULL" : ""}
                                    />
                                </div>
                            ))}
                        </div>
                    </ScrollArea>

                    <div className="p-6 pt-2 bg-black/10 mt-auto border-t border-white/10 shrink-0">
                        {saveError && (
                            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-md text-red-400 text-sm">
                                {saveError}
                            </div>
                        )}
                        <DialogFooter className="flex w-full items-center justify-end sm:justify-end">
                            <Button
                                variant="ghost"
                                onClick={() => setEditingRow(null)}
                                disabled={isSaving}
                                className="mr-2"
                            >
                                <X className="mr-2 h-4 w-4" /> Cancel
                            </Button>
                            <Button
                                onClick={handleSave}
                                disabled={isSaving}
                                className="bg-primary hover:bg-primary/80 text-white"
                            >
                                {isSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Check className="mr-2 h-4 w-4" />}
                                Save Changes
                            </Button>
                        </DialogFooter>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    )
}
