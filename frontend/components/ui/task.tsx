"use client";
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { GripVertical, User, Calendar } from 'lucide-react';
import { Checkbox } from "@/components/ui/checkbox"
import { Task } from '@/lib/types';



interface DraggableTaskProps {
  task: Task;
  onDragStart: (e: React.DragEvent, task: Task) => void;
  isDragging: boolean;
}


const DraggableTask: React.FC<DraggableTaskProps> = ({ task, onDragStart, isDragging }) => {
  const [checkedItems, setCheckedItems] = React.useState<string[]>(
    task.checkList?.filter(item => item.completed).map(item => item.id) || []
  );

  const handleCheck = (itemId: string, checked: boolean) => {
    setCheckedItems(prev =>
      checked ? [...prev, itemId] : prev.filter((value: string) => value !== itemId)
    );
  };

  return (
    <Card 
      draggable
      onDragStart={(e) => onDragStart(e, task)}
      className={`cursor-move transition-all duration-200 hover:shadow-md mb-3 ${
        isDragging ? 'opacity-50 transform rotate-1' : ''
      }`}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-sm font-medium line-clamp-2 flex-1">
            {task.title}
          </CardTitle>
          <GripVertical className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" />
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        {task.description && (
          <p className="text-xs text-gray-600 mb-3 line-clamp-2">
            {task.description}
          </p>
        )}
        <div className="flex flex-wrap gap-1 mb-2">
          {task.assignee && (
            <Badge variant="secondary" className="text-xs">
              <User className="w-3 h-3 mr-1" />
              {task.assignee}
            </Badge>
          )}
          {task.dueDate && (
            <Badge variant="outline" className="text-xs">
              <Calendar className="w-3 h-3 mr-1" />
              {task.dueDate}
            </Badge>
          )}
        </div>
        <Badge 
          variant={
            task.status === 'completed' ? 'default' : 
            task.status === 'in-progress' ? 'secondary' : 'outline'
          }
          className="text-xs"
        >
          {task.status.replace('-', ' ')}
        </Badge>

        <div className="mt-4">
          {task.checkList && task.checkList.length > 0 && (
            <>
              <div className="mb-1 font-semibold text-xs text-gray-500">Checklist</div>
              <form>
            {task.checkList.map((item) => (
              <div key={item.id} className="flex items-center mb-1">
                <Checkbox
                  name={`checkList.${item.id}`}
                  checked={checkedItems.includes(item.id)}
                  onCheckedChange={(checked: boolean) => handleCheck(item.id, checked)}
                />
                <label className="ml-2 text-xs text-gray-700">
                  {item.title}
                </label>
              </div>
            ))}
              </form>
            </>
          )}
        </div>
       
      </CardContent>
    </Card>
  );
};

export default DraggableTask;