import { cn } from '@/lib/utils'
import { APP_CONFIG } from '@/config/app'

interface LogoTextProps {
  className?: string
  foreground?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

export function LogoText({ className, size = 'md', foreground = 'text-foreground' }: LogoTextProps) {
  const sizeClasses = {
    sm: 'text-lg font-semibold',
    md: 'text-xl font-bold',
    lg: 'text-2xl font-bold',
    xl: 'text-3xl font-bold'
  }

  return (
    <span className={cn(sizeClasses[size], className)}>
      <span className={foreground}>{APP_CONFIG.displayName.company}</span>
      <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 dark:from-blue-400 dark:via-purple-400 dark:to-blue-600 bg-clip-text text-transparent">
        {APP_CONFIG.displayName.hub}
      </span>
    </span>
  )
}
