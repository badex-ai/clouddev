import React,{useState, useEffect} from 'react'
import { useAuthUser } from '@/contexts/userContext'


export default function MemberSettingsPage() {

  const [familyMember, setFamilyMember] = useState(null)

  const { userData } = useAuthUser();

  // useEffect(() => {
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


  //   getFamilyMembers();
  // }, [])



  

  const familyMembers = [
    { id: 1, name: 'Seun', role: 'Admin' },
    { id: 2, name: 'Tolu', role: 'Member' },
    { id: 3, name: 'Ayo', role: 'Member' },
    { id: 4, name: 'Bola', role: 'Guest' }
  ]

  const familyList = familyMembers.map(member => (
    <li key={member.id}>
      {member.name} - {member.role}
    </li>
  ));


  return (
    <div className="margin-top-30 width-100 ">
      <h1>
        family members
      </h1>

      <p>
        Manage family members and their roles.
      </p>
      <div>add new Family member</div>
      <p>
      family members list  
      </p>
      <ul>
        {familyList}
      </ul>


    </div>
  )
}

