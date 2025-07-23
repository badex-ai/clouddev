"use client"
import React from 'react'
import { useState } from 'react';
import { Task } from '@/lib/types';
import KanbanTable from '@/components/ui/kanbanTable';
import AddTaskModal from '@/components/ui/addTaskModal';
import { useAuthUser } from '@/contexts/userContext';


function Dashboard() {
  const { user } = useAuthUser();
 
    const [tasks, setTasks] = useState<Task[]>([
    {
      id: '1',
      title: 'Design user interface mockups',
      description: 'Create wireframes and mockups for the new dashboard',
      assignee: 'John Doe',
      dueDate: '2024-03-15',
      status: 'initialized'
    },
    {
      id: '2',
      title: 'Implement authentication system',
      description: 'Set up user login, registration, and password reset functionality',
      assignee: 'Jane Smith',
      dueDate: '2024-03-20',
      status: 'in-progress',
      checkList: [
        { id: 'check1', title: 'Create login API', completed: false },
        { id: 'check2', title: 'Implement JWT authentication', completed: false },
        { id: 'check3', title: 'Set up user roles', completed: false }
        ]
    },
    {
      id: '3',
      title: 'Set up database schema',
      description: 'Design and implement the database structure for the application',
      assignee: 'Bob Johnson',
      status: 'completed'
    },
    {
      id: '4',
      title: 'Code review process',
      description: 'Establish code review guidelines and workflow',
      assignee: 'Alice Brown',
      dueDate: '2024-03-18',
      status: 'initialized',
      checkList: [
        { id: 'item1', title: 'Review PR #123', completed: false },
        { id: 'item2', title: 'Update documentation', completed: false }
      ]
    }
  ]);

  const [showAddModal, setShowAddModal] = useState(false);
  const [addModalStatus, setAddModalStatus] = useState<string>('initialized');

  const handleTaskMove = (taskId: string, newStatus: string) => {
    setTasks(prevTasks =>
      prevTasks.map(task =>
        task.id === taskId
          ? { ...task, status: newStatus as 'initialized' | 'in-progress' | 'completed' }
          : task
      )
    );
  };

  const handleAddTask = (task: Omit<Task, 'id'>) => {
    const newTask: Task = {
      ...task,
      id: Date.now().toString()
    };
    setTasks(prev => [...prev, newTask]);
  };

  const handleAddTaskClick = (status: string) => {
    setAddModalStatus(status);
    setShowAddModal(true);
  };
  return (
   <div className="w-full h-screen bg-gray-50 p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">{user?.name}'s Board</h1>
        <p className="text-gray-600 mt-1">Manage your tasks across different stages</p>
      </div>
      
      <KanbanTable
        tasks={tasks}
        onTaskMove={handleTaskMove}
        onAddTask={handleAddTaskClick}
      />

      <AddTaskModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onAdd={handleAddTask}
        initialStatus={addModalStatus}
      />
    </div>
  )
}

export default Dashboard;