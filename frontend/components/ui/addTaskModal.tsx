


"use client";
import { useState } from 'react';
// 🔥 Added React Hook Form and Zod imports
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Input } from '@/components/ui/input';
// 🔥 Added Select component imports
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
// 🔥 Added Form components
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Task } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { useAuthUser } from '@/contexts/userContext';

// 🔥 Added Zod schema
const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200, "Title must be less than 200 characters"),
  description: z.string().optional(),
  assignee_id: z.string().min(1, "Assignee is required"),
  due_date: z.string().optional(),
});
const {userData} = useAuthUser()
console.log(userData?.family?.id)

type TaskFormData = z.infer<typeof taskSchema>;

interface AddTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (task: Omit<Task, 'id'>) => void;
  initialStatus: string;
  // 🔥 Added assignees prop for dropdown options
  assignees?: { id: string; name: string }[];
}

const AddTaskModal: React.FC<AddTaskModalProps> = ({ 
  isOpen, 
  onClose, 
  onAdd, 
  initialStatus,
  // 🔥 Added default empty array for assignees
  assignees = []
}) => {

  // 🔥 Replaced useState with useForm
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: '',
      description: '',
      assignee_id: '',
      due_date: '',
    },
  });

  // 🔥 Updated handleSubmit to use React Hook Form
  const handleSubmit = (data: TaskFormData) => {
    onAdd({
      title: data.title,
      description: data.description || undefined,
      assignee: data.assignee_id, // This will be mapped to assignee_id programmatically
      dueDate: data.due_date || undefined,
      status: initialStatus as 'initialized'
    });
    // 🔥 Reset form instead of individual state setters
    form.reset();
    onClose();
    console.log()

    //  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/tasks/create`, {
    //     method: 'POST', 
    //     headers: {
    //       'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify({
    //       family_id: userData?.family?.id,
    //       date: selectedDate,

    //     }),
    //   });


  };


    

  if (!isOpen) return null;

  
  

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md mx-4">
        <CardHeader>
          <CardTitle>Add New Task</CardTitle>
        </CardHeader>
        <CardContent>
          {/* 🔥 Wrapped form content with Form component */}
          <Form {...form}>
            <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
              {/* 🔥 Converted title field to use FormField */}
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Title *</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        placeholder="Enter task title"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              {/* 🔥 Converted description field to use FormField */}
              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        placeholder="Enter task description"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              {/* 🔥 Changed assignee input to Select dropdown */}
              <FormField
                control={form.control}
                name="assignee_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Assignee *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select an assignee" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {assignees.map((assignee) => (
                          <SelectItem key={assignee.id} value={assignee.id}>
                            {assignee.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              {/* 🔥 Converted due date field to use FormField */}
              <FormField
                control={form.control}
                name="due_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Due Date</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        type="date"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="outline" onClick={onClose}>
                  Cancel
                </Button>
                {/* 🔥 Changed to submit type */}
                <Button type="submit">Add Task</Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
};

export default AddTaskModal;