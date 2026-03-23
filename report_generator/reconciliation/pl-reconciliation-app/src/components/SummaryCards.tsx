import { CheckCircle, XCircle, BarChart3 } from 'lucide-react';
import type { CheckResult } from '@/lib/types';

interface Props {
  results: CheckResult[];
}

export function SummaryCards({ results }: Props) {
  const total = results.length;
  const passed = results.filter(r => r.passed).length;
  const failed = total - passed;
  const rate = total > 0 ? ((passed / total) * 100).toFixed(1) : '0';

  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      <Card label="ตรวจทั้งหมด" value={total} color="blue" icon={<BarChart3 className="w-5 h-5" />} />
      <Card label="ผ่าน" value={passed} color="green" icon={<CheckCircle className="w-5 h-5" />} />
      <Card label="ไม่ผ่าน" value={failed} color="red" icon={<XCircle className="w-5 h-5" />} />
      <Card label="อัตราผ่าน" value={`${rate}%`} color="amber" icon={<BarChart3 className="w-5 h-5" />} />
    </div>
  );
}

function Card({ label, value, color, icon }: { label: string; value: string | number; color: string; icon: React.ReactNode }) {
  const colors: Record<string, string> = {
    blue: 'bg-[rgba(31,94,255,0.06)] text-[var(--app-accent)] border-[rgba(31,94,255,0.12)]',
    green: 'bg-[rgba(23,114,69,0.06)] text-[var(--app-success)] border-[rgba(23,114,69,0.16)]',
    red: 'bg-[rgba(192,58,43,0.06)] text-[var(--app-danger)] border-[rgba(192,58,43,0.14)]',
    amber: 'bg-[rgba(213,166,50,0.08)] text-[#9b6a08] border-[rgba(213,166,50,0.2)]',
  };

  return (
    <div className={`rounded-[22px] border px-4 py-4 sm:px-5 ${colors[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.14em] opacity-70">{label}</p>
          <p className="mt-2 text-2xl font-semibold tracking-[-0.03em] text-neutral-950">{value}</p>
        </div>
        <div className="opacity-70">{icon}</div>
      </div>
    </div>
  );
}
