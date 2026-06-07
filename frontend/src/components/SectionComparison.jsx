import ItemBadge from './ItemBadge';
import ProgressRing from './ProgressRing';

const sectionLabels = {
  skills: 'Skills Match',
  education: 'Education Fit',
  experience: 'Experience Relevance',
  keywords: 'Keyword Coverage',
};

const listLimit = 6;

const formatSectionLabel = (name) => {
  if (!name) {
    return 'Section';
  }

  const original = typeof name === 'string' ? name : String(name);
  const normalized = original.toLowerCase();
  return (
    sectionLabels[normalized] ?? original.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())
  );
};

const renderItemGroup = (items, status, emptyMessage) => {
  if (!items?.length) {
    return <p className="text-xs text-slate-400 italic">{emptyMessage}</p>;
  }

  const shouldShowCount = items.length > listLimit;
  const displayItems = items.slice(0, listLimit);

  return (
    <div className="mt-2 flex flex-wrap gap-2">
      {displayItems.map((item) => (
        <ItemBadge key={`${status}-${item}`} text={item} status={status} size="sm" />
      ))}
      {shouldShowCount && (
        <span className="text-xs text-slate-400 self-center">+{items.length - listLimit} more</span>
      )}
    </div>
  );
};

export default function SectionComparison({ section }) {
  const {
    section_name: sectionName,
    cv_items: cvItems = [],
    jd_items: jdItems = [],
    matched_items: matchedItems = [],
    missing_items: missingItems = [],
    extra_items: extraItems = [],
    match_percentage: matchPercentage = 0,
  } = section;

  const title = formatSectionLabel(sectionName);

  return (
    <article className="glass rounded-3xl border border-white/10 p-5 shadow-glow-teal min-h-[230px] flex flex-col gap-4">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Section</p>
          <h3 className="text-lg font-semibold text-white">{title}</h3>
        </div>
        <ProgressRing percentage={Math.min(100, Math.max(0, matchPercentage))} size={84} strokeWidth={6} />
      </div>

      <div className="flex flex-wrap gap-3 text-xs text-slate-400">
        <span className="rounded-full border border-white/10 px-3 py-1">CV items: {cvItems.length}</span>
        <span className="rounded-full border border-white/10 px-3 py-1">JD items: {jdItems.length}</span>
        <span className="rounded-full border border-white/10 px-3 py-1">Matched: {matchedItems.length}</span>
      </div>

      <div className="flex flex-wrap gap-3 text-xs font-semibold text-slate-300">
        <ItemBadge text="Matched" status="matched" size="sm" />
        <ItemBadge text="Missing" status="missing" size="sm" />
        <ItemBadge text="Extra" status="extra" size="sm" />
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-[0.65rem] uppercase tracking-[0.3em] text-slate-400">Matched Items</p>
          {renderItemGroup(matchedItems, 'matched', 'No matched items yet.')}
        </div>
        <div>
          <p className="text-[0.65rem] uppercase tracking-[0.3em] text-slate-400">Missing Items</p>
          {renderItemGroup(missingItems, 'missing', 'No missing items detected.')}
        </div>
        <div>
          <p className="text-[0.65rem] uppercase tracking-[0.3em] text-slate-400">Extra Items in CV</p>
          {renderItemGroup(extraItems, 'extra', 'No extra items observed.')}
        </div>
      </div>
    </article>
  );
}
