import { z } from 'zod';


export const createFamilyMemberFormSchema = z.object({
    name: z.string().min(3, "Name is required"),
    email: z.string().min(3, "Email is required").email("Invalid email address")
});

export type CreateNewFamilyMemberFormType = z.infer<typeof createFamilyMemberFormSchema>;