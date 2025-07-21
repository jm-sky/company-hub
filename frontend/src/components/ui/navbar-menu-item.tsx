'use client'

import Link from 'next/link'
import { Hourglass } from 'lucide-react'
import { NavigationMenuItem, NavigationMenuLink } from '@/components/ui/navigation-menu'
import { cn } from '@/lib/utils'

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
      return 'text-primary font-medium before:w-full'
    }
    return 'text-muted-foreground hover:text-primary hover:before:w-full'
  }

  return (
    <NavigationMenuItem className={className}>
      <NavigationMenuLink asChild>
        <Link
          href={disabled ? '#' : href}
          className={cn(`py-1.5 flex-row items-center flex-nowrap font-medium hover:bg-transparent before:content-[""] before:h-[2px] before:w-0 before:absolute before:bottom-0 before:left-0 before:bg-brand before:transition-all before:duration-300 before:ease-in-out`, getClassName())}
          onClick={disabled ? (e) => e.preventDefault() : undefined}
        >
          {label}
          {disabled && (
            <Hourglass className="ml-2 size-3 text-muted-foreground" />
          )}
        </Link>
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
      <NavigationMenuLink asChild>
        <Link
          href={disabled ? '#' : href}
          className={`py-1.5 flex-nowrap ${getClassName()}`}
          onClick={disabled ? (e) => e.preventDefault() : undefined}
        >
          {label}
          {disabled && (
            <Hourglass className="ml-2 size-3 text-muted-foreground" />
          )}
        </Link>
      </NavigationMenuLink>
    </NavigationMenuItem>
  )
}
