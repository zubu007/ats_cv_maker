/**
 * ItemBadge Component
 * Display item with status indicator (matched, missing, extra)
 */

export default function ItemBadge({ text, status = 'matched', size = 'md' }) {
  const statusStyles = {
    matched: 'bg-teal/10 border-teal/30 text-teal',
    missing: 'bg-red-500/10 border-red-500/30 text-red-300',
    extra: 'bg-mint/10 border-mint/30 text-mint',
    preferred: 'bg-lavender/10 border-lavender/30 text-lavender',
  };

  const icons = {
    matched: '✓',
    missing: '✗',
    extra: '+',
    preferred: '⭐',
  };

  const sizeStyles = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${statusStyles[status]} ${sizeStyles[size]} font-medium transition-all hover:scale-105`}
    >
      <span className="text-xs">{icons[status]}</span>
      <span>{text}</span>
    </span>
  );
}
