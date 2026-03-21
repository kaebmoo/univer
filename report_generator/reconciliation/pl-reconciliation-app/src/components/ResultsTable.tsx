import { useState, useMemo, useCallback } from 'react';
import * as XLSX from 'xlsx';
import { CheckCircle, XCircle, Search, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Download } from 'lucide-react';
import { cn } from '@/utils/cn';
import type { CheckResult } from '@/lib/types';

const PAGE_SIZE = 50;

interface Props {
  results: CheckResult[];
}

export function ResultsTable({ results }: Props) {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'PASS' | 'FAIL'>('ALL');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [page, setPage] = useState(1);

  const categories = useMemo(
    () => ['ALL', ...Array.from(new Set(results.map(r => r.category))).sort()],
    [results],
  );

  // Count pass/fail from ALL results (before status filter)
  const totalPass = useMemo(() => results.filter(r => r.passed).length, [results]);
  const totalFail = useMemo(() => results.filter(r => !r.passed).length, [results]);

  // Apply filters
  const filtered = useMemo(() => {
    return results.filter(r => {
      const matchSearch = !search ||
        r.check_name?.toLowerCase().includes(search.toLowerCase()) ||
        r.category.toLowerCase().includes(search.toLowerCase());
      const matchStatus = statusFilter === 'ALL' || r.status === statusFilter;
      const matchCategory = categoryFilter === 'ALL' || r.category === categoryFilter;
      return matchSearch && matchStatus && matchCategory;
    });
  }, [results, search, statusFilter, categoryFilter]);

  // Pagination
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  if (safePage !== page) setPage(safePage);
  const pageRows = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);

  // Export filtered data directly (not via component — ensures fresh data)
  const handleExportFiltered = useCallback(() => {
    const data = filtered; // captured from closure at click time
    if (data.length === 0) return;

    const mapped = data.map(r => ({
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

    const summary = [{
      'Total': data.length,
      'Passed': data.filter(r => r.passed).length,
      'Failed': data.filter(r => !r.passed).length,
      'Pass Rate': `${((data.filter(r => r.passed).length / data.length) * 100).toFixed(1)}%`,
      'Filter': statusFilter !== 'ALL' ? statusFilter : categoryFilter !== 'ALL' ? categoryFilter : search || 'None',
      'Generated': new Date().toLocaleString('th-TH'),
    }];

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(summary), 'Summary');
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(mapped), 'Filtered Results');

    XLSX.writeFile(wb, `reconciliation_filtered_${Date.now()}.xlsx`);
  }, [filtered, statusFilter, categoryFilter, search]);

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="ค้นหา..."
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }}
            className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={e => { setStatusFilter(e.target.value as 'ALL' | 'PASS' | 'FAIL'); setPage(1); }}
          className="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="ALL">ทุกสถานะ ({results.length})</option>
          <option value="PASS">ผ่าน ({totalPass})</option>
          <option value="FAIL">ไม่ผ่าน ({totalFail})</option>
        </select>
        <select
          value={categoryFilter}
          onChange={e => { setCategoryFilter(e.target.value); setPage(1); }}
          className="px-3 py-2 text-sm border border-gray-300 rounded-lg max-w-[300px] truncate focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {categories.map(c => (
            <option key={c} value={c}>{c === 'ALL' ? 'ทุกหมวด' : c}</option>
          ))}
        </select>

        {/* Export filtered — inline button, uses filtered data directly */}
        <button
          onClick={handleExportFiltered}
          disabled={filtered.length === 0}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors',
            filtered.length === 0
              ? 'bg-gray-50 text-gray-400 border-gray-200 cursor-not-allowed'
              : 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100',
          )}
        >
          <Download className="w-3 h-3" />
          Export ที่กรอง ({filtered.length})
        </button>
      </div>

      {/* Table */}
      {pageRows.length === 0 ? (
        <p className="text-sm text-gray-400 py-8 text-center">ไม่มีข้อมูล</p>
      ) : (
        <div className="overflow-x-auto border border-gray-200 rounded-lg">
          <table className="w-full text-sm text-left">
            <thead className="text-xs uppercase bg-gray-50 text-gray-600 sticky top-0">
              <tr>
                <th className="px-3 py-2.5 font-semibold w-8 text-center">#</th>
                <th className="px-3 py-2.5 font-semibold">หมวด</th>
                <th className="px-3 py-2.5 font-semibold">รายการ</th>
                <th className="px-3 py-2.5 font-semibold text-right">ค่า SOURCE</th>
                <th className="px-3 py-2.5 font-semibold text-right">ค่า TARGET</th>
                <th className="px-3 py-2.5 font-semibold text-right">ผลต่าง</th>
                <th className="px-3 py-2.5 font-semibold text-center">สถานะ</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {pageRows.map((r, i) => {
                const rowNum = (safePage - 1) * PAGE_SIZE + i + 1;
                return (
                  <tr key={i} className={cn('hover:bg-gray-50', !r.passed && 'bg-red-50/30')}>
                    <td className="px-3 py-2 text-gray-400 text-xs text-center">{rowNum}</td>
                    <td className="px-3 py-2 text-gray-500 max-w-[200px] truncate text-xs" title={r.category}>{r.category}</td>
                    <td className="px-3 py-2 font-medium text-gray-800 max-w-[250px] truncate" title={r.check_name}>{r.check_name}</td>
                    <td className="px-3 py-2 text-right tabular-nums" title={r.source_label}>
                      {fmt(r.source_value)}
                    </td>
                    <td className="px-3 py-2 text-right tabular-nums" title={r.target_label}>
                      {fmt(r.target_value)}
                    </td>
                    <td className={cn('px-3 py-2 text-right tabular-nums font-medium', r.passed ? 'text-green-600' : 'text-red-600')}>
                      {fmt(r.diff)}
                    </td>
                    <td className="px-3 py-2 text-center">
                      {r.passed
                        ? <span className="inline-flex items-center gap-0.5 text-green-700 bg-green-50 px-2 py-0.5 rounded-full text-xs font-medium"><CheckCircle className="w-3 h-3" />PASS</span>
                        : <span className="inline-flex items-center gap-0.5 text-red-700 bg-red-50 px-2 py-0.5 rounded-full text-xs font-medium"><XCircle className="w-3 h-3" />FAIL</span>
                      }
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <p className="text-xs text-gray-500">
            แสดง {(safePage - 1) * PAGE_SIZE + 1}–{Math.min(safePage * PAGE_SIZE, filtered.length)} จาก {filtered.length} รายการ
          </p>
          <div className="flex items-center gap-1">
            <PgBtn onClick={() => setPage(1)} disabled={safePage === 1}><ChevronsLeft className="w-4 h-4" /></PgBtn>
            <PgBtn onClick={() => setPage(p => Math.max(1, p - 1))} disabled={safePage === 1}><ChevronLeft className="w-4 h-4" /></PgBtn>
            <span className="px-3 py-1.5 text-sm font-medium text-gray-700">
              {safePage} / {totalPages}
            </span>
            <PgBtn onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={safePage === totalPages}><ChevronRight className="w-4 h-4" /></PgBtn>
            <PgBtn onClick={() => setPage(totalPages)} disabled={safePage === totalPages}><ChevronsRight className="w-4 h-4" /></PgBtn>
          </div>
        </div>
      )}
    </div>
  );
}

function PgBtn({ children, onClick, disabled }: { children: React.ReactNode; onClick: () => void; disabled: boolean }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'p-1.5 rounded-md border border-gray-300 transition-colors',
        disabled ? 'text-gray-300 cursor-not-allowed' : 'text-gray-600 hover:bg-gray-100',
      )}
    >
      {children}
    </button>
  );
}

function fmt(n: number): string {
  return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
