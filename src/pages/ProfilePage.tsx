import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { User, Mail, MapPin, Clock, Cpu, Save } from 'lucide-react';

const ProfilePage = () => {
  const { user, updateUser } = useAuth();
  const { toast } = useToast();
  const [name, setName] = useState(user?.name || '');
  const [saving, setSaving] = useState(false);

  const handleSave = () => {
    setSaving(true);
    setTimeout(() => {
      updateUser({ name });
      toast({ title: 'Profile updated' });
      setSaving(false);
    }, 500);
  };

  return (
    <div className="p-4 md:p-6 space-y-6 animate-fade-in max-w-2xl">
      <h1 className="text-2xl font-bold">Profile</h1>

      <div className="rounded-lg border bg-card p-6 shadow-card space-y-4">
        <div className="flex items-center gap-4 pb-4 border-b">
          <div className="rounded-full bg-primary/10 p-4"><User className="h-8 w-8 text-primary" /></div>
          <div>
            <p className="font-semibold text-lg">{user?.name}</p>
            <p className="text-sm text-muted-foreground">{user?.email}</p>
          </div>
        </div>

        <div><label className="text-sm font-medium">Full Name</label><Input value={name} onChange={e => setName(e.target.value)} /></div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-3 rounded-lg bg-muted p-3">
            <Mail className="h-4 w-4 text-muted-foreground" /><div><p className="text-muted-foreground">Email</p><p className="font-medium">{user?.email}</p></div>
          </div>
          <div className="flex items-center gap-3 rounded-lg bg-muted p-3">
            <Cpu className="h-4 w-4 text-muted-foreground" /><div><p className="text-muted-foreground">Platform</p><p className="font-medium">{user?.platform}</p></div>
          </div>
          <div className="flex items-center gap-3 rounded-lg bg-muted p-3">
            <MapPin className="h-4 w-4 text-muted-foreground" /><div><p className="text-muted-foreground">Zone</p><p className="font-medium">{user?.zone}</p></div>
          </div>
          <div className="flex items-center gap-3 rounded-lg bg-muted p-3">
            <Clock className="h-4 w-4 text-muted-foreground" /><div><p className="text-muted-foreground">Working Hours</p><p className="font-medium">{user?.workingHours}</p></div>
          </div>
        </div>

        <Button onClick={handleSave} disabled={saving} className="gap-2"><Save className="h-4 w-4" /> Save Changes</Button>
      </div>

      <div className="rounded-lg border bg-card p-6 shadow-card">
        <h2 className="font-semibold mb-4">Notification Preferences</h2>
        <div className="space-y-3">
          {['Trigger alerts', 'Payout notifications', 'Weekly summary', 'Marketing emails'].map(pref => (
            <label key={pref} className="flex items-center justify-between">
              <span className="text-sm">{pref}</span>
              <input type="checkbox" defaultChecked={pref !== 'Marketing emails'} className="rounded" />
            </label>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
