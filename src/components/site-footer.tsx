import { Link } from "@tanstack/react-router";

export function SiteFooter() {
  return (
    <footer className="border-t border-border/60 bg-secondary/40">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-5 py-8 text-sm text-muted-foreground sm:flex-row">
        <p>Asana AI — real-time yoga coaching powered by Python computer vision.</p>
        <nav className="flex gap-4">
          <Link to="/poses" className="transition-colors hover:text-foreground">
            Poses
          </Link>
          <Link to="/practice" className="transition-colors hover:text-foreground">
            Practice
          </Link>
        </nav>
      </div>
    </footer>
  );
}