import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Task } from '@/lib/types';
import { Badge } from '@/components/ui/badge';
import DraggableTask  from '@/components/ui/task';

interface KanbanTableProps {
  tasks: Task[];
  onTaskMove: (taskId: string, newStatus: string) => void;

}

const KanbanTable: React.FC<KanbanTableProps> = ({ tasks, onTaskMove}) => {
  const [draggingTask, setDraggingTask] = useState<Task | null>(null);
  const [dragOverColumn, setDragOverColumn] = useState<string | null>(null);

  const handleDragStart = (e: React.DragEvent, task: Task) => {
    setDraggingTask(task);
    e.dataTransfer.setData('text/plain', task.id);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent, newStatus: string) => {
    e.preventDefault();
    const taskId = e.dataTransfer.getData('text/plain');
    onTaskMove(taskId, newStatus);
    setDraggingTask(null);
    setDragOverColumn(null);
  };

  const handleDragEnter = (status: string) => {
    setDragOverColumn(status);
  };

  const handleDragLeave = () => {
    setDragOverColumn(null);
  };

  const getTasksByStatus = (status: string) => {
    return tasks.filter(task => task.status === status);
  };

  const getColumnBgColor = (status: string) => {
    switch (status) {
      case 'initialized': return 'bg-gray-50';
      case 'in-progress': return 'bg-blue-50';
      case 'completed': return 'bg-green-50';
      default: return 'bg-gray-50';
    }
  };

  const getColumnBorderColor = (status: string, isDragOver: boolean) => {
    if (isDragOver) return 'border-blue-400 border-2';
    switch (status) {
      case 'initialized': return 'border-gray-200';
      case 'in-progress': return 'border-blue-200';
      case 'completed': return 'border-green-200';
      default: return 'border-gray-200';
    }
  };

  const columns = [
    { title: 'Initialized', status: 'initialized' },
    { title: 'In Progress', status: 'in-progress' },
    { title: 'Completed', status: 'completed' }
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-[calc(100vh-120px)]">
      {/* Table Header */}
      <div className="grid grid-cols-3 border-b border-gray-200">
        {columns.map((column) => (
          <div
            key={column.status}
            className="p-4 border-r border-gray-200 last:border-r-0"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <h2 className="font-semibold text-gray-700 uppercase text-sm tracking-wide">
                  {column.title}
                </h2>
                <Badge variant="secondary" className="text-xs">
                  {getTasksByStatus(column.status).length}
                </Badge>
              </div>
             
              
            </div>
          </div>
        ))}
      </div>

      {/* Table Body */}
      <div className="grid grid-cols-3 h-full">
        {columns.map((column) => (
          <div
            key={column.status}
            className={`border-r border-gray-200 last:border-r-0 transition-all duration-200 ${getColumnBgColor(column.status)} ${getColumnBorderColor(column.status, dragOverColumn === column.status)}`}
            onDrop={(e) => handleDrop(e, column.status)}
            onDragOver={handleDragOver}
            onDragEnter={() => handleDragEnter(column.status)}
            onDragLeave={handleDragLeave}
          >
            <div className="p-4 h-full overflow-y-auto">
              {getTasksByStatus(column.status).map((task) => (
                <DraggableTask
                  key={task.id}
                  task={task}
                  onDragStart={handleDragStart}
                  isDragging={draggingTask?.id === task.id}
                />
              ))}
              {getTasksByStatus(column.status).length === 0 && (
                <div className="flex items-center justify-center h-40 text-gray-400 text-sm">
                  <div className="text-center">
                    <div className="mb-2">No tasks</div>
                    <div className="text-xs">Drop tasks here</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export  default KanbanTable;