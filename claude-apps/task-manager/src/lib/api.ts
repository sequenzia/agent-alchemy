import type { Task, TaskList } from '@/types/task'

const API_BASE = '/api'

export interface TaskListsResponse {
  taskLists: TaskList[]
}

export interface TasksResponse {
  tasks: Task[]
}

export async function fetchTaskLists(): Promise<TaskList[]> {
  const response = await fetch(`${API_BASE}/task-lists`)
  if (!response.ok) {
    throw new Error(`Failed to fetch task lists: ${response.statusText}`)
  }
  const data: TaskListsResponse = await response.json()
  return data.taskLists
}

export async function fetchTasks(taskListId: string): Promise<Task[]> {
  const response = await fetch(`${API_BASE}/tasks/${encodeURIComponent(taskListId)}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch tasks: ${response.statusText}`)
  }
  const data: TasksResponse = await response.json()
  return data.tasks
}
