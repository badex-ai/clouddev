


"use client";
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Task, TaskStatus } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { ExtendedUserProfile } from '@/lib/types';
import {localToUtc} from'@/lib/utils'
import { toast } from "sonner"

const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200, "Title must be less than 200 characters"),
  description: z.string().optional(),
  assignee_id: z.string().min(1, "Assignee is required"),
  due_date: z.string().regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/, {
    message: "Invalid format. Use YYYY-MM-DDTHH:mm",
  })
  .refine((val) => {
    const now = new Date();
    const input = new Date(val);
    return input.getTime() - now.getTime() >= 60 * 60 * 1000; // 1 hour
  }, {
    message: "Date must be at least 1 hour from now",
  })
});


type TaskFormData = z.infer<typeof taskSchema>;

interface AddTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (task: Omit<Task, 'id'>) => void;
  assignees?: { id: number; username: string }[];
  userData: ExtendedUserProfile | null
}

const AddTaskModal: React.FC<AddTaskModalProps> = ({ 
  isOpen, 
  onClose, 
  onAdd, 
  assignees,
  userData

}) => {

  const [isLoading, setIsLoading] = useState(false)

  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: '',
      description: '',
      assignee_id: '',
      due_date: '',
    },
  });



  const   handleSubmit = async(data: TaskFormData) => {
        onAdd({
          title: data.title,
          description: data.description || undefined,
          assignee_id: parseInt(data.assignee_id), 
          due_date: data.due_date ,
          status:  'initialised' 
        });

        setIsLoading(true)

      const user = assignees?.find(user => 
      
        data.assignee_id === user.username
      );
      
      const taskData = {
        title: data.title,
        description: data.description || undefined,
        creator_id: userData?.id,
        assignee_id: user?.id,
        due_date: localToUtc(data.due_date),
        family_id: userData?.family?.id
        
      }

     console.log('taskData', taskData)

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/tasks/create`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(taskData)
      });
      
      
      const result =  await response.json()

      if(result){
        setIsLoading(false)
        form.reset();
      }

      toast.success("Task Created Successfully");
  };
   

  if (!isOpen) return null;

  return (
    
   <div className="fixed inset-0 z-50">
  {/* Backdrop - clickable area */}
  <div 
    onClick={onClose} 
    className="absolute inset-0 bg-black bg-opacity-70"
  ></div>
  
  {/* Content container - centered */}
  <div className="relative h-full flex items-center justify-center pointer-events-none">
    <Card className="w-full max-w-md mx-4 pointer-events-auto">
      <CardHeader>
        <CardTitle>Add New Task</CardTitle>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Title *</FormLabel>
                  <FormControl>
                    <Input {...field} placeholder="Enter task title" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Input {...field} placeholder="Enter task description" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="assignee_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Assign to *</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value || ""}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select an assignee" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {assignees?.map((assignee) => (
                        <SelectItem key={assignee.id} value={assignee.username}>
                          {assignee.username}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="due_date"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Due Date</FormLabel>
                  <FormControl>
                    <Input {...field} type="datetime-local" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="flex gap-2 justify-end">
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              {isLoading ? (
                <Button>...</Button>
              ) : (
                <Button type="submit" disabled={isLoading}>
                  Add Task
                </Button>
              )}
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  </div>
  </div>


  )
}


export default AddTaskModal;