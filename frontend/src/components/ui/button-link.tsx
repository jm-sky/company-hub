import * as React from "react"
import { type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { buttonVariants } from "./button"
import Link from "next/link"

function ButtonLink({
  className,
  variant,
  vibe,
  size,
  href,
  ...props
}: React.ComponentProps<"a"> &
  VariantProps<typeof buttonVariants> & {
    href: string
  }) {

  return (
    <Link
      className={cn(buttonVariants({ variant, size, className, vibe }))}
      href={href}
      {...props}
    />
  )
}

export { ButtonLink }
