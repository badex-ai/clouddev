'use client';
import React, { useState, useEffect } from 'react';
import { useAuthUser } from '@/contexts/userContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';
import { Users, Plus, Mail, User, MoreVertical, Minus } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { createNewFamilyMember } from '@/lib/actions/userActions';
import {
  createFamilyMemberFormSchema,
  CreateNewFamilyMemberFormType,
} from '@/lib/validations/user';
import { CreateNewFamilyMember, FamilyMember } from '@/lib/types';
import {
  getFamilymembers,
  deactivateFamilymember,
  reactivateFamilymember,
} from '@/lib/actions/userActions';
import { cn } from '@/lib/utils';
import * as changeCase from "change-case";


export default function MemberSettingsPage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [submitIsLoading, setSubmitIsLoading] = useState(false);
  const [membersLoading, setMembersLoading] = useState(true);

  const [familyMembers, setFamilyMembers] = useState<Array<FamilyMember>>([]);

  const { userData } = useAuthUser();

  const {
    register,
    handleSubmit,
    formState: {},
  } = useForm<CreateNewFamilyMemberFormType>({
    resolver: zodResolver(createFamilyMemberFormSchema),
  });

  useEffect(() => {
    const fetchFamilyMembers = async () => {
      if (!userData?.family) {
        return;
      }

      try {
        const family = await getFamilymembers(userData?.family?.id);
        // console.log('familyMembers', family)

        const familyMembers = family.users;

        setFamilyMembers(familyMembers);
      } catch (e) {
        // console.log('Error fetching family members:', e);
        toast.error('Sometin went wron wile fetcin family member. Please try again.');
      } finally {
        setMembersLoading(false);
      }
    };
    if (userData?.family?.id) {
      fetchFamilyMembers();
    }
  }, []);

  useEffect(() => {}, [submitIsLoading]);

  // console.log(familyMembers)

  const onFormSubmit = async (data: CreateNewFamilyMemberFormType) => {
    setSubmitIsLoading(true);
    console.log('data from the form', data);

    try {
      if (!userData?.family || !userData?.family?.id || !userData?.family?.name) {
        toast('Family information is missing. Please refresh and try again.');
        return;
      }

      const newData: CreateNewFamilyMember = {
        ...data,
        family_id: userData.family.id,
        family_name: userData.family.name,
      };

      const newMember = await createNewFamilyMember(newData);

      // console.log(newMember, 'newly created familyMember');

      if (newMember) {
        setFamilyMembers((prevMembers) => [...prevMembers, newMember]);

        toast('Family Member Created', {
          description: 'A new family member was added successfully.',
          action: {
            label: "Close",
            onClick: () => {
              toast.dismiss();
            },
          },
          duration: 4000,
        });
        
        setIsDialogOpen(false);
      }
    } catch (error) {
      // console.log(error, 'tis is te error ');
     
      const message = error instanceof Error ? error.message : String(error); 
      toast('Reactivation failed', {
       description: message,
       action: {
         label: 'Close',
         onClick: () => {
            toast.dismiss();
          },
        },
       duration: 4000,
     });
      
    } finally {
      setSubmitIsLoading(false);
    }
  };

  async function handleDeactivateFamilyMember(memberId: string) {
    // console.log(memberId, 'this is the member id');

    try {
      if (!memberId) {
        console.log('No memberId provided');
        return;
      }

      console.log('About to call deactivateFamilymember');
      const result = await deactivateFamilymember(memberId);
      console.log(result, 'result for deactivating family member');

      // Check for success property instead of truthy result
      
        toast('Family member created', {
                description: 'Your ave successfully created a new family member' ,
                action: {
                  label: "Close",
                  onClick: () => {
                    toast.dismiss();
                  },
                },
                duration: 4000, // in ms (default is 4000)
              });
        

        setFamilyMembers((prev) =>
          prev.map((member) =>
            member.public_id === memberId ? { ...member, is_active: false } : member
          )
        );
      
    } catch (error) {
      console.error('Error deactivating family member:', error);
      // toast(error.message || 'Failed to deactivate family member. Please try again.');

      const message = error instanceof Error ? error.message : String(error);
        toast('Deactivation failed', {
          description: message,
          action: {
            label: "Close",
            onClick: () => {
              toast.dismiss();
            },
          },
          duration: 4000, // in ms (default is 4000)
        });

    }
  }

  async function handleReactivateFamilyMember(memberId: string) {
    console.log(memberId, 'this is the member id');

    try {
      if (!memberId) return;

      await reactivateFamilymember(memberId);

      toast('Family Member Reactivated', {
        description: 'The family member was reactivated successfully.',
        action: {
          label: "Close",
          onClick: () => {
            toast.dismiss();
          },
        },
        duration: 4000,
      });

      setFamilyMembers((prev) =>
        prev.map((member) =>
          member.public_id === memberId ? { ...member, is_active: true } : member
        )
      );
    } catch (error) {
      console.error('Error reactivating family member:', error);

      const message = error instanceof Error ? error.message : String(error);
      toast('Reactivation failed', {
        description: message,
        action: {
          label: 'Close',
          onClick: () => {
            toast.dismiss();
          },
        },
        duration: 4000,
      });
    }
  }

  // console.log(familyMembers, "tis are te family members")

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Family Members</h1>
        <p className="text-muted-foreground mt-2">Manage family members and their roles.</p>
      </div>

      {/* Add New Family Member Button */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Users className="h-5 w-5" />
          <h2 className="text-xl font-semibold">Family Members List</h2>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Add New Family Member
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Add New Family Member</DialogTitle>
              <DialogDescription>
                Enter the details for the new family member. They will receive an invitation via
                email.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label htmlFor="member-name">Name</Label>
                <Input
                  id="member-name"
                  placeholder="Enter full name"
                  {...register('name')}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="member-email">Email</Label>
                <Input
                  id="member-email"
                  type="email"
                  placeholder="Enter email address"
                  {...register('email')}
                  required
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                {/* <Loader2 className="mr-2 h-4 w-4 animate-spin" /> */}
                <Button type="submit" disabled={submitIsLoading}>
                  {submitIsLoading ? '...loading' : 'Create Member'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Family Members List */}
      <div className="space-y-6">
        {!membersLoading &&
          familyMembers &&
          familyMembers.map((member) => (
            <div
              key={member.public_id}
              className={cn(
                'p-4 rounded-lg transition-colors',
                member.is_active
                  ? 'hover:bg-muted/50 text-black-500'
                  : 'hover:bg-muted/30 opacity-60 text-gray-400'
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <User className="h-6 w-6 text-primary" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="font-semibold text-lg">{changeCase.capitalCase(member.name)}</h3>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Mail className="h-3 w-3" />
                      {member.email}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Badge variant={member.role === 'Admin' ? 'default' : 'secondary'}>
                    {member.role}
                  </Badge>

                  {!member.is_active && <Badge variant={'default'}>deactivated</Badge>}

                  {member.role != 'admin' && member.is_active && (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm" aria-label="Open menu">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={() => {
                            // e.preventDefault();
                            console.log('clicked my boy');
                            handleDeactivateFamilyMember(member.public_id);
                          }}
                          className="flex items-center gap-2 text-destructive"
                        >
                          <Minus className="h-4 w-4" />
                          Deactivate Member
                        </DropdownMenuItem>
                        {/* <DropdownMenuItem onClick={() => handleDeleteFamilyMember(member.public_id)} className="flex items-center gap-2 text-destructive">
                      <Trash2 className="h-4 w-4" />
                      Delete Member
                    </DropdownMenuItem> */}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  )}

                  {member.role != 'admin' && !member.is_active && (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm" aria-label="Open menu" >
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onSelect={(e) => {
                            e.preventDefault();
                            handleReactivateFamilyMember(member.public_id);
                          }}
                          className="flex items-center gap-2 text-success"
                        >
                          <Plus className="h-4 w-4" />
                          Activate Member
                        </DropdownMenuItem>
                        {/* <DropdownMenuItem onClick={() => handleDeleteFamilyMember(member.public_id)} className="flex items-center gap-2 text-destructive">
                      <Trash2 className="h-4 w-4" />
                      Delete Member
                    </DropdownMenuItem> */}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  )}
                </div>
              </div>
            </div>
          ))}
      </div>

      {!membersLoading && familyMembers?.length === 0 && (
        <div className="text-center py-12">
          <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No family members yet</h3>
          <p className="text-muted-foreground mb-4">Start by adding your first family member</p>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add First Member
              </Button>
            </DialogTrigger>
          </Dialog>
        </div>
      )}
    </div>
  );
}
