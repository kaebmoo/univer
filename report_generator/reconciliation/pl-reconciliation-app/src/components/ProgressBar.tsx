interface Props {
  percent: number;
  message: string;
}

export function ProgressBar({ percent, message }: Props) {
  return (
    <div className="rounded-[22px] border border-black/8 bg-white/75 p-4">
      <div className="mb-3 flex items-center justify-between text-sm">
        <span className="text-[var(--app-muted)]">{message}</span>
        <span className="font-medium text-[var(--app-accent)]">{percent}%</span>
      </div>
      <div className="h-2.5 w-full rounded-full bg-neutral-200">
        <div
          className="h-2.5 rounded-full bg-[var(--app-accent)] transition-all duration-300"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
