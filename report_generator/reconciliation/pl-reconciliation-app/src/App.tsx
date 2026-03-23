import { FileSpreadsheet, Play, RefreshCw, CheckCircle, AlertCircle, Trash2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { useReconciliationStore } from '@/stores/reconciliation-store';
import { FileUploadPanel } from '@/components/FileUploadPanel';
import { SummaryCards } from '@/components/SummaryCards';
import { ResultsTable } from '@/components/ResultsTable';
import { ExportButton } from '@/components/ExportButton';
import { ProgressBar } from '@/components/ProgressBar';

const REQUIRED_KEYS = ['costtypeMth', 'costtypeYtd', 'glgroupMth', 'glgroupYtd', 'reportMth', 'reportYtd'];

export default function App() {
  const {
    files,
    results,
    loading,
    progress,
    error,
    setFiles,
    removeFile,
    clearFiles,
    startReconciliation,
  } = useReconciliationStore();

  const hasAllRequired = REQUIRED_KEYS.every(k => files[k]);
  const hasAnyFile = Object.keys(files).filter(k => files[k]).length > 0;
  const hasCombined = !!files['combinedExcel'];
  const hasTxt = !!files['stmtTxt'];
  const uploadedCount = Object.values(files).filter(Boolean).length;
  const readyCount = REQUIRED_KEYS.filter(k => files[k]).length;

  return (
    <div className="min-h-screen text-neutral-950">
      <header className="sticky top-0 z-20 border-b border-black/5 bg-[rgba(244,241,234,0.82)] backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--app-accent)] shadow-[0_10px_24px_rgba(31,94,255,0.28)]">
              <FileSpreadsheet className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="utility-kicker mb-1">NT Finance Workspace</p>
              <h1 className="text-lg font-semibold tracking-[-0.02em] text-neutral-950 sm:text-xl">NT P&amp;L Reconciliation</h1>
            </div>
          </div>
          <div className="hidden items-center gap-6 text-sm text-[var(--app-muted)] md:flex">
            <div>
              <div className="font-medium text-neutral-900">{uploadedCount}</div>
              <div>uploaded</div>
            </div>
            <div>
              <div className="font-medium text-neutral-900">{readyCount}/6</div>
              <div>required</div>
            </div>
            <div className="max-w-[220px] text-right leading-5">
              ทำงานใน browser และไม่ส่งข้อมูลออกนอกเครื่อง
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="grid gap-6 lg:grid-cols-[minmax(0,1.15fr)_320px] lg:items-start">
          <div className="surface-panel-strong soft-grid animate-rise-in overflow-hidden rounded-[28px] p-6 sm:p-8">
            <div className="flex flex-col gap-5 border-b border-black/7 pb-6 sm:flex-row sm:items-end sm:justify-between">
              <div className="max-w-2xl">
                <p className="utility-kicker mb-3">Operational Surface</p>
                <h2 className="max-w-xl text-3xl font-semibold leading-tight tracking-[-0.035em] text-neutral-950 sm:text-4xl">
                  ตรวจงบจาก source data ถึง report ได้ในหน้าเดียว
                </h2>
                <p className="mt-3 max-w-xl text-sm leading-6 text-[var(--app-muted)] sm:text-[15px]">
                  อัปโหลดไฟล์ที่ต้องใช้ ระบบจะจำแนกชนิดไฟล์อัตโนมัติและรันชุดตรวจหลักตามข้อมูลที่มีอยู่โดยไม่เปลี่ยน workflow เดิมของทีม
                </p>
              </div>
              <div className="grid grid-cols-3 gap-3 text-sm sm:min-w-[260px]">
                <div className="rounded-2xl border border-black/8 bg-white/70 p-3">
                  <div className="text-[11px] uppercase tracking-[0.14em] text-[var(--app-muted)]">Uploaded</div>
                  <div className="mt-2 text-2xl font-semibold tracking-[-0.03em] text-neutral-950">{uploadedCount}</div>
                </div>
                <div className="rounded-2xl border border-black/8 bg-white/70 p-3">
                  <div className="text-[11px] uppercase tracking-[0.14em] text-[var(--app-muted)]">Required</div>
                  <div className="mt-2 text-2xl font-semibold tracking-[-0.03em] text-neutral-950">{readyCount}/6</div>
                </div>
                <div className="rounded-2xl border border-black/8 bg-white/70 p-3">
                  <div className="text-[11px] uppercase tracking-[0.14em] text-[var(--app-muted)]">Mode</div>
                  <div className="mt-2 text-sm font-medium leading-5 text-neutral-950">Browser-local</div>
                </div>
              </div>
            </div>

            <div className="mt-6 flex flex-wrap items-center gap-3 text-xs text-[var(--app-muted)]">
              <span className="rounded-full border border-black/8 bg-white/65 px-3 py-1.5">4 CSV source files</span>
              <span className="rounded-full border border-black/8 bg-white/65 px-3 py-1.5">2 Excel reports</span>
              <span className="rounded-full border border-black/8 bg-white/65 px-3 py-1.5">Optional combined / txt</span>
            </div>

            <div className="mt-8">
              <div className="mb-4 flex items-center justify-between gap-4">
                <div>
                  <h3 className="text-base font-semibold text-neutral-900">อัปโหลดไฟล์</h3>
                  <p className="mt-1 text-sm text-[var(--app-muted)]">
                    เลือกหลายไฟล์พร้อมกันได้ ระบบจะจัดหมวดให้จากชื่อไฟล์
                  </p>
                </div>
                {hasAnyFile && (
                  <button
                    onClick={clearFiles}
                    disabled={loading}
                    className="inline-flex items-center gap-1.5 rounded-full border border-black/8 bg-white/75 px-3 py-2 text-sm text-[var(--app-muted)] transition-colors hover:border-red-200 hover:text-red-600 disabled:opacity-50"
                  >
                    <Trash2 className="w-3.5 h-3.5" /> ล้างทั้งหมด
                  </button>
                )}
              </div>

              <FileUploadPanel
                files={files}
                onFilesClassified={setFiles}
                onFileRemove={removeFile}
                disabled={loading}
              />

              {hasAllRequired && (
                <div className="mt-6 rounded-2xl border border-[var(--app-accent-soft)] bg-[rgba(31,94,255,0.07)] p-4 text-sm text-neutral-800">
                  <p className="mb-2 font-medium text-neutral-950">จะรันการตรวจสอบ</p>
                  <ul className="space-y-1 text-sm leading-6 text-[var(--app-muted)]">
                    <li>BU Level: totals, by BU, cross-sheet, column-total, alliance</li>
                    <li>SG/Service: service group, product, EBITDA, EBIT, cross-column</li>
                    <li>Enhanced: completeness, cross-sheet consistency, internal math{hasTxt ? ', tie-out กับงบการเงิน' : ''}</li>
                    {hasCombined && <li>Combined: เทียบ combined output กับ source CSV</li>}
                  </ul>
                </div>
              )}

              {hasAnyFile && !hasAllRequired && (
                <div className="mt-6 flex items-start gap-2 rounded-2xl border border-amber-200 bg-amber-50/90 p-4 text-sm text-amber-900">
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                  <p>ยังขาดไฟล์จำเป็น อัปโหลดให้ครบ 6 ไฟล์หลักเพื่อเริ่มชุดตรวจหลัก</p>
                </div>
              )}

              {error && (
                <div className="mt-6 flex items-start gap-2 rounded-2xl border border-red-200 bg-red-50/90 p-4 text-sm text-red-700">
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                  <p>{error}</p>
                </div>
              )}

              {loading && (
                <div className="mt-6">
                  <ProgressBar percent={progress.percent} message={progress.message} />
                </div>
              )}
            </div>
          </div>

          <aside className="surface-panel sticky top-24 animate-rise-in rounded-[28px] p-5 sm:p-6">
            <p className="utility-kicker mb-3">Run Control</p>
            <h3 className="text-xl font-semibold tracking-[-0.03em] text-neutral-950">พร้อมตรวจสอบเมื่อข้อมูลครบ</h3>
            <p className="mt-3 text-sm leading-6 text-[var(--app-muted)]">
              ปุ่มรันจะเริ่มประมวลผลจากไฟล์ที่อัปโหลดในเครื่องทันที และแสดงผลสรุปพร้อมตารางสำหรับค้นหาและ export
            </p>

            <div className="mt-6 space-y-3 border-y border-black/7 py-4 text-sm text-[var(--app-muted)]">
              <div className="flex items-center justify-between">
                <span>CSV source</span>
                <span className="font-medium text-neutral-900">{['costtypeMth', 'costtypeYtd', 'glgroupMth', 'glgroupYtd'].filter(k => files[k]).length}/4</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Excel report</span>
                <span className="font-medium text-neutral-900">{['reportMth', 'reportYtd'].filter(k => files[k]).length}/2</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Optional data</span>
                <span className="font-medium text-neutral-900">{['combinedExcel', 'stmtTxt'].filter(k => files[k]).length}/2</span>
              </div>
            </div>

            <button
              onClick={startReconciliation}
              disabled={loading || !hasAnyFile}
              className={cn(
                'mt-6 flex w-full items-center justify-center gap-2 rounded-2xl px-5 py-4 text-sm font-medium transition-all',
                loading || !hasAnyFile
                  ? 'cursor-not-allowed bg-neutral-200 text-neutral-500'
                  : 'bg-[var(--app-accent)] text-white shadow-[0_18px_32px_rgba(31,94,255,0.24)] hover:translate-y-[-1px] hover:bg-[#1a52df]',
              )}
            >
              {loading
                ? <><RefreshCw className="w-5 h-5 animate-spin" /> กำลังประมวลผล...</>
                : <><Play className="w-5 h-5" /> เริ่มตรวจสอบทั้งหมด</>
              }
            </button>

            <p className="mt-4 text-xs leading-5 text-[var(--app-muted)]">
              รองรับการรัน BU Level, SG/Service, Enhanced และ Combined ตามไฟล์ที่มีอยู่ในรอบนั้น
            </p>
          </aside>
        </section>

        {results && results.length > 0 && (
          <section className="surface-panel-strong animate-rise-in mt-6 rounded-[28px] p-6 sm:p-8">
            <div className="flex flex-col gap-3 border-b border-black/7 pb-5 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="utility-kicker mb-2">Results</p>
                <h2 className="text-2xl font-semibold tracking-[-0.03em] text-neutral-950">ผลการตรวจสอบ</h2>
                <p className="mt-1 text-sm text-[var(--app-muted)]">สรุปสถานะทั้งหมด พร้อมตัวกรองและ export สำหรับการตรวจสอบต่อ</p>
              </div>
              <ExportButton results={results} mode="All" />
            </div>

            <div className="mt-6">
              <SummaryCards results={results} />
            </div>

            {results.every(r => r.passed) && (
              <div className="mt-6 rounded-[24px] border border-emerald-200 bg-emerald-50/80 px-6 py-8 text-center">
                <CheckCircle className="mx-auto mb-3 h-12 w-12 text-emerald-600" />
                <h3 className="text-xl font-semibold tracking-[-0.03em] text-neutral-950">ผ่านทุกรายการ</h3>
                <p className="mt-1 text-sm text-[var(--app-muted)]">{results.length} รายการตรวจสอบทั้งหมดถูกต้อง</p>
              </div>
            )}

            <div className="mt-6">
              <ResultsTable results={results} />
            </div>
          </section>
        )}

        {results && results.length === 0 && (
          <div className="surface-panel mt-6 rounded-[28px] px-6 py-12 text-center text-[var(--app-muted)]">
            <p>ไม่พบรายการตรวจสอบ — ตรวจสอบว่าไฟล์ถูกต้อง</p>
          </div>
        )}
      </main>

      <footer className="mx-auto mt-8 max-w-7xl border-t border-black/6 px-4 py-4 text-center text-xs text-[var(--app-muted)] sm:px-6 lg:px-8">
        NT P&L Reconciliation v1.0
      </footer>
    </div>
  );
}
