'use client'
import React, { useState } from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Badge } from '@/components/ui/badge';
import { 
  Bell, 
  Palette, 
  Phone,
  MessageCircle,
  Mail
} from 'lucide-react';

export default function GeneralSettingsPage() {
  const [notificationType, setNotificationType] = useState('email');
  const [whatsappNumber, setWhatsappNumber] = useState('');
  const [selectedTheme, setSelectedTheme] = useState('light');

  const themes = [
    { id: 'light', name: 'Light', preview: 'bg-gradient-to-br from-blue-50 to-indigo-100' },
    { id: 'dark', name: 'Dark', preview: 'bg-gradient-to-br from-gray-800 to-gray-900' },
    { id: 'system', name: 'System', preview: 'bg-gradient-to-br from-purple-100 to-pink-100' }
  ];

  return (
    <div className="max-w-[60%] mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">General Settings</h1>
        <p className="text-muted-foreground mt-2">Manage your account preferences and application settings</p>
      </div>

      {/* Notification Settings */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 mb-6">
          <Bell className="h-5 w-5" />
          <h2 className="text-xl font-semibold">Notification Preferences</h2>
        </div>
        
        <div className="space-y-4">
          <Label>Choose your notification method</Label>
          <RadioGroup value={notificationType} onValueChange={setNotificationType} className="space-y-3">
            <div className="flex items-center space-x-3">
              <RadioGroupItem value="email" id="email" />
              <Label htmlFor="email" className="flex items-center gap-2 cursor-pointer">
                <Mail className="h-4 w-4" />
                Email
              </Label>
            </div>
            
            <div className="flex items-center space-x-3 opacity-50">
              <RadioGroupItem value="call" id="call" disabled />
              <Label htmlFor="call" className="flex items-center gap-2 cursor-not-allowed">
                <Phone className="h-4 w-4" />
                Phone Call
                <Badge variant="secondary" className="text-xs">Unavailable</Badge>
              </Label>
            </div>
            
            <div className="flex items-center space-x-3 opacity-50">
              <RadioGroupItem value="whatsapp" id="whatsapp" disabled />
              <Label htmlFor="whatsapp" className="flex items-center gap-2 cursor-not-allowed">
                <MessageCircle className="h-4 w-4" />
                WhatsApp
                <Badge variant="secondary" className="text-xs">Unavailable</Badge>
              </Label>
            </div>
          </RadioGroup>

          {notificationType === 'whatsapp' && (
            <div className="space-y-2 ml-6">
              <Label htmlFor="whatsapp-number">WhatsApp Number</Label>
              <Input
                id="whatsapp-number"
                placeholder="+1 (555) 123-4567"
                value={whatsappNumber}
                onChange={(e) => setWhatsappNumber(e.target.value)}
                className="max-w-sm"
              />
            </div>
          )}
        </div>
      </div>

      {/* Theme Settings */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 mb-6">
          <Palette className="h-5 w-5" />
          <h2 className="text-xl font-semibold">Choose Theme</h2>
        </div>
        
        <div className="space-y-4">
          <Label>Select your preferred appearance</Label>
          <RadioGroup value={selectedTheme} onValueChange={setSelectedTheme} className="grid grid-cols-3 gap-4">
            {themes.map((theme) => (
              <div key={theme.id} className="space-y-2">
                <RadioGroupItem value={theme.id} id={theme.id} className="sr-only" />
                <Label 
                  htmlFor={theme.id} 
                  className={`cursor-pointer block border-2 rounded-lg p-3 transition-all hover:border-primary/50 ${
                    selectedTheme === theme.id ? 'border-primary bg-primary/5' : 'border-muted'
                  }`}
                >
                  <div className={`h-20 rounded-md ${theme.preview} mb-2`} />
                  <div className="text-center font-medium">{theme.name}</div>
                  {selectedTheme === theme.id && (
                    <Badge className="w-full justify-center mt-2">Selected</Badge>
                  )}
                </Label>
              </div>
            ))}
          </RadioGroup>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end pt-6">
        <Button size="lg" className="px-8">
          Save Settings
        </Button>
      </div>
    </div>)
}

