interface Task {
  public_id: string;
  title: string;
  description?: string;
  assignee_id: string;
  due_date: string;
  status: TaskStatus;
  checklist?: ChecklistItem[] ;
}

interface ChecklistItem { id: number; title: string; completed: boolean }

interface Family {
  id: string;
  name: string;
  members: { id: string; name: string; role: string, username: string }[];
 
  
}


interface FamilyMember{
   id: string; name: string; role: string,family_id: number, is_active: boolean, username: string,email: string }

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



interface CreateTask{
    title: string,
    description: string| undefined
    creator_id:  string
    assignee_id: string
    due_date: string
    family_id: string
}
interface UserProfile {
    sub: string
    nickname?: string
    picture?: string;
    email: string;
    email_verified: boolean;
}


  interface ExtendedUserProfile extends UserProfile {
  // Add your API-specific user fields here
  id: string;
  family: Family;
  name: string;
  username: string;
  role: string;
  // familyMembers: {id: number; username: string}[]


  // ... other fields from your API
}


interface CreateNewFamilyMember {
  name: string;
  email: string;
  family_id: number; // Optional, if the family ID is not provided
  family_name: string; // Optional, if the family name is not provided
}



export type { Task, DraggableTaskProps, AddTaskModalProps, UserProfile, ExtendedUserProfile,TaskStatus, CreateNewFamilyMember,FamilyMember,CreateTask,ChecklistItem };