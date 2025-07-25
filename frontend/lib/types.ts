interface Task {
  id: string;
  title: string;
  description?: string;
  assignee?: string;
  dueDate?: string;
  status: 'initialized' | 'in-progress' | 'completed';
  checkList?: { id: string; title: string; completed: boolean }[];
}

interface Family {
  id: string;
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

  // ... other fields from your API
}



export type { Task, DraggableTaskProps, AddTaskModalProps, UserProfile, ExtendedUserProfile };