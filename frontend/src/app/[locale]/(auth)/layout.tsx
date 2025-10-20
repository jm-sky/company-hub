import { ReactNode } from 'react';
import { ThemeToggle } from '@/components/ui/theme-toggle';

export default function AuthLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="relative min-h-screen bg-muted-foreground/20 dark:bg-background">
      <div className="absolute top-1 right-1 flex gap-2 p-2">
        <ThemeToggle />
      </div>
      {children}
    </div>
  );
}
