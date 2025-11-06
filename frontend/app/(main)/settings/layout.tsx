'use client';
import React from 'react';
import { SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar';
import { SettingsSidebar } from '@/components/molecules/settingsSidebar';

export default function SettingsPage({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-full">
      <SidebarProvider>
        <SettingsSidebar />
        <main className="w-full">{children}</main>
      </SidebarProvider>
    </div>
  );
}
