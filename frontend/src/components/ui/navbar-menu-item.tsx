'use client'

import { Hourglass } from 'lucide-react'
import { NavigationMenuItem, NavigationMenuLink } from '@/components/ui/navigation-menu'

interface NavbarMenuItemProps {
  href: string
  label: string
  disabled?: boolean
  isActive?: boolean
  className?: string
}

export function NavbarMenuItem({ href, label, disabled = false, isActive = false, className = '' }: NavbarMenuItemProps) {
  const getClassName = () => {
    if (disabled) {
      return 'text-muted-foreground cursor-not-allowed opacity-50'
    }
    if (isActive) {
      return 'text-primary font-medium'
    }
    return 'text-muted-foreground hover:text-primary'
  }

  return (
    <NavigationMenuItem className={className}>
      <NavigationMenuLink
        href={disabled ? '#' : href}
        className={`py-1.5 flex-row items-center flex-nowrap font-medium ${getClassName()}`}
        onClick={disabled ? (e) => e.preventDefault() : undefined}
      >
        {label}
        {disabled && (
          <Hourglass className="ml-2 size-3 text-muted-foreground" />
        )}
      </NavigationMenuLink>
    </NavigationMenuItem>
  )
}

export function MobileNavbarMenuItem({ href, label, disabled = false, isActive = false }: NavbarMenuItemProps) {
  const getClassName = () => {
    if (disabled) {
      return 'text-muted-foreground cursor-not-allowed opacity-50'
    }
    if (isActive) {
      return 'text-primary font-medium'
    }
    return 'text-foreground'
  }

  return (
    <NavigationMenuItem className="w-full">
      <NavigationMenuLink 
        href={disabled ? '#' : href} 
        className={`py-1.5 flex-nowrap ${getClassName()}`}
        onClick={disabled ? (e) => e.preventDefault() : undefined}
      >
        {label}
        {disabled && (
          <Hourglass className="ml-2 size-3 text-muted-foreground" />
        )}
      </NavigationMenuLink>
    </NavigationMenuItem>
  )
}