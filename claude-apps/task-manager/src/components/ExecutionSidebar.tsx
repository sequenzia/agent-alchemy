'use client'

import { useState } from 'react'
import { X } from 'lucide-react'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Button } from '@/components/ui/button'
import type { ExecutionContext } from '@/types/execution'

interface ExecutionSidebarProps {
  executionContext: ExecutionContext | null
  open: boolean
  onClose: () => void
}

const TAB_LABELS: Record<string, string> = {
  execution_context: 'Context',
  task_log: 'Log',
  execution_plan: 'Plan',
  session_summary: 'Summary',
}

function getTabLabel(name: string): string {
  return TAB_LABELS[name] ?? name.replace(/_/g, ' ')
}

export function ExecutionSidebar({
  executionContext,
  open,
  onClose,
}: ExecutionSidebarProps) {
  const [activeTab, setActiveTab] = useState<string | null>(null)

  if (!open || !executionContext) return null

  const { artifacts } = executionContext
  const currentTab = activeTab ?? artifacts[0]?.name ?? null
  const currentArtifact = artifacts.find((a) => a.name === currentTab)

  return (
    <div className="flex flex-col h-full w-[440px] border-l bg-card">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <h2 className="text-sm font-semibold">Execution Context</h2>
        <Button variant="ghost" size="icon" onClick={onClose} className="h-7 w-7">
          <X className="h-4 w-4" />
          <span className="sr-only">Close sidebar</span>
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex border-b px-2 gap-1 overflow-x-auto">
        {artifacts.map((artifact) => (
          <button
            key={artifact.name}
            onClick={() => setActiveTab(artifact.name)}
            className={`px-3 py-2 text-xs font-medium whitespace-nowrap transition-colors border-b-2 ${
              currentTab === artifact.name
                ? 'border-primary text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground hover:border-muted-foreground/50'
            }`}
          >
            {getTabLabel(artifact.name)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {currentArtifact ? (
          <div className="prose prose-sm dark:prose-invert max-w-none prose-headings:text-sm prose-headings:font-semibold prose-p:text-sm prose-p:leading-relaxed prose-code:text-xs prose-pre:text-xs prose-pre:bg-muted prose-pre:border prose-table:text-xs prose-th:px-2 prose-th:py-1 prose-td:px-2 prose-td:py-1 prose-table:border-collapse [&_table]:w-full [&_th]:border [&_td]:border [&_th]:border-border [&_td]:border-border [&_th]:bg-muted">
            <Markdown remarkPlugins={[remarkGfm]}>
              {currentArtifact.content}
            </Markdown>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">No content available</p>
        )}
      </div>
    </div>
  )
}
