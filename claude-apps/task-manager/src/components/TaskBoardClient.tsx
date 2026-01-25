'use client'

import { useState } from 'react'
import { KanbanBoard } from '@/components/KanbanBoard'
import { SummaryStats } from '@/components/SummaryStats'
import { TaskDetail } from '@/components/TaskDetail'
import { TaskListSelector } from '@/components/TaskListSelector'
import { SearchInput } from '@/components/SearchInput'
import { ThemeToggle } from '@/components/ThemeToggle'
import { useTasks } from '@/hooks/useTasks'
import { useSSE } from '@/hooks/useSSE'
import type { Task, TaskList } from '@/types/task'

interface TaskBoardClientProps {
  listId: string
  initialTasks: Task[]
  taskLists: TaskList[]
}

export function TaskBoardClient({ listId, initialTasks, taskLists }: TaskBoardClientProps) {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  // Use TanStack Query with initial data from server
  const { data: tasks } = useTasks(listId, initialTasks)

  // Enable SSE for real-time updates
  useSSE(listId)

  const currentTasks = tasks ?? initialTasks

  const handleNavigateToTask = (taskId: string) => {
    const task = currentTasks.find((t) => t.id === taskId)
    if (task) {
      setSelectedTask(task)
    }
  }

  return (
    <>
      <header className="border-b bg-card px-4 py-3">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <h1 className="text-xl font-bold">Claude Task Manager</h1>
          <div className="flex items-center gap-2 sm:gap-4">
            <TaskListSelector taskLists={taskLists} currentListId={listId} />
            <SearchInput value={searchQuery} onChange={setSearchQuery} />
            <ThemeToggle />
          </div>
        </div>
      </header>
      {currentTasks.length > 0 && <SummaryStats tasks={currentTasks} />}
      <main className={currentTasks.length > 0 ? 'h-[calc(100vh-121px)]' : 'h-[calc(100vh-65px)]'}>
        {currentTasks.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-muted-foreground">No tasks found</p>
          </div>
        ) : (
          <KanbanBoard
            tasks={currentTasks}
            searchQuery={searchQuery}
            onTaskClick={setSelectedTask}
          />
        )}
      </main>
      <TaskDetail
        task={selectedTask}
        onClose={() => setSelectedTask(null)}
        onNavigateToTask={handleNavigateToTask}
      />
    </>
  )
}
