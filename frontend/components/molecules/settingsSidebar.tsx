import { Sidebar, SidebarContent, SidebarHeader, SidebarMenu,SidebarMenuButton, SidebarMenuSub,SidebarMenuSubItem,SidebarMenuItem, SidebarMenuSubButton,SidebarGroup } from "@/components/ui/sidebar"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import Link from "next/link";

// export function SettingsSidebar() {
//   return (
//     <Sidebar>
//     <SidebarHeader>
//         Settings
//     </SidebarHeader>
//     <SidebarMenu>
//   <Collapsible defaultOpen className="group/collapsible">
//     <SidebarMenuItem>
        
//       <CollapsibleTrigger asChild>
//         <SidebarMenuButton />
//          Users
//       </CollapsibleTrigger>
     
//       <CollapsibleContent>
//         <SidebarMenuSub>
//             authentication
//           <SidebarMenuSubItem />
//         </SidebarMenuSub>
//       </CollapsibleContent>
//     </SidebarMenuItem>
//   </Collapsible>
// </SidebarMenu>
//      <SidebarContent />
//     </Sidebar>
//   )
// }

// export function SettingsSidebar() {
//   return (
//     <Sidebar>
//       <SidebarHeader>
//         <h2 className="text-lg font-semibold">Settings</h2>
//       </SidebarHeader>
      
//       <SidebarContent>
//         <SidebarGroup>
//           <SidebarMenu>
            
//             {/* Appearance Section */}
//             <Collapsible defaultOpen className="group/collapsible">
//               <SidebarMenuItem>
//                 <CollapsibleTrigger asChild>
//                   <SidebarMenuButton>
//                     {/* <Palette className="h-4 w-4" /> */}
//                     <span>Appearance</span>
//                     {/* <ChevronDown className="ml-auto h-4 w-4 transition-transform group-data-[state=open]/collapsible:rotate-180" /> */}
//                   </SidebarMenuButton>
//                 </CollapsibleTrigger>
                
//                 <CollapsibleContent>
//                   <SidebarMenuSub>
//                     <SidebarMenuSubItem>
//                       <SidebarMenuSubButton asChild>
//                         <a href="/settings/appearance/themes">
//                           <span>Themes</span>
//                         </a>
//                       </SidebarMenuSubButton>
//                     </SidebarMenuSubItem>
                    
//                     <SidebarMenuSubItem>
//                       <SidebarMenuSubButton asChild>
//                         <a href="/settings/appearance/layout">
//                           <span>Layout</span>
//                         </a>
//                       </SidebarMenuSubButton>
//                     </SidebarMenuSubItem>
//                   </SidebarMenuSub>
//                 </CollapsibleContent>
//               </SidebarMenuItem>
//             </Collapsible>

//             {/* Team Section */}
//             <Collapsible defaultOpen className="group/collapsible">
//               <SidebarMenuItem>
//                 <CollapsibleTrigger asChild>
//                   <SidebarMenuButton>
//                     {/* <Users className="h-4 w-4" /> */}
//                     <span>Team</span>
//                     {/* <ChevronDown className="ml-auto h-4 w-4 transition-transform group-data-[state=open]/collapsible:rotate-180" /> */}
//                   </SidebarMenuButton>
//                 </CollapsibleTrigger>
                
//                 <CollapsibleContent>
//                   <SidebarMenuSub>
//                     <SidebarMenuSubItem>
//                       <SidebarMenuSubButton asChild>
//                         <a href="/settings/team/members">
//                           <span>Members</span>
//                         </a>
//                       </SidebarMenuSubButton>
//                     </SidebarMenuSubItem>
                    
//                     <SidebarMenuSubItem>
//                       <SidebarMenuSubButton asChild>
//                         <a href="/settings/team/roles">
//                           <span>Roles</span>
//                         </a>
//                       </SidebarMenuSubButton>
//                     </SidebarMenuSubItem>
//                   </SidebarMenuSub>
//                 </CollapsibleContent>
//               </SidebarMenuItem>
//             </Collapsible>

//           </SidebarMenu>
//         </SidebarGroup>
//       </SidebarContent>
//     </Sidebar>
//   )
// }

export function SettingsSidebar() {
  return (
    <Sidebar>
      <SidebarHeader>
        Settings
      </SidebarHeader>
      
      <SidebarContent>
        <SidebarMenu>
          {/* Appearance Section */}
          <Collapsible defaultOpen className="group/collapsible">
            <SidebarMenuItem>
              <CollapsibleTrigger asChild>
                <SidebarMenuButton>
                  Appearance
                </SidebarMenuButton>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <SidebarMenuSub>
                  <SidebarMenuSubItem>
                    <SidebarMenuSubButton>
                      <Link href="/settings/themes">Themes</Link>
                    </SidebarMenuSubButton>
                  </SidebarMenuSubItem>
                </SidebarMenuSub>
              </CollapsibleContent>
            </SidebarMenuItem>
          </Collapsible>

          {/* Family Section */}
          <Collapsible defaultOpen className="group/collapsible">
            <SidebarMenuItem>
              <CollapsibleTrigger asChild>
                <SidebarMenuButton>
                  Family
                </SidebarMenuButton>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <SidebarMenuSub>
                  <SidebarMenuSubItem>
                    <SidebarMenuSubButton>
                        <Link href="/settings/family/members">Members</Link>
                      
                    </SidebarMenuSubButton>
                  </SidebarMenuSubItem>
                  <SidebarMenuSubItem>
                    <SidebarMenuSubButton>
                         <Link href="/settings/family/roles">Roles</Link>
                      
                    </SidebarMenuSubButton>
                  </SidebarMenuSubItem>
                </SidebarMenuSub>
              </CollapsibleContent>
            </SidebarMenuItem>
          </Collapsible>
        </SidebarMenu>
      </SidebarContent>
    </Sidebar>
  )
}