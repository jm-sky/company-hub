'use client'

import {
  BoltIcon,
  BookOpenIcon,
  LogOutIcon,
  User,
  Hourglass,
} from "lucide-react"
import { useRouter } from 'next/navigation'

import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useAuth, useUser } from '@/lib/hooks/useAuth'

export default function UserMenu() {
  const { data: user } = useUser()
  const { logout } = useAuth()
  const router = useRouter()

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  const getInitials = (email: string) => {
    return email.split('@')[0].slice(0, 2).toUpperCase()
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="h-auto p-0 hover:bg-transparent">
          <Avatar>
            <AvatarImage src="" alt="Profile image" />
            <AvatarFallback>
              {user?.name ? getInitials(user.name) : user?.email ? getInitials(user.email) : <User className="size-4" />}
            </AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="max-w-64" align="end">
        <DropdownMenuLabel className="flex min-w-0 flex-col">
          <span className="text-foreground truncate text-sm font-medium">
            {user?.name || 'User'}
          </span>
          <span className="text-muted-foreground truncate text-xs font-normal">
            {user?.email || 'user@example.com'}
          </span>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem disabled>
            <User size={16} className="opacity-60" aria-hidden="true" />
            <span>Profile</span>
            <Hourglass className="ml-auto size-3 text-muted-foreground" />
          </DropdownMenuItem>
          <DropdownMenuItem disabled>
            <BoltIcon size={16} className="opacity-60" aria-hidden="true" />
            <span>Settings</span>
            <Hourglass className="ml-auto size-3 text-muted-foreground" />
          </DropdownMenuItem>
          <DropdownMenuItem>
            <BookOpenIcon size={16} className="opacity-60" aria-hidden="true" />
            <span>Documentation</span>
          </DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleLogout}>
          <LogOutIcon size={16} className="opacity-60" aria-hidden="true" />
          <span>Logout</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}