import SectionComparison from './SectionComparison';

export default function AnalysisSectionsGrid({ sections }) {
  if (!sections?.length) {
    return null;
  }

  const sortedSections = [...sections].sort(
    (a, b) => (b.match_percentage || 0) - (a.match_percentage || 0)
  );

  return (
    <section className="mt-10">
      <div className="flex flex-col gap-1">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Section Comparison</p>
        <h2 className="text-3xl font-semibold text-white">Match every part of the JD</h2>
        <p className="text-sm text-slate-300 max-w-3xl">
          See how each area of your CV stacks up against the job description with live badges, progress rings, and ranked highlights.
        </p>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {sortedSections.map((section) => (
          <SectionComparison key={section.section_name} section={section} />
        ))}
      </div>
    </section>
  );
}
