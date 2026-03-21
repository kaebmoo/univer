import * as XLSX from 'xlsx';
import { Download } from 'lucide-react';
import { cn } from '@/utils/cn';
import type { CheckResult } from '@/lib/types';

interface Props {
  results: CheckResult[];
  mode: string;
  label?: string;
  size?: 'sm' | 'md';
}

export function ExportButton({ results, mode, label = 'Export Excel', size = 'md' }: Props) {
  const handleExport = () => {
    const summary = [{
      'Total Checks': results.length,
      'Passed': results.filter(r => r.passed).length,
      'Failed': results.filter(r => !r.passed).length,
      'Pass Rate': `${((results.filter(r => r.passed).length / results.length) * 100).toFixed(1)}%`,
      'Mode': mode,
      'Generated': new Date().toLocaleString('th-TH'),
    }];

    const mapped = results.map(r => ({
      'Category': r.category,
      'Check': r.check_name,
      'Source Label': r.source_label,
      'Source Value': r.source_value,
      'Target Label': r.target_label,
      'Target Value': r.target_value,
      'Difference': r.diff,
      'Tolerance': r.tolerance,
      'Status': r.status,
    }));

    const failed = mapped.filter(r => r.Status === 'FAIL');

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(summary), 'Summary');
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(mapped), 'All Checks');
    if (failed.length > 0) {
      XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(failed), 'Failed Checks');
    }

    // Per category — limit to avoid too many sheets
    const categories = Array.from(new Set(mapped.map(r => r.Category)));
    for (const cat of categories.slice(0, 50)) {
      const catResults = mapped.filter(r => r.Category === cat);
      const safeName = cat.substring(0, 31).replace(/[\\/*?:\[\]]/g, '_');
      try {
        XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(catResults), safeName);
      } catch {
        // Skip if sheet name collision
      }
    }

    XLSX.writeFile(wb, `reconciliation_${mode}_${Date.now()}.xlsx`);
  };

  return (
    <button
      onClick={handleExport}
      className={cn(
        'flex items-center gap-1.5 font-medium shadow-sm transition-colors rounded-lg',
        size === 'sm'
          ? 'px-3 py-1.5 text-xs bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200'
          : 'px-4 py-2 text-sm bg-green-600 hover:bg-green-700 text-white',
      )}
    >
      <Download className={size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'} />
      {label}
    </button>
  );
}
