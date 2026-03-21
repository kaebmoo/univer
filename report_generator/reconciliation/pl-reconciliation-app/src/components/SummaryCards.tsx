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
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <Card label="ตรวจทั้งหมด" value={total} color="blue" icon={<BarChart3 className="w-5 h-5" />} />
      <Card label="ผ่าน" value={passed} color="green" icon={<CheckCircle className="w-5 h-5" />} />
      <Card label="ไม่ผ่าน" value={failed} color="red" icon={<XCircle className="w-5 h-5" />} />
      <Card label="อัตราผ่าน" value={`${rate}%`} color="amber" icon={<BarChart3 className="w-5 h-5" />} />
    </div>
  );
}

function Card({ label, value, color, icon }: { label: string; value: string | number; color: string; icon: React.ReactNode }) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    red: 'bg-red-50 text-red-600 border-red-200',
    amber: 'bg-amber-50 text-amber-600 border-amber-200',
  };

  return (
    <div className={`rounded-xl border p-4 ${colors[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium opacity-80">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="opacity-60">{icon}</div>
      </div>
    </div>
  );
}
