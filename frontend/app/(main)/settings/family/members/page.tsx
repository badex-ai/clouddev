'use client'
import React,{useState, useEffect} from 'react'
import { useAuthUser } from '@/contexts/userContext'
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { 
  Users, 
  Plus, 
  Mail, 
  User,
  MoreVertical,
  Trash2,
  Edit
} from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';


export default function MemberSettingsPage() {

 const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
   const [familyMembers, setFamilyMembers] = useState([
    { id: 1, name: 'John Doe', email: 'john.doe@email.com', role: 'Admin' },
    { id: 2, name: 'Jane Smith', email: 'jane.smith@email.com', role: 'Member' },
    { id: 3, name: 'Mike Johnson', email: 'mike.johnson@email.com', role: 'Member' }
  ]);

  const { userData } = useAuthUser();

  console.log('userData', userData);

  useEffect(() => {
  //     const getFamilyMembers = async () =>   {
  //             try{
  //             const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/tasks/date`, {
  //                 method: 'POST', 
  //                 headers: {
  //                   'Content-Type': 'application/json',
  //                 },
  //                 body: JSON.stringify({
  //                   family_id: userData?.family?.id,
                  
  //                 }),
  //               });
  //         }catch{}
          

  // }


    // getFamilyMembers();
  }, [])


    const createNewMember = () => {
    console.log('Creating new family member:', { name, email });
    
    // Add the new member to the list
    const newMember = {
      id: familyMembers.length + 1,
      name,
      email,
      role: 'Member'
    };
    
    setFamilyMembers([...familyMembers, newMember]);
    
    // Reset form and close dialog
    setName('');
    setEmail('');
    setIsDialogOpen(false);
  };

  // const familyMembers = userData?.family?.members

  const handleSubmit = (e) => {
    e.preventDefault();
    if (name.trim() && email.trim()) {
      createNewMember();
    }
  };

  

 

  // const familyList = familyMembers?.map(member => (
  //   <li key={member.id}>
  //     {member.name} - {member.role}
  //   </li>
  // ));


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
                Enter the details for the new family member. They will receive an invitation via email.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 pt-4">
              <div className="space-y-2">
                <Label htmlFor="member-name">Name</Label>
                <Input
                  id="member-name"
                  placeholder="Enter full name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="member-email">Email</Label>
                <Input
                  id="member-email"
                  type="email"
                  placeholder="Enter email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setIsDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit">
                  Create Member
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Family Members List */}
      <div className="space-y-6">
        {familyMembers.map((member) => (
          <div key={member.id} className="p-4 rounded-lg hover:bg-muted/50 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <User className="h-6 w-6 text-primary" />
                </div>
                <div className="space-y-1">
                  <h3 className="font-semibold text-lg">{member.name}</h3>
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
                
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem className="flex items-center gap-2">
                      <Edit className="h-4 w-4" />
                      Edit Member
                    </DropdownMenuItem>
                    <DropdownMenuItem className="flex items-center gap-2 text-destructive">
                      <Trash2 className="h-4 w-4" />
                      Remove Member
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          </div>
        ))}
      </div>

      {familyMembers.length === 0 && (
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

      {/* Save Button */}
      <div className="flex justify-end pt-6">
        <Button size="lg" className="px-8">
          Save Settings
        </Button>
      </div>
    </div>
  );
}

