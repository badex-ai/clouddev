


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
import { formatISO } from 'date-fns';

const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200, "Title must be less than 200 characters"),
  description: z.string().optional(),
  assignee_id: z.string().min(1, "Assignee is required"),
  due_date: z.string().optional(),
});
// const {userData} = useAuthUser()
// console.log(userData?.family?.id)

type TaskFormData = z.infer<typeof taskSchema>;

interface AddTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (task: Omit<Task, 'id'>) => void;
  initialStatus: string;
  assignees?: { id: string; username: string }[];
  userData: ExtendedUserProfile
}

const AddTaskModal: React.FC<AddTaskModalProps> = ({ 
  isOpen, 
  onClose, 
  onAdd, 
  initialStatus,
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
          assignee: data.assignee_id, 
          dueDate: data.due_date || undefined,
          status:  'initialised' 
        });

        setIsLoading(true)

      const user = assignees?.find(user => 
      
        data.assignee_id === user.username
      );
      // let datfmt =  formatISO(new Date(`${data.due_date})`) );
      console.log("family id",userData.family?.id)

      console.log('dateeeeeee',new Date(`${data.due_date}:00Z`)) 
      const taskData = {
        title: data.title,
        description: data.description || undefined,
        creator_id: userData.id,
        status: 'initialised',
        assignee_id: user?.id,
        due_date: `${data.due_date}:00Z`,
        family_id: userData.family?.id
        
      }
      // console.log('result of task creation', taskData)

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/tasks/create`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(taskData)
      });
      
       const result =  await response.json()
      form.reset();


    console.log("this is the data for the result",result)
    // console.log("this is the data for the form",taskData)
    
    
   
    
   




  };


    

  if (!isOpen) return null;

  
  

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md mx-4">
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
                      <Input
                        {...field}
                        placeholder="Enter task title"
                      />
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
                      <Input
                        {...field}
                        placeholder="Enter task description"
                      />
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
                    <FormLabel>Assignee *</FormLabel>
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
                      <Input
                        {...field}
                       type="datetime-local"
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