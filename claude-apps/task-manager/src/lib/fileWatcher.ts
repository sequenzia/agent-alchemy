import { watch, type FSWatcher } from 'chokidar'
import { EventEmitter } from 'node:events'
import { readFile } from 'node:fs/promises'
import { homedir } from 'node:os'
import { join, basename, dirname } from 'node:path'
import type { Task, SSEEventType } from '@/types/task'

export interface FileWatcherEvent {
  type: SSEEventType
  taskListId: string
  taskId: string
  task?: Task
}

export class FileWatcher extends EventEmitter {
  private watcher: FSWatcher | null = null
  private readonly basePath: string
  private started = false

  constructor() {
    super()
    this.basePath = join(homedir(), '.claude', 'tasks')
  }

  async start(): Promise<void> {
    if (this.started) {
      return
    }

    // Watch the base directory directly - more reliable than glob patterns
    this.watcher = watch(this.basePath, {
      persistent: true,
      ignoreInitial: true,
      usePolling: true,
      interval: 300,
      depth: 2,
    })

    this.watcher
      .on('add', (path) => {
        if (!path.endsWith('.json')) return
        this.handleFileChange('task:created', path)
      })
      .on('change', (path) => {
        if (!path.endsWith('.json')) return
        this.handleFileChange('task:updated', path)
      })
      .on('unlink', (path) => {
        if (!path.endsWith('.json')) return
        this.handleFileDelete(path)
      })
      .on('error', (error) => console.error('File watcher error:', error))

    this.started = true
    console.log(`File watcher started: watching ${this.basePath}`)
  }

  private async handleFileChange(
    type: 'task:created' | 'task:updated',
    filePath: string
  ): Promise<void> {
    try {
      const taskId = basename(filePath, '.json')
      const taskListId = basename(dirname(filePath))

      const content = await readFile(filePath, 'utf-8')
      const task = JSON.parse(content) as Task

      const event: FileWatcherEvent = {
        type,
        taskListId,
        taskId,
        task,
      }

      this.emit('taskEvent', event)
    } catch (error) {
      console.error(`Error processing file change: ${filePath}`, error)
    }
  }

  private handleFileDelete(filePath: string): void {
    const taskId = basename(filePath, '.json')
    const taskListId = basename(dirname(filePath))

    const event: FileWatcherEvent = {
      type: 'task:deleted',
      taskListId,
      taskId,
    }

    this.emit('taskEvent', event)
  }

  async stop(): Promise<void> {
    if (this.watcher) {
      await this.watcher.close()
      this.watcher = null
      this.started = false
      console.log('File watcher stopped')
    }
  }

  getBasePath(): string {
    return this.basePath
  }

  isStarted(): boolean {
    return this.started
  }
}

// Global singleton pattern for development hot reload
// This prevents multiple file watchers from being created during Next.js HMR
const globalForWatcher = globalThis as unknown as {
  fileWatcher: FileWatcher | undefined
}

export const fileWatcher = globalForWatcher.fileWatcher ?? new FileWatcher()

if (process.env.NODE_ENV !== 'production') {
  globalForWatcher.fileWatcher = fileWatcher
}
