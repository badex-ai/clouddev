interface Task {
  id: number;
  title: string;
  description?: string;
  assignee_id: number;
  due_date?: string;
  status: TaskStatus;
  checkList?: { id: string; title: string; completed: boolean }[];
}

interface Family {
  id: number;
  name: String;
  
}

interface DraggableTaskProps {
  task: Task;
  onDragStart: (e: React.DragEvent, task: Task) => void;
  isDragging: boolean;
}

interface AddTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (task: Omit<Task, 'id'>) => void;
  initialStatus: string;
}

type TaskStatus = "initialised" | "completed" | "in-progress"

interface UserProfile {
    sub: string;
    nickname?: string;
    picture?: string;
    email?: string;
    email_verified?: boolean;
}

  interface ExtendedUserProfile extends UserProfile {
  // Add your API-specific user fields here
  id?: string;
  family?: Family;
  name?: string;
  username?: string;
  role?: string;
  familyMembers: {id: number; username: string}[]

  // ... other fields from your API
}



export type { Task, DraggableTaskProps, AddTaskModalProps, UserProfile, ExtendedUserProfile,TaskStatus };