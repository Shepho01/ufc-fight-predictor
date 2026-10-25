type ModelPrediction = {
  name: string;
  islamWinProbability: number;
  description: string;
};

type MatchupPrediction = {
  fightId: string;
  fighterA: string;
  fighterB: string;
  fightDate: string;
  trainingCutoff: string;
  trainingFights: number;
  featureCount: number;
  predictions: ModelPrediction[];
};

async function getMatchupPrediction(): Promise<MatchupPrediction> {
  const apiUrl = process.env.UFC_API_URL;

  if (!apiUrl) {
    throw new Error("UFC_API_URL is not configured.");
  }

  const response = await fetch(`${apiUrl}/api/predictions/islam-vs-volk-1`, {
    cache: "no-store",
    signal: AbortSignal.timeout(5000),
  });

  if (!response.ok) {
    throw new Error(`Prediction API returned ${response.status}`);
  }

  return response.json();
}

function PredictionCard({
  name,
  islamWinProbability,
  description,
}: ModelPrediction) {
  const volkWinProbability = 100 - islamWinProbability;

  return (
    <article className="rounded-2xl border border-slate-700 bg-slate-900 p-6">
      <h3 className="text-lg font-semibold text-white">{name}</h3>

      <p className="mt-2 text-sm leading-6 text-slate-400">{description}</p>

      <div className="mt-6 flex items-end justify-between gap-4">
        <div>
          <p className="text-sm text-slate-300">Makhachev</p>
          <p className="mt-1 text-3xl font-semibold text-emerald-400">
            {islamWinProbability.toFixed(1)}%
          </p>
        </div>

        <div className="text-right">
          <p className="text-sm text-slate-300">Volkanovski</p>
          <p className="mt-1 text-3xl font-semibold text-sky-400">
            {volkWinProbability.toFixed(1)}%
          </p>
        </div>
      </div>

      <div
        aria-hidden="true"
        className="mt-4 flex h-3 overflow-hidden rounded-full bg-sky-400"
      >
        <div
          className="h-full bg-emerald-400"
          style={{ width: `${islamWinProbability}%` }}
        />
      </div>

      <p className="mt-4 text-xs text-slate-400">
        Experimental win probability estimates
      </p>
    </article>
  );
}

export default async function Home() {
  let matchup: MatchupPrediction;

  try {
    matchup = await getMatchupPrediction();
  } catch (error) {
    console.error("Could not load matchup:", error);

    return (
      <main className="min-h-screen bg-slate-950 px-6 py-12 text-white">
        <h1 className="text-2xl font-bold">
          Predictions temporarily unavailable
        </h1>
        <p className="mt-4 text-slate-400">
          Please try refreshing the page shortly.
        </p>
      </main>
    );
  }

  const predictions = matchup.predictions;

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-12 text-slate-100 sm:px-10">
      <div className="mx-auto max-w-5xl">
        <header className="border-b border-slate-800 pb-8">
          <p className="text-sm font-semibold uppercase tracking-widest text-emerald-400">
            UFC Fight Predictor
          </p>

          <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-5xl">
            Explore the matchup.
          </h1>

          <p className="mt-4 max-w-2xl leading-7 text-slate-400">
            Compare experimental model predictions built from historical fighter
            statistics.
          </p>
        </header>

        <section
          aria-labelledby="matchup-heading"
          className="mt-8 rounded-2xl border border-slate-700 bg-slate-900 p-6 sm:p-8"
        >
          <p className="text-sm text-slate-400">
            UFC 284 · 11 February 2023 · Lightweight
          </p>

          <h2 id="matchup-heading" className="sr-only">
            Islam Makhachev versus Alexander Volkanovski
          </h2>

          <div className="mt-6 grid items-center gap-6 text-center sm:grid-cols-[1fr_auto_1fr]">
            <div>
              <p className="text-sm text-emerald-400">Fighter A</p>
              <p className="mt-2 text-2xl font-bold sm:text-3xl">
                Islam Makhachev
              </p>
            </div>

            <span className="text-sm font-semibold text-slate-500">VS</span>

            <div>
              <p className="text-sm text-sky-400">Fighter B</p>
              <p className="mt-2 text-2xl font-bold sm:text-3xl">
                Alexander Volkanovski
              </p>
            </div>
          </div>

          <dl className="mt-8 grid gap-6 border-t border-slate-700 pt-6 sm:grid-cols-3">
            <div>
              <dt className="text-sm text-slate-400">Training examples</dt>
              <dd className="mt-1 font-semibold">
                {matchup.trainingFights} earlier fights
              </dd>
            </div>

            <div>
              <dt className="text-sm text-slate-400">Training cutoff</dt>
              <dd className="mt-1 font-semibold">Before 11 February 2023</dd>
            </div>

            <div>
              <dt className="text-sm text-slate-400">Prediction inputs</dt>
              <dd className="mt-1 font-semibold">
                Four historical differences
              </dd>
            </div>
          </dl>
        </section>

        <section aria-labelledby="predictions-heading" className="mt-10">
          <h2 id="predictions-heading" className="text-2xl font-semibold">
            Model predictions
          </h2>

          <p className="mt-2 leading-7 text-slate-400">
            Each model used the same training fights. Their estimates differ
            because they learn different relationships.
          </p>

          <div className="mt-6 grid gap-5 md:grid-cols-2">
            {predictions.map((prediction) => (
              <PredictionCard key={prediction.name} {...prediction} />
            ))}
          </div>
        </section>

        <aside className="mt-8 rounded-xl border border-slate-700 p-5 text-sm leading-6 text-slate-400">
          <p className="font-semibold text-slate-200">
            Historical case study · In development
          </p>
          <p className="mt-2">
            These saved estimates were generated retrospectively using training
            fights before the matchup date. They are not live forecasts. Results
            for one fight do not establish overall model reliability.
          </p>
        </aside>
      </div>
    </main>
  );
}
