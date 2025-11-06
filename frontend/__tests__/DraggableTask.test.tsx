import { render, screen, fireEvent } from '@testing-library/react'
import DraggableTask from '@/components/ui/taskComponent'
import userEvent from '@testing-library/user-event'
import { Task, TaskStatus } from '@/lib/types'
import '@testing-library/jest-dom'
import { useAuthUser } from '@/contexts/userContext'
import { utcToLocal } from '@/lib/utils';

// Mock the useAuthUser hook
jest.mock('@/contexts/userContext', () => ({
  useAuthUser: jest.fn(),
}))

// Mock task data according to actual Task type
const mockTask: Task = {
  public_id: '1',
  title: 'Test Task',
  description: 'Test Description',
  status: 'initialised' as TaskStatus,
  assignee_id: '123',
  due_date: new Date().toISOString().slice(0, 16), // Format: YYYY-MM-DDTHH:mm
  checklist: [
    { id: 1, title: 'Subtask 1', completed: false },
    { id: 2, title: 'Subtask 2', completed: true },
  ]
}

// Mock family member data
const mockFamilyMember = {
  id: '123',
  username: 'John Doe',
  email: 'john@example.com',
  role: 'member'
}

// Mock the handlers
const mockDragStart = jest.fn()
const mockDeleteTask = jest.fn()
const mockTaskUpdate = jest.fn()

// Set up useAuthUser mock return value
beforeEach(() => {
  (useAuthUser as jest.Mock).mockReturnValue({
    userData: {
      family: {
        members: [mockFamilyMember]
      }
    }
  })
})

describe('TaskComponent', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders task details correctly', () => {
    render(
      <DraggableTask
        task={mockTask}
        onDragStart={mockDragStart}
        isDragging={false}
        onDeleteTask={mockDeleteTask}
        onTaskUpdate={mockTaskUpdate}
      />
    )

    // Check if essential task information is displayed
    expect(screen.getByText(mockTask.title)).toBeInTheDocument()
    if (mockTask.description) {
      expect(screen.getByText(mockTask.description)).toBeInTheDocument()
    }
    expect(screen.getByText(mockTask.status.replace('-', ' '))).toBeInTheDocument()
  })

  it('handles drag start correctly', async () => {
    render(
      <DraggableTask
        task={mockTask}
        onDragStart={mockDragStart}
        isDragging={false}
        onDeleteTask={mockDeleteTask}
        onTaskUpdate={mockTaskUpdate}
      />
    )

    const taskCard = screen.getByText(mockTask.title).closest('.cursor-move')
    if (!taskCard) throw new Error('Task card not found')
    
    fireEvent.dragStart(taskCard)
    expect(mockDragStart).toHaveBeenCalledWith(expect.any(Object), mockTask)
  })

  it('calls deleteTask when delete button is clicked', async () => {
    render(
      <DraggableTask
        task={mockTask}
        onDragStart={mockDragStart}
        isDragging={false}
        onDeleteTask={mockDeleteTask}
        onTaskUpdate={mockTaskUpdate}
      />
    )

    // Find and click delete button
    const deleteButton = screen.getByTitle('Delete task')
    await userEvent.click(deleteButton)

    // Verify deleteTask was called with correct task id
    expect(mockDeleteTask).toHaveBeenCalledWith(mockTask.public_id)
  })

  it('displays assigned user information', () => {
    render(
      <DraggableTask
        task={mockTask}
        onDragStart={mockDragStart}
        isDragging={false}
        onDeleteTask={mockDeleteTask}
        onTaskUpdate={mockTaskUpdate}
      />
    )

    expect(screen.getByText(mockFamilyMember.username)).toBeInTheDocument()
  })

  it('displays and handles checklist items', () => {
    render(
      <DraggableTask
        task={mockTask}
        onDragStart={mockDragStart}
        isDragging={false}
        onDeleteTask={mockDeleteTask}
        onTaskUpdate={mockTaskUpdate}
      />
    )

    // Check if checklist section is displayed
    expect(screen.getByText('Checklist')).toBeInTheDocument()
    
    // Check individual items
     mockTask.checklist?.forEach(item => {
    expect(screen.getByText(item.title)).toBeInTheDocument()
    const checkbox = screen.getByRole('checkbox', { name: item.title })
    expect(checkbox).toBeInTheDocument()
    
    // Use toBeChecked() or not.toBeChecked() instead of toHaveProperty
    if (item.completed) {
      expect(checkbox).toBeChecked()
    } else {
      expect(checkbox).not.toBeChecked()
    }
    })
  })

  it('displays formatted due date correctly', () => {
    render(
      <DraggableTask
        task={mockTask}
        onDragStart={mockDragStart}
        isDragging={false}
        onDeleteTask={mockDeleteTask}
        onTaskUpdate={mockTaskUpdate}
      />
    )

    const formattedDate =  utcToLocal(mockTask.due_date)
    expect(screen.getByTitle(/due date/i)).toHaveTextContent(formattedDate)
  })
})