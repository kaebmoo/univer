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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
              <FileSpreadsheet className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">NT P&L Reconciliation</h1>
              <p className="text-xs text-gray-500">ระบบตรวจกระทบยอดงบกำไรขาดทุน — ทำงานใน Browser ไม่ส่งข้อมูลออกนอกเครื่อง</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6 space-y-6">
        {/* File Upload */}
        <section className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-gray-800">อัพโหลดไฟล์</h2>
              <p className="text-xs text-gray-500 mt-0.5">
                Browse เลือกหลายไฟล์พร้อมกัน ระบบจะจำแนกให้อัตโนมัติ
                {uploadedCount > 0 && <span className="text-blue-600 font-medium ml-1">({uploadedCount} ไฟล์)</span>}
              </p>
            </div>
            {hasAnyFile && (
              <button
                onClick={clearFiles}
                disabled={loading}
                className="text-sm text-gray-400 hover:text-red-500 flex items-center gap-1 disabled:opacity-50"
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

          {/* What will run */}
          {hasAllRequired && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200 text-sm text-blue-800">
              <p className="font-medium mb-1">จะรันการตรวจสอบ:</p>
              <ul className="list-disc list-inside space-y-0.5 text-xs">
                <li>BU Level — CSV vs Excel totals, by BU, cross-sheet, column-total, alliance</li>
                <li>SG/Service — Service group, product, EBITDA, EBIT, cross-column</li>
                <li>Enhanced — completeness, cross-sheet consistency, internal math{hasTxt ? ', tie-out กับงบการเงิน' : ''}</li>
                {hasCombined && <li>Combined — ตรวจไฟล์ combined output vs source CSV</li>}
              </ul>
            </div>
          )}

          {/* Warning if not all required */}
          {hasAnyFile && !hasAllRequired && (
            <div className="mt-4 p-3 bg-amber-50 rounded-lg border border-amber-200 text-sm text-amber-800 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <p>ยังขาดไฟล์จำเป็น — อัพโหลดเพิ่มเพื่อรันการตรวจสอบ</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg flex items-start gap-2 border border-red-200 text-sm">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <p>{error}</p>
            </div>
          )}

          {/* Progress */}
          {loading && (
            <div className="mt-4">
              <ProgressBar percent={progress.percent} message={progress.message} />
            </div>
          )}

          {/* Run Button */}
          <div className="mt-6 flex justify-center">
            <button
              onClick={startReconciliation}
              disabled={loading || !hasAnyFile}
              className={cn(
                'flex items-center gap-2 px-8 py-3 rounded-lg font-medium shadow-sm transition-colors',
                loading || !hasAnyFile
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 text-white',
              )}
            >
              {loading
                ? <><RefreshCw className="w-5 h-5 animate-spin" /> กำลังประมวลผล...</>
                : <><Play className="w-5 h-5" /> เริ่มตรวจสอบทั้งหมด</>
              }
            </button>
          </div>
        </section>

        {/* Results */}
        {results && results.length > 0 && (
          <section className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-gray-800">ผลการตรวจสอบ</h2>
              <ExportButton results={results} mode="All" />
            </div>

            <SummaryCards results={results} />

            {results.every(r => r.passed) && (
              <div className="text-center py-8 bg-green-50 rounded-lg border border-green-200">
                <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
                <h3 className="text-xl font-bold text-gray-800">ผ่านทุกรายการ!</h3>
                <p className="text-gray-500 mt-1">{results.length} รายการตรวจสอบทั้งหมดถูกต้อง</p>
              </div>
            )}

            <ResultsTable results={results} />
          </section>
        )}

        {results && results.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <p>ไม่พบรายการตรวจสอบ — ตรวจสอบว่าไฟล์ถูกต้อง</p>
          </div>
        )}
      </main>

      <footer className="text-center py-4 text-xs text-gray-400 border-t border-gray-100 mt-8">
        NT P&L Reconciliation v1.0
      </footer>
    </div>
  );
}
