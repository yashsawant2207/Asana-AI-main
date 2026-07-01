import { createFileRoute, Link } from "@tanstack/react-router";
import { Activity, Camera, Cpu, ScanLine } from "lucide-react";
import { Button } from "@/components/ui/button";
import { POSES } from "@/lib/poses";
import heroImg from "@/assets/hero-yoga.jpg";

export const Route = createFileRoute("/")({
  component: Index,
});

const steps = [
  {
    icon: Camera,
    title: "Turn on your camera",
    body: "Your webcam streams securely to the pose engine. Nothing is recorded — only live frames are analyzed.",
  },
  {
    icon: Cpu,
    title: "Python reads your body",
    body: "A MediaPipe computer-vision model tracks 12 key joints and measures your alignment frame by frame.",
  },
  {
    icon: Activity,
    title: "Get instant corrections",
    body: "A rule engine compares each angle to the ideal pose and coaches you in real time until it's perfect.",
  },
];

function Index() {
  return (
    <>
      <section className="mx-auto grid max-w-6xl items-center gap-10 px-5 py-14 md:grid-cols-2 md:py-20">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full bg-secondary px-3 py-1 text-xs font-medium text-secondary-foreground">
            <ScanLine className="h-3.5 w-3.5" /> Real-time pose tracking
          </span>
          <h1 className="mt-5 text-4xl font-semibold leading-tight text-foreground sm:text-5xl">
            Your personal yoga coach that actually sees you.
          </h1>
          <p className="mt-5 max-w-md text-lg text-muted-foreground">
            Asana AI analyzes your webcam with a Python computer-vision engine and gives you
            live posture feedback across 12 classic asanas — align, hold, and perfect every posture with muscle-focused guidance.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button asChild size="lg">
              <Link to="/practice">Start practicing</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link to="/poses">Browse poses</Link>
            </Button>
          </div>
        </div>
        <div className="relative">
          <div className="absolute -inset-4 -z-10 rounded-[2rem] bg-primary/10 blur-2xl" />
          <img
            src={heroImg}
            alt="Yoga tree pose with joint tracking points overlaid"
            width={1280}
            height={1280}
            className="w-full rounded-[1.75rem] border border-border/60 shadow-lg"
          />
        </div>
      </section>

      <section className="border-y border-border/60 bg-secondary/30">
        <div className="mx-auto max-w-6xl px-5 py-16">
          <h2 className="text-center text-3xl font-semibold text-foreground">How it works</h2>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {steps.map((step) => (
              <div key={step.title} className="rounded-2xl border border-border/60 bg-card p-6 shadow-sm">
                <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  <step.icon className="h-5 w-5" />
                </span>
                <h3 className="mt-4 text-lg font-semibold text-foreground">{step.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{step.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-16">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h2 className="text-3xl font-semibold text-foreground">A library of guided poses</h2>
            <p className="mt-2 text-muted-foreground">Twelve classic asanas, each mapped to its Sanskrit name, target muscles, and benefit-focused alignment cues.</p>
          </div>
          <Button asChild variant="ghost" className="hidden sm:inline-flex">
            <Link to="/poses">See all</Link>
          </Button>
        </div>
        <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {POSES.slice(0, 8).map((pose) => (
            <div key={pose.id} className="rounded-2xl border border-border/60 bg-card p-5 shadow-sm">
              <p className="text-xs font-medium uppercase tracking-wide text-accent">{pose.focus}</p>
              <h3 className="mt-1 text-base font-semibold text-foreground">{pose.name}</h3>
              <p className="mt-1 text-sm italic text-muted-foreground">{pose.sanskrit}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-4xl px-5 pb-20">
        <div className="rounded-3xl bg-primary px-8 py-12 text-center text-primary-foreground">
          <h2 className="text-3xl font-semibold">Ready to find your alignment?</h2>
          <p className="mx-auto mt-3 max-w-md text-primary-foreground/80">
            Roll out your mat, open your camera, and let the coach guide your practice.
          </p>
          <Button asChild size="lg" variant="secondary" className="mt-6">
            <Link to="/practice">Start a session</Link>
          </Button>
        </div>
      </section>
    </>
  );
}
