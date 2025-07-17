'use client'

import { LucideIcon } from 'lucide-react'
import { Hourglass } from 'lucide-react'
import Link from 'next/link'

interface SidebarMenuItemProps {
  name: string
  href: string
  icon: LucideIcon
  disabled?: boolean
  isActive?: boolean
}

export function SidebarMenuItem({ name, href, icon: Icon, disabled = false, isActive = false }: SidebarMenuItemProps) {
  const getClassName = () => {
    if (disabled) {
      return 'text-muted-foreground cursor-not-allowed'
    }
    if (isActive) {
      return 'bg-accent text-accent-foreground'
    }
    return 'text-foreground hover:bg-accent hover:text-accent-foreground'
  }

  return (
    <Link
      href={disabled ? '#' : href}
      className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${getClassName()}`}
      onClick={disabled ? (e) => e.preventDefault() : undefined}
    >
      <Icon className="mr-3 size-4" />
      {name}
      {disabled && (
        <Hourglass className="ml-auto size-3 text-muted-foreground" />
      )}
    </Link>
  )
}
