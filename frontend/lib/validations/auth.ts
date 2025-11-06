import { z } from "zod"

export const loginSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(6, "Password must be at least 6 characters"),
})

export const signupSchema = z
  .object({
    name: z
      .string()
      .min(1, "Full name is required")
      .trim()
      .toLowerCase(),
    
    email: z
      .string()
      .email("Invalid email address")
      .trim()
      .toLowerCase(),
    
    family_name: z
      .string()
      .min(1, "Family name is required")
      .trim()
      .toLowerCase(),

    password: z
      .string()
      .min(8, "Password must be at least 8 characters long")
      .refine((val) => {
        const lower = /[a-z]/.test(val);
        const upper = /[A-Z]/.test(val);
        const number = /[0-9]/.test(val);
        const special = /[!@#$%^&*(),.?":{}|<>]/.test(val);

        const count = [lower, upper, number, special].filter(Boolean).length;
        return count >= 3;
      }, {
        message:
          "Password must contain at least 3 of the following: lowercase, uppercase, number, or special character",
      }),

    confirmPassword: z.string().min(8, "Please confirm your password"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  })
// export type LoginFormData = z.infer<typeof loginSchema>
export type SignupFormData = z.infer<typeof signupSchema>