import * as z from 'zod';

export const taskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title must be less than 200 characters'),
  description: z.string().optional(),
  assignee_id: z.string().min(32, 'Assignee is required'),
  due_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/, {
      message: 'Invalid format. Use YYYY-MM-DDTHH:mm',
    })
    .refine(
      (val) => {
        const now = new Date();
        const input = new Date(val);
        return input.getTime() - now.getTime() >= 60 * 60 * 1000; // 1 hour
      },
      {
        message: 'Date must be at least 1 hour from now',
      }
    ),
});

export type TaskFormData = z.infer<typeof taskSchema>;

export const ChecklistSchema = z.object({
  subtask: z
    .string()
    .min(1, 'type out the subtask')
    .max(299, 'Subtask must be less that 200 characters'),
});

export type ChecklistItemForm = z.infer<typeof ChecklistSchema>;
