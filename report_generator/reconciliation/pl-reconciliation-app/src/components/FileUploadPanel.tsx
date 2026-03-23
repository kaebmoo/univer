import { useRef } from 'react';
import { FileCheck, X, FileText, FileSpreadsheet, Upload, AlertTriangle } from 'lucide-react';
import { cn } from '@/utils/cn';
import { classifyFiles, getFileLabel, type FileKey } from '@/lib/file-classifier';
import type { FileState } from '@/lib/types';

interface Props {
  files: FileState;
  onFilesClassified: (classified: Record<string, File>) => void;
  onFileRemove: (key: string) => void;
  disabled?: boolean;
}

const CSV_KEYS: FileKey[] = ['costtypeMth', 'costtypeYtd', 'glgroupMth', 'glgroupYtd'];
const EXCEL_KEYS: FileKey[] = ['reportMth', 'reportYtd'];
const OPTIONAL_KEYS: FileKey[] = ['combinedExcel', 'stmtTxt'];

export function FileUploadPanel({ files, onFilesClassified, onFileRemove, disabled }: Props) {
  const csvRef = useRef<HTMLInputElement>(null);
  const excelRef = useRef<HTMLInputElement>(null);
  const optionalRef = useRef<HTMLInputElement>(null);

  const handleBrowse = (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    if (!fileList || fileList.length === 0) return;

    const arr = Array.from(fileList);
    const { classified, unrecognized } = classifyFiles(arr);

    if (unrecognized.length > 0) {
      const names = unrecognized.map(f => f.name).join(', ');
      alert(`ไม่สามารถระบุไฟล์ได้: ${names}\n\nกรุณาตรวจสอบชื่อไฟล์ให้ตรงกับรูปแบบ เช่น\n- TRN_PL_COSTTYPE_NT_MTH_TABLE_*.csv\n- Report_NT_*.xlsx`);
    }

    if (classified.length > 0) {
      const map: Record<string, File> = {};
      for (const c of classified) {
        map[c.key] = c.file;
      }
      onFilesClassified(map);
    }

    // Reset input so same files can be re-selected
    e.target.value = '';
  };

  const csvCount = CSV_KEYS.filter(k => files[k]).length;
  const excelCount = EXCEL_KEYS.filter(k => files[k]).length;
  const optionalCount = OPTIONAL_KEYS.filter(k => files[k]).length;

  return (
    <div className="space-y-4">
      {/* CSV Browse */}
      <DropZone
        icon={<FileText className="w-5 h-5 text-blue-500" />}
        title="CSV Source Data"
        subtitle={`เลือก 4 ไฟล์: COSTTYPE MTH/YTD + GLGROUP MTH/YTD`}
        count={csvCount}
        total={4}
        accept=".csv"
        inputRef={csvRef}
        onChange={handleBrowse}
        disabled={disabled}
      />
      <FileList keys={CSV_KEYS} files={files} onRemove={onFileRemove} />

      {/* Optional Browse */}
      <DropZone
        icon={<FileText className="w-5 h-5 text-amber-500" />}
        title="ไฟล์เสริม (ไม่บังคับ)"
        subtitle="Combined Excel (.xlsx) / Financial Statement (.txt)"
        count={optionalCount}
        total={2}
        accept=".xlsx,.xls,.txt"
        inputRef={optionalRef}
        onChange={handleBrowse}
        disabled={disabled}
        optional
      />
      <FileList keys={OPTIONAL_KEYS} files={files} onRemove={onFileRemove} />

      {/* Excel Browse */}
      <DropZone
        icon={<FileSpreadsheet className="w-5 h-5 text-green-600" />}
        title="Excel Reports"
        subtitle="เลือก 2 ไฟล์: Report MTH + Report YTD"
        count={excelCount}
        total={2}
        accept=".xlsx,.xls"
        inputRef={excelRef}
        onChange={handleBrowse}
        disabled={disabled}
      />
      <FileList keys={EXCEL_KEYS} files={files} onRemove={onFileRemove} />
    </div>
  );
}

// ==========================================
// Sub-components
// ==========================================

function DropZone({
  icon,
  title,
  subtitle,
  count,
  total,
  accept,
  inputRef,
  onChange,
  disabled,
  optional,
}: {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
  count: number;
  total: number;
  accept: string;
  inputRef: React.RefObject<HTMLInputElement | null>;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  disabled?: boolean;
  optional?: boolean;
}) {
  const allDone = count === total;

  return (
    <button
      type="button"
      onClick={() => inputRef.current?.click()}
      disabled={disabled}
      className={cn(
        'w-full flex items-center gap-4 rounded-[22px] border p-4 text-left transition-colors sm:p-5',
        allDone
          ? 'border-emerald-200 bg-emerald-50/75'
          : 'border-black/8 bg-white/70 hover:border-[var(--app-accent)]/35 hover:bg-white/90',
        disabled && 'opacity-50 cursor-not-allowed',
      )}
    >
      <div className="shrink-0">{icon}</div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-900 text-sm">{title}</span>
          {!optional && count < total && (
            <span className="text-xs text-red-500 font-medium">*จำเป็น</span>
          )}
        </div>
        <p className="text-xs text-[var(--app-muted)] mt-0.5">{subtitle}</p>
      </div>
      <div className="shrink-0 flex items-center gap-2">
        <span className={cn(
          'text-sm font-medium',
          allDone ? 'text-emerald-700' : 'text-[var(--app-muted)]',
        )}>
          {count}/{total}
        </span>
        <Upload className="w-4 h-4 text-[var(--app-muted)]" />
      </div>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple
        onChange={onChange}
        className="hidden"
      />
    </button>
  );
}

function FileList({
  keys,
  files,
  onRemove,
}: {
  keys: FileKey[];
  files: FileState;
  onRemove: (key: string) => void;
}) {
  const items = keys.filter(k => files[k]);
  if (items.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 pl-1">
      {items.map(key => {
        const file = files[key] as File;
        return (
          <div
            key={key}
            className="flex items-center gap-1.5 rounded-full border border-black/8 bg-white/80 px-3 py-1.5 text-xs"
          >
            <FileCheck className="w-3 h-3 text-green-500 shrink-0" />
            <span className="text-[var(--app-muted)]">{getFileLabel(key as FileKey)}:</span>
            <span className="text-gray-900 font-medium truncate max-w-[180px]">{file.name}</span>
            <button
              onClick={() => onRemove(key)}
              className="text-gray-300 hover:text-red-500 ml-1"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        );
      })}
      {/* Show missing required files */}
      {keys.filter(k => !files[k]).map(key => (
        <div
          key={key}
          className="flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50/85 px-3 py-1.5 text-xs"
        >
          <AlertTriangle className="w-3 h-3 text-amber-500 shrink-0" />
          <span className="text-amber-700">{getFileLabel(key as FileKey)}</span>
          <span className="text-amber-500">— ยังไม่ได้อัพโหลด</span>
        </div>
      ))}
    </div>
  );
}
