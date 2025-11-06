import { z } from 'zod';


export const createFamilyMemberFormSchema = z.object({
  name: z
    .string()
    .min(3, "Name is required")
    .trim() // removes leading/trailing spaces
    .transform((val) => val.toLowerCase()), // converts to lowercase

  email: z
    .string()
    .min(8, "Email is required")
    .email("Invalid email address")
    .trim()
    .transform((val) => val.toLowerCase()),
});


export type CreateNewFamilyMemberFormType = z.infer<typeof createFamilyMemberFormSchema>;