export default function Loading() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-12 text-slate-100">
      <div className="mx-auto max-w-5xl">
        <p className="text-sm font-semibold uppercase tracking-widest text-emerald-400">
          UFC Fight Predictor
        </p>

        <h1 className="mt-4 text-3xl font-bold">
          Loading matchup predictions…
        </h1>

        <p role="status" className="mt-4 text-slate-400">
          Fetching the saved model results.
        </p>
      </div>
    </main>
  );
}
