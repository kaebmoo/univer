/**
 * Zustand store — unified file upload, run all reconcilers at once.
 */
import { create } from 'zustand';
import {
  type CheckResult,
  type FileState,
  type WorkerOutMessage,
  type WorkerStartMessage,
  type ReconcilerFlags,
} from '@/lib/types';

interface ReconciliationStore {
  files: FileState;
  results: CheckResult[] | null;
  loading: boolean;
  progress: { percent: number; message: string };
  error: string | null;

  /** Set multiple files at once (from classified browse) */
  setFiles: (map: Record<string, File>) => void;
  /** Remove a single file */
  removeFile: (key: string) => void;
  clearFiles: () => void;
  clearResults: () => void;
  startReconciliation: () => void;
}

export const useReconciliationStore = create<ReconciliationStore>((set, get) => ({
  files: {},
  results: null,
  loading: false,
  progress: { percent: 0, message: '' },
  error: null,

  setFiles: (map) =>
    set((s) => ({
      files: { ...s.files, ...map },
      results: null,
      error: null,
    })),

  removeFile: (key) =>
    set((s) => {
      const next = { ...s.files };
      delete next[key];
      return { files: next, results: null, error: null };
    }),

  clearFiles: () =>
    set({ files: {}, results: null, error: null, progress: { percent: 0, message: '' } }),

  clearResults: () =>
    set({ results: null, error: null }),

  startReconciliation: async () => {
    const state = get();

    const hasAnyFile = Object.keys(state.files).length > 0;

    if (!hasAnyFile) {
      set({ error: 'กรุณาอัพโหลดไฟล์อย่างน้อย 1 ไฟล์' });
      return;
    }

    set({
      loading: true,
      progress: { percent: 0, message: 'กำลังเริ่ม...' },
      error: null,
      results: null,
    });

    try {
      // Convert files to ArrayBuffers
      const fileBuffers: Record<string, ArrayBuffer> = {};
      for (const [key, file] of Object.entries(state.files)) {
        if (file) {
          fileBuffers[key] = await (file as File).arrayBuffer();
        }
      }

      // Determine which reconcilers to run based on available files
      const hasCsvAll = ['costtypeMth', 'costtypeYtd', 'glgroupMth', 'glgroupYtd'].every(k => state.files[k]);
      const hasExcelAll = ['reportMth', 'reportYtd'].every(k => state.files[k]);

      const flags: ReconcilerFlags = {
        buLevel: hasCsvAll && hasExcelAll,
        sgService: hasCsvAll && hasExcelAll,
        enhanced: hasCsvAll && hasExcelAll,
        combined: !!state.files['combinedExcel'] && !!state.files['glgroupMth'] && !!state.files['glgroupYtd'],
      };

      if (!flags.buLevel && !flags.sgService && !flags.enhanced && !flags.combined) {
        set({
          loading: false,
          error: 'ไฟล์ไม่เพียงพอสำหรับการตรวจสอบ — ต้องมี CSV 4 ไฟล์ + Excel 2 ไฟล์ เป็นอย่างน้อย',
        });
        return;
      }

      // Create worker
      const worker = new Worker(
        new URL('../workers/reconciliation.worker.ts', import.meta.url),
        { type: 'module' },
      );

      worker.onmessage = (e: MessageEvent<WorkerOutMessage>) => {
        const msg = e.data;
        switch (msg.type) {
          case 'PROGRESS':
            set({ progress: { percent: msg.percent, message: msg.message } });
            break;
          case 'DONE':
            set({
              loading: false,
              results: msg.results,
              progress: { percent: 100, message: 'เสร็จสิ้น' },
            });
            worker.terminate();
            break;
          case 'ERROR':
            set({
              loading: false,
              error: msg.message,
              progress: { percent: 0, message: '' },
            });
            worker.terminate();
            break;
        }
      };

      worker.onerror = (err) => {
        console.error('Worker onerror:', err);
        set({
          loading: false,
          error: `Worker error: ${err.message || 'Unknown worker error — check browser console (F12)'}`,
        });
        worker.terminate();
      };

      const message: WorkerStartMessage = {
        type: 'START',
        files: fileBuffers,
        flags,
      };

      worker.postMessage(message);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      set({ loading: false, error: message, progress: { percent: 0, message: '' } });
    }
  },
}));
