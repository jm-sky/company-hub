import { ButtonLink } from "../ui/button-link";
import { ThemeToggle } from "../ui/theme-toggle";

export default function LandingNav() {
  return (
    <nav className="relative z-50 border-b border-border/40 bg-background/80 backdrop-blur-sm">
    <div className="container mx-auto px-4 md:px-6">
      <div className="flex h-16 items-center justify-between">
        <div className="flex items-center">
          <h1 className="text-xl font-bold text-foreground">
            Company<span className="text-brand">Hub</span>
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <ButtonLink
            variant="ghost"
            href="/login"
          >
            Login
          </ButtonLink>
          <ButtonLink
            href="/register"
            className="bg-primary text-primary-foreground hover:bg-primary/90"
          >
            Get Started
          </ButtonLink>
        </div>
      </div>
    </div>
  </nav>
  );
}
