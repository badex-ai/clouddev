interface Task {
  id: string;
  title: string;
  description?: string;
  assignee?: string;
  dueDate?: string;
  status: 'initialized' | 'in-progress' | 'completed';
  checkList?: { id: string; title: string; completed: boolean }[];
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

interface UserProfile {
    sub: string;
    name?: string;
    nickname?: string;
    given_name?: string;
    family_name?: string;
    picture?: string;
    email?: string;
    email_verified?: boolean;
    org_id?: string;
    [key: string]: any;
}

  interface ExtendedUserProfile extends UserProfile {
  // Add your API-specific user fields here
  id?: string;
  fullName?: string;
  preferences?: any;
  role?: string;
  // ... other fields from your API
}



export type { Task, DraggableTaskProps, AddTaskModalProps, UserProfile, ExtendedUserProfile };