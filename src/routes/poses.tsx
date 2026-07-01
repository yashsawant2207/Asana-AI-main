import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { POSES } from "@/lib/poses";

export const Route = createFileRoute("/poses")({
  head: () => ({
    meta: [
      { title: "Pose Library — Asana AI" },
      {
        name: "description",
        content:
          "Explore 12 classic yoga asanas with live alignment coaching, muscle-targeted benefit cues, and Sanskrit names.",
      },
      { property: "og:title", content: "Pose Library — Asana AI" },
      {
        property: "og:description",
        content: "Browse 12 classic asanas with muscle focus, Sanskrit names, and real-time alignment guidance.",
      },
    ],
  }),
  component: PosesPage,
});

const difficultyStyles: Record<string, string> = {
  Beginner: "bg-success/15 text-success",
  Intermediate: "bg-warning/20 text-warning",
  Advanced: "bg-accent/15 text-accent",
};

function PosesPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-14">
      <header className="max-w-2xl">
        <h1 className="text-4xl font-semibold text-foreground">Pose library</h1>
        <p className="mt-3 text-lg text-muted-foreground">
          Each asana includes muscle-targeted alignment cues and benefits the coach checks in real time.
          Pick one and head to the practice screen when you're ready.
        </p>
      </header>

      <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {POSES.map((pose) => (
          <article
            key={pose.id}
            className="flex flex-col rounded-2xl border border-border/60 bg-card p-6 shadow-sm"
          >
            <div className="overflow-hidden rounded-3xl bg-muted">
              <img
                src={pose.image}
                alt={`${pose.name} pose illustration`}
                className="h-40 w-full object-cover object-center"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium uppercase tracking-wide text-accent">
                {pose.focus}
              </span>
              <span
                className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${difficultyStyles[pose.difficulty]}`}
              >
                {pose.difficulty}
              </span>
            </div>
            <h2 className="mt-3 text-xl font-semibold text-foreground">{pose.name}</h2>
            <p className="text-sm italic text-muted-foreground">{pose.sanskrit}</p>
            <p className="mt-3 flex-1 text-sm text-muted-foreground">{pose.description}</p>
            <ul className="mt-4 space-y-1.5">
              {pose.cues.map((cue) => (
                <li key={cue} className="flex gap-2 text-sm text-foreground">
                  <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                  {cue}
                </li>
              ))}
            </ul>
            <Button asChild variant="secondary" className="mt-5">
              <Link to="/practice" search={{ pose: pose.id }}>
                Practice this pose
              </Link>
            </Button>
          </article>
        ))}
      </div>
    </div>
  );
}