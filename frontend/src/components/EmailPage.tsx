import { useState } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Search, Filter, ArrowUpDown, Star, MoreHorizontal, Mail } from "lucide-react";

interface Email {
    id: number;
    sender: string;
    subject: string;
    preview: string;
    time: string;
    isStarred: boolean;
    isUnread: boolean;
    tag: string;
}

const dummyEmails: Email[] = [
    {
        id: 1,
        sender: "Sarah Johnson",
        subject: "Project Update: Q1 Goals",
        preview: "Here are the updated KPIs for the first quarter given the new...",
        time: "10:30 AM",
        isStarred: true,
        isUnread: true,
        tag: "Work"
    },
    {
        id: 2,
        sender: "Tech Daily",
        subject: "The Future of AI Agents",
        preview: "In today's newsletter, we dive deep into autonomous agents and...",
        time: "9:15 AM",
        isStarred: false,
        isUnread: true,
        tag: "Newsletter"
    },
    {
        id: 3,
        sender: "Alex Chen",
        subject: "Lunch tomorrow?",
        preview: "Hey! Are we still on for trying that new sushi place downtown?",
        time: "Yesterday",
        isStarred: false,
        isUnread: false,
        tag: "Personal"
    },
    {
        id: 4,
        sender: "Cloud Billing",
        subject: "Invoice #2024-001",
        preview: "Your monthly subscription has been renewed. View details attached...",
        time: "Yesterday",
        isStarred: false,
        isUnread: false,
        tag: "Finance"
    },
    {
        id: 5,
        sender: "Team Lead",
        subject: "Code Review Required",
        preview: "Please review PR #452 regarding the new authentication flow...",
        time: "2 days ago",
        isStarred: true,
        isUnread: false,
        tag: "Work"
    },
    {
        id: 6,
        sender: "Security Alert",
        subject: "New login detected",
        preview: "We noticed a new login from a device in San Francisco...",
        time: "3 days ago",
        isStarred: false,
        isUnread: false,
        tag: "Important"
    },
    {
        id: 7,
        sender: "Marketing Team",
        subject: "Campaign Draft",
        preview: "Draft copy for next week's launch is ready for your approval...",
        time: "4 days ago",
        isStarred: false,
        isUnread: false,
        tag: "Work"
    }
];

export function EmailPage() {
    const [search, setSearch] = useState("");
    const [filter] = useState("all");

    const filteredEmails = dummyEmails.filter(email =>
        (email.sender.toLowerCase().includes(search.toLowerCase()) ||
            email.subject.toLowerCase().includes(search.toLowerCase())) &&
        (filter === "all" || email.tag.toLowerCase() === filter.toLowerCase())
    );

    return (
        <div className="h-full flex flex-col bg-white/30 dark:bg-black/20 backdrop-blur-md">
            {/* Toolbar */}
            <div className="h-16 border-b border-white/20 px-6 flex items-center justify-between bg-white/40 dark:bg-black/40">
                <div className="flex items-center gap-4 flex-1">
                    <div className="relative flex-1 max-w-sm group">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-blue-500 transition-colors" />
                        <Input
                            placeholder="Search emails..."
                            className="pl-9 bg-white/50 dark:bg-black/50 border-white/20 dark:border-white/10 focus-visible:ring-blue-500/50 transition-all focus:bg-white/80 dark:focus:bg-black/80"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-primary">
                        <Filter className="h-4 w-4 mr-2" />
                        Filter
                    </Button>
                    <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-primary">
                        <ArrowUpDown className="h-4 w-4 mr-2" />
                        Sort
                    </Button>
                </div>
            </div>

            {/* Email List */}
            <ScrollArea className="flex-1">
                <div className="divide-y divide-white/10 dark:divide-white/5">
                    {filteredEmails.map((email) => (
                        <div key={email.id} className="group px-6 py-4 hover:bg-white/40 dark:hover:bg-white/5 transition-colors cursor-pointer flex items-center gap-4">
                            <div className="flex-shrink-0">
                                {email.isUnread && <div className="w-2.5 h-2.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]" />}
                            </div>

                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 flex items-center justify-center border border-white/10">
                                <span className="font-semibold text-sm text-gray-600 dark:text-gray-300">
                                    {email.sender[0]}
                                </span>
                            </div>

                            <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between mb-0.5">
                                    <h4 className={`text-sm truncate ${email.isUnread ? 'font-semibold text-foreground' : 'font-medium text-muted-foreground'}`}>
                                        {email.sender}
                                    </h4>
                                    <span className="text-xs text-muted-foreground whitespace-nowrap ml-2">
                                        {email.time}
                                    </span>
                                </div>
                                <h5 className="text-sm font-medium text-foreground/90 truncate">
                                    {email.subject}
                                </h5>
                                <p className="text-xs text-muted-foreground truncate opacity-80 group-hover:opacity-100 transition-opacity">
                                    {email.preview}
                                </p>
                            </div>

                            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-yellow-500/20 hover:text-yellow-500">
                                    <Star className={`h-4 w-4 ${email.isStarred ? 'fill-yellow-500 text-yellow-500' : ''}`} />
                                </Button>
                                <Button variant="ghost" size="icon" className="h-8 w-8">
                                    <MoreHorizontal className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    ))}

                    {filteredEmails.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
                            <Mail className="h-12 w-12 mb-4 opacity-20" />
                            <p>No emails found</p>
                        </div>
                    )}
                </div>
            </ScrollArea>
        </div>
    );
}
