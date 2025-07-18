import { cn } from "@/lib/utils";

export default function LinkUnderline({ children, href, className }: { children: React.ReactNode, href: string, className?: string }) {
  return (
    <a
      href={href}
      className={
        cn(
          "opacity-80 hover:opacity-100 transition-opacity duration-300 relative",
          className,
          "after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-full after:h-px after:bg-white after:scale-x-0",
          "hover:after:scale-x-100 after:transition-transform after:duration-300 after:ease-in-out",
        )
      }
    >
      {children}
    </a>
  )
}
