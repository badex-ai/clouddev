'use client';
import React, { EventHandler, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { GripVertical, User, Calendar } from 'lucide-react';
import { Checkbox } from '@/components/ui/checkbox';
import { Task } from '@/lib/types';
import { utcToLocal } from '@/lib/utils';
import { Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuthUser } from '@/contexts/userContext';
import { Plus } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { addCheckListItem, deleteCheckListItem } from '@/lib/actions/taskActions';
import { ChecklistItemForm, ChecklistSchema } from '@/lib/validations/task';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Label } from '@/components/ui/label'

interface DraggableTaskProps {
  task: Task;
  onDragStart: (e: React.DragEvent, task: Task) => void;
  isDragging: boolean;
  onDeleteTask: (taskId: string) => void;
  onTaskUpdate: (updatedTask: Task) => void;
}

const DraggableTask: React.FC<DraggableTaskProps> = ({
  task,
  onDragStart,
  isDragging,
  onDeleteTask,
  onTaskUpdate,
}) => {
  const { userData } = useAuthUser();
  const [openAddChecklistItem, setOpenAddChecklistItem] = useState(false);
  const [addToCheckListLoading, setAddToCheckListLoading] = useState(false);

  const assingedUser = userData?.family?.members.filter((member) => {
    return member.id == task.assignee_id;
  })[0];
  const [checkedItems, setCheckedItems] = React.useState<string[]>(
    task.checklist?.filter((item) => item.completed).map((item) => item.id.toString()) || []
  );

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ChecklistItemForm>({
    resolver: zodResolver(ChecklistSchema),
  });

  const handleCheck = (itemId: string, checked: boolean) => {
    setCheckedItems((prev) =>
      checked ? [...prev, itemId] : prev.filter((value: string) => value !== itemId)
    );
  };

  const handleAddChecklist = () => {
    setOpenAddChecklistItem(true);
  };

  const handleDelectChecklistItem = async (taskId: string, itemId: number) => {
    // console.log('checklist ietem deleted', taskId)
    try {
      const result = await deleteCheckListItem(taskId, itemId);
      if (result.ok) {
        const updatedTask = await result.json();
        onTaskUpdate(updatedTask);
      }
    } catch {
      // console.log()
    }
  };

  const onSubmitChecklist = async (data: ChecklistItemForm) => {
    try {
      setAddToCheckListLoading(true);

      const newCheckList = {
        id: task.checklist ? task.checklist.length + 1 : 1,
        title: data.subtask,
        completed: false,
      };

      const result = await addCheckListItem(task.public_id, newCheckList);
      // Handle successful submission

      const updatedTask = await result.json();
      reset(); // Reset the form after successful submission
      setOpenAddChecklistItem(false);
      onTaskUpdate(updatedTask);
    } catch (error) {
      console.error('Error adding checklist item:', error);
    } finally {
      setAddToCheckListLoading(false);
    }
  };

  // This function handles Enter key press to trigger form submission
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault(); // Prevent default to avoid any unwanted behavior
      handleSubmit(onSubmitChecklist)(); // Manually trigger form submission
    }
  };

  return (
    <div className="relative">
      <Card
        draggable
        onDragStart={(e) => onDragStart(e, task)}
        className={`cursor-move transition-all duration-200 hover:shadow-md mb-3 ${
          isDragging ? 'opacity-50 transform rotate-1' : ''
        }`}
      >
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between">
            <CardTitle className="text-sm font-medium line-clamp-2 flex-1">{task.title}</CardTitle>
            <GripVertical className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" />
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          {task.description && (
            <p className="text-xs text-gray-600 mb-3 line-clamp-2">{task.description}</p>
          )}
          <div className="flex flex-wrap gap-1 mb-2">
            {task.assignee_id && (
              <Badge variant="secondary" className="text-xs">
                <User className="w-3 h-3 mr-1" />
                {assingedUser?.username}
              </Badge>
            )}
            {task.due_date && (
              <Badge variant="outline"  title="Due date"className="text-xs">
                <Calendar className="w-3 h-3 mr-1" />
                {`${utcToLocal(task.due_date)}`}
              </Badge>
            )}
          </div>
          <Badge
            variant={
              task.status === 'completed'
                ? 'default'
                : task.status === 'in-progress'
                  ? 'secondary'
                  : 'outline'
            }
            className="text-xs"
          >
            {task.status.replace('-', ' ')}
          </Badge>

          <div className="mt-4 relative">
            <div className=" mb-4">
              <Button
                variant="ghost"
                size="sm"
                title="Add checklist"
                onClick={() => handleAddChecklist()}
              >
                <div>
                  <svg fill="#000000" viewBox="0 0 1920 1920" xmlns="http://www.w3.org/2000/svg">
                    <g id="SVGRepo_bgCarrier" strokeWidth="0"></g>
                    <g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g>
                    <g id="SVGRepo_iconCarrier">
                      {' '}
                      <path
                        d="M459.897 902.842v689.845h1034.767v-574.87h230.064v804.819H229.948V902.842h229.949Zm1299.37-570.916L1920 496.455l-845.06 825.86-408.044-398.846 160.85-164.413 247.194 241.675 684.326-668.805ZM459.896 98v230.063H689.96v229.949H459.897v229.833H229.948V558.012H0V328.063h229.948V98h229.949Zm919.816 229.983V557.93h-574.87V327.983h574.87Z"
                        fillRule="evenodd"
                      ></path>{' '}
                    </g>
                  </svg>
                </div>
                <Plus className="h-4 w-4 text-gray-600 " />
              </Button>
              {openAddChecklistItem && (
                <div className="z-4 w-[14rem] bg-gray py-1 px-2 absolute top-[0] left-[40]">
                  <form onSubmit={handleSubmit(onSubmitChecklist)}>
                    <Input
                      {...register('subtask')}
                      onKeyDown={handleKeyPress}
                      className="h-7"
                      placeholder="add new check item"
                      autoFocus
                    />
                    {errors.subtask && (
                      <p className="text-red-500 text-xs mt-1">{errors.subtask.message}</p>
                    )}
                  </form>
                </div>
              )}
            </div>
            {task.checklist && task.checklist.length > 0 && (
              <>
                <div className="mb-1 font-semibold text-xs text-gray-500">Checklist</div>

                {task.checklist.map((item) => (
                  <div key={item.id} className="flex items-center mb-1">
                    <Checkbox
                       id={`checklist-${item.id}`}  
                      name={`checklist.${item.id}`}
                      checked={checkedItems.includes(item.id.toString())}
                      onCheckedChange={(checked: boolean) =>
                        handleCheck(item.id.toString(), checked)
                      }
                    />
                    <Label 
          htmlFor={`checklist-${item.id}`}
          className="ml-2 text-sm text-gray-700"
        >
          {item.title}
        </Label>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      title="Delete ChecklistItem"
                      onClick={() => handleDelectChecklistItem(task.public_id, item.id)}
                    >
                      <Trash2 className="h-4 w-4 text-gray-600 " />
                    </Button>
                  </div>
                ))}
              </>
            )}
          </div>
        </CardContent>
      </Card>
      <div className="absolute top-4 right-15">
        <Button
          variant="ghost"
          size="sm"
          title="Delete task"
          onClick={() => onDeleteTask(task.public_id)}
        >
          <Trash2 className="h-4 w-4 text-gray-600 " />
        </Button>
      </div>
    </div>
  );
};

export default DraggableTask;
