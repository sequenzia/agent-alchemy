import { readdir, readFile, access } from 'node:fs/promises'
import { join, basename } from 'node:path'
import { homedir } from 'node:os'
import type { Task, TaskList, TaskStatus } from '@/types/task'

const TASKS_DIR = join(homedir(), '.claude', 'tasks')

function isValidTaskStatus(status: unknown): status is TaskStatus {
  return status === 'pending' || status === 'in_progress' || status === 'completed'
}

function parseTask(content: string, filename: string): Task | null {
  try {
    const data = JSON.parse(content)

    // Validate required fields
    if (typeof data.id !== 'string' && typeof data.id !== 'number') {
      data.id = basename(filename, '.json')
    } else {
      data.id = String(data.id)
    }

    if (typeof data.subject !== 'string') {
      console.warn(`Task ${data.id}: missing subject`)
      return null
    }

    // Normalize status
    if (!isValidTaskStatus(data.status)) {
      data.status = 'pending'
    }

    // Ensure arrays exist
    data.blocks = Array.isArray(data.blocks) ? data.blocks.map(String) : []
    data.blockedBy = Array.isArray(data.blockedBy) ? data.blockedBy.map(String) : []

    // Optional fields
    data.description = typeof data.description === 'string' ? data.description : ''
    if (data.activeForm !== undefined && typeof data.activeForm !== 'string') {
      delete data.activeForm
    }

    return data as Task
  } catch (error) {
    console.error(`Error parsing task file ${filename}:`, error)
    return null
  }
}

export async function getTaskLists(): Promise<TaskList[]> {
  try {
    await access(TASKS_DIR)
  } catch {
    console.warn(`Tasks directory not found: ${TASKS_DIR}`)
    return []
  }

  const entries = await readdir(TASKS_DIR, { withFileTypes: true })
  const taskLists: TaskList[] = []

  for (const entry of entries) {
    if (!entry.isDirectory()) continue

    const dirPath = join(TASKS_DIR, entry.name)
    try {
      const files = await readdir(dirPath)
      const jsonFiles = files.filter((f) => f.endsWith('.json'))

      if (jsonFiles.length > 0) {
        taskLists.push({
          id: entry.name,
          name: entry.name,
          taskCount: jsonFiles.length,
        })
      }
    } catch (error) {
      console.warn(`Error reading directory ${dirPath}:`, error)
    }
  }

  return taskLists.sort((a, b) => a.name.localeCompare(b.name))
}

export async function getTasks(taskListId: string): Promise<Task[]> {
  const dirPath = join(TASKS_DIR, taskListId)

  try {
    await access(dirPath)
  } catch {
    return []
  }

  const files = await readdir(dirPath)
  const jsonFiles = files.filter((f) => f.endsWith('.json'))
  const tasks: Task[] = []

  for (const file of jsonFiles) {
    try {
      const content = await readFile(join(dirPath, file), 'utf-8')
      const task = parseTask(content, file)
      if (task) {
        tasks.push(task)
      }
    } catch (error) {
      console.warn(`Error reading task file ${file}:`, error)
    }
  }

  // Sort by ID numerically if possible, otherwise alphabetically
  return tasks.sort((a, b) => {
    const aNum = parseInt(a.id, 10)
    const bNum = parseInt(b.id, 10)
    if (!isNaN(aNum) && !isNaN(bNum)) {
      return aNum - bNum
    }
    return a.id.localeCompare(b.id)
  })
}

export async function getTask(
  taskListId: string,
  taskId: string
): Promise<Task | null> {
  const filePath = join(TASKS_DIR, taskListId, `${taskId}.json`)

  try {
    const content = await readFile(filePath, 'utf-8')
    return parseTask(content, `${taskId}.json`)
  } catch {
    return null
  }
}

export function getTasksDir(): string {
  return TASKS_DIR
}
