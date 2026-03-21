/**
 * Web Worker for reconciliation processing.
 * Runs ALL reconcilers in one pass from unified file upload.
 */
import * as XLSX from 'xlsx';
import { ValidationLevel, type CheckResult, type WorkerStartMessage, type WorkerOutMessage } from '@/lib/types';
import { parseCSVFromBuffer, type CsvRow } from '@/lib/csv-reader';
import { parseTextFromBuffer } from '@/lib/text-reader';
import { ExcelSheetReader, readSheetAsArray } from '@/lib/excel-reader';
import { SHEETS } from '@/lib/constants';

// Reconcilers
import {
  reconcileCsvVsExcelTotals,
  reconcileCsvVsExcelByBu,
  reconcileCrossSheet,
  checkColumnTotal,
  checkAllianceConsistency,
} from '@/lib/reconcilers/bu-level';
import { runEnhancedReconciliation } from '@/lib/reconcilers/enhanced';
import { runCombinedReconciliation } from '@/lib/reconcilers/combined';
import {
  reconcileServiceGroup,
  reconcileProduct,
  reconcileEbitdaSg,
  reconcileEbitdaProduct,
  reconcileEbitSg,
  reconcileEbitProduct,
  reconcileCrossColumn,
  reconcileColumnTotal as reconcileColumnTotalSg,
  reconcileCrossSheetTotal,
  reconcileCrossSheetSg,
  reconcileCrossSheetProduct,
} from '@/lib/reconcilers/sg-svc';

function post(msg: WorkerOutMessage) {
  self.postMessage(msg);
}

function progress(percent: number, message: string) {
  post({ type: 'PROGRESS', percent, message });
}

function readExcel(buffer: ArrayBuffer): XLSX.WorkBook {
  return XLSX.read(buffer, { type: 'array' });
}

function tryParseCsv(buffer: ArrayBuffer | undefined): CsvRow[] | null {
  if (!buffer) return null;
  try {
    return parseCSVFromBuffer(buffer);
  } catch {
    return null;
  }
}

function tryReadExcel(buffer: ArrayBuffer | undefined): XLSX.WorkBook | null {
  if (!buffer) return null;
  try {
    return readExcel(buffer);
  } catch {
    return null;
  }
}

self.onmessage = async (e: MessageEvent<WorkerStartMessage>) => {
  const { files, flags, options } = e.data;

  try {
    const results: CheckResult[] = [];

    // ==========================================
    // 1. Parse files — only what's available
    // ==========================================
    progress(5, 'กำลังอ่านไฟล์...');

    const costCsvMth = tryParseCsv(files['costtypeMth']);
    const costCsvYtd = tryParseCsv(files['costtypeYtd']);
    const glCsvMth = tryParseCsv(files['glgroupMth']);
    const glCsvYtd = tryParseCsv(files['glgroupYtd']);

    progress(10, 'กำลังอ่าน Excel...');

    const wbMth = tryReadExcel(files['reportMth']);
    const wbYtd = tryReadExcel(files['reportYtd']);

    const stmtLines = files['stmtTxt'] ? parseTextFromBuffer(files['stmtTxt']) : null;

    // Check if we have enough data
    const hasCsv = costCsvMth && costCsvYtd && glCsvMth && glCsvYtd;
    const hasExcel = wbMth && wbYtd;

    if (!hasCsv || !hasExcel) {
      post({
        type: 'ERROR',
        message: `ไฟล์ไม่เพียงพอ: ${!hasCsv ? 'ขาด CSV บางไฟล์' : ''}${!hasCsv && !hasExcel ? ' และ ' : ''}${!hasExcel ? 'ขาด Excel บางไฟล์' : ''}`,
      });
      return;
    }

    let currentProgress = 20;

    // ==========================================
    // 2. BU Level (reconcile_nt_pl.py)
    // ==========================================
    if (flags.buLevel) {
      progress(currentProgress, 'BU Level: กำลังตรวจสอบ...');

      for (const period of ['MTH', 'YTD'] as const) {
        const wb = period === 'MTH' ? wbMth : wbYtd;
        const costCsv = period === 'MTH' ? costCsvMth : costCsvYtd;
        const glCsv = period === 'MTH' ? glCsvMth : glCsvYtd;

        try {
          // CSV vs Excel — COSTTYPE → ต้นทุน_กลุ่มธุรกิจ
          if (wb.Sheets[SHEETS.cost_biz]) {
            const costBizReader = new ExcelSheetReader(wb.Sheets[SHEETS.cost_biz], SHEETS.cost_biz);
            results.push(...reconcileCsvVsExcelTotals(costCsv, costBizReader, 'COSTTYPE', period, SHEETS.cost_biz));
            results.push(...reconcileCsvVsExcelByBu(costCsv, costBizReader, 'COSTTYPE', period, SHEETS.cost_biz));
          }

          // CSV vs Excel — GLGROUP → หมวดบัญชี_กลุ่มธุรกิจ
          if (wb.Sheets[SHEETS.gl_biz]) {
            const glBizReader = new ExcelSheetReader(wb.Sheets[SHEETS.gl_biz], SHEETS.gl_biz);
            results.push(...reconcileCsvVsExcelTotals(glCsv, glBizReader, 'GLGROUP', period, SHEETS.gl_biz));
            results.push(...reconcileCsvVsExcelByBu(glCsv, glBizReader, 'GLGROUP', period, SHEETS.gl_biz));
          }

          // Cross-sheet
          const levels = [
            { name: 'กลุ่มธุรกิจ', cost: SHEETS.cost_biz, gl: SHEETS.gl_biz },
            { name: 'กลุ่มบริการ', cost: SHEETS.cost_sg, gl: SHEETS.gl_sg },
            { name: 'บริการ', cost: SHEETS.cost_svc, gl: SHEETS.gl_svc },
          ];
          for (const lv of levels) {
            if (wb.Sheets[lv.cost] && wb.Sheets[lv.gl]) {
              const cr = new ExcelSheetReader(wb.Sheets[lv.cost], lv.cost);
              const gr = new ExcelSheetReader(wb.Sheets[lv.gl], lv.gl);
              results.push(...reconcileCrossSheet(cr, gr, period, lv.name));
            }
          }

          // Column-Total & Alliance
          for (const sheetKey of ['cost_biz', 'gl_biz'] as const) {
            if (wb.Sheets[SHEETS[sheetKey]]) {
              const reader = new ExcelSheetReader(wb.Sheets[SHEETS[sheetKey]], SHEETS[sheetKey]);
              results.push(...checkColumnTotal(reader, period, SHEETS[sheetKey]));
            }
          }
          for (const sheetKey of ['cost_biz', 'gl_biz', 'cost_sg', 'gl_sg'] as const) {
            if (wb.Sheets[SHEETS[sheetKey]]) {
              const reader = new ExcelSheetReader(wb.Sheets[SHEETS[sheetKey]], SHEETS[sheetKey]);
              results.push(...checkAllianceConsistency(reader, period, SHEETS[sheetKey]));
            }
          }
        } catch (err) {
          console.error(`BU Level ${period} error:`, err);
        }
      }
      currentProgress = 35;
    }

    // ==========================================
    // 3. SG/Service (reconcile_sg_svc_v2.py)
    // ==========================================
    if (flags.sgService) {
      progress(currentProgress, 'SG/Service: กำลังตรวจสอบ...');

      // Python pattern: SG functions → กลุ่มบริการ sheet, Product functions → บริการ sheet
      // sheet_sg = {COSTTYPE: ต้นทุน_กลุ่มบริการ, GLGROUP: หมวดบัญชี_กลุ่มบริการ}
      // sheet_svc = {COSTTYPE: ต้นทุน_บริการ, GLGROUP: หมวดบัญชี_บริการ}
      const sheetSg: Record<string, string> = { COSTTYPE: SHEETS.cost_sg, GLGROUP: SHEETS.gl_sg };
      const sheetSvc: Record<string, string> = { COSTTYPE: SHEETS.cost_svc, GLGROUP: SHEETS.gl_svc };

      for (const period of ['MTH', 'YTD'] as const) {
        const wb = period === 'MTH' ? wbMth : wbYtd;
        const costCsv = period === 'MTH' ? costCsvMth : costCsvYtd;
        const glCsv = period === 'MTH' ? glCsvMth : glCsvYtd;

        for (const csvType of ['COSTTYPE', 'GLGROUP'] as const) {
          const csv = csvType === 'COSTTYPE' ? costCsv : glCsv;

          // --- SG-level checks on กลุ่มบริการ sheet ---
          const sgSheetName = sheetSg[csvType];
          const wsSg = wb.Sheets[sgSheetName];
          if (wsSg) {
            try {
              const sgData = readSheetAsArray(wsSg);
              results.push(...reconcileServiceGroup(csv, sgData, csvType, period, sgSheetName));
              results.push(...reconcileEbitSg(csv, sgData, csvType, period, sgSheetName));
              results.push(...reconcileEbitdaSg(csv, sgData, csvType, period, sgSheetName));
              results.push(...reconcileCrossColumn(sgData, period, sgSheetName));
            } catch (err) {
              console.error(`SG ${csvType} ${sgSheetName} ${period} error:`, err);
            }
          }

          // --- Product-level checks on บริการ sheet ---
          const svcSheetName = sheetSvc[csvType];
          const wsSvc = wb.Sheets[svcSheetName];
          if (wsSvc) {
            try {
              const svcData = readSheetAsArray(wsSvc);
              results.push(...reconcileProduct(csv, svcData, csvType, period, svcSheetName));
              results.push(...reconcileEbitProduct(csv, svcData, csvType, period, svcSheetName));
              results.push(...reconcileEbitdaProduct(csv, svcData, csvType, period, svcSheetName));
              results.push(...reconcileCrossColumn(svcData, period, svcSheetName));
            } catch (err) {
              console.error(`Product ${csvType} ${svcSheetName} ${period} error:`, err);
            }
          }
        }

        // Column-Total checks (all 4 SG/SVC sheets)
        for (const sheetKey of [SHEETS.cost_sg, SHEETS.cost_svc, SHEETS.gl_sg, SHEETS.gl_svc]) {
          const ws = wb.Sheets[sheetKey];
          if (!ws) continue;
          try {
            const data = readSheetAsArray(ws);
            results.push(...reconcileColumnTotalSg(data, period, sheetKey));
          } catch (err) {
            console.error(`Column-Total ${sheetKey} ${period} error:`, err);
          }
        }

        // Cross-sheet checks
        for (const { costSheet, glSheet, level } of [
          { level: 'กลุ่มบริการ', costSheet: SHEETS.cost_sg, glSheet: SHEETS.gl_sg },
          { level: 'บริการ', costSheet: SHEETS.cost_svc, glSheet: SHEETS.gl_svc },
        ]) {
          const wsCost = wb.Sheets[costSheet];
          const wsGl = wb.Sheets[glSheet];
          if (!wsCost || !wsGl) continue;

          try {
            const costSheetData = readSheetAsArray(wsCost);
            const glSheetData = readSheetAsArray(wsGl);

            results.push(...reconcileCrossSheetTotal(costSheetData, glSheetData, period, level));
            results.push(...reconcileCrossSheetSg(costSheetData, glSheetData, period));
            results.push(...reconcileCrossSheetProduct(costSheetData, glSheetData, period));
          } catch (err) {
            console.error(`SG Cross-sheet ${level} ${period} error:`, err);
          }
        }

        progress(currentProgress + (period === 'MTH' ? 10 : 20), `SG/Service: ${period} เสร็จ`);
      }
      currentProgress = 65;
    }

    // ==========================================
    // 4. Enhanced (pl_reconciliation_enhanced.py)
    // ==========================================
    if (flags.enhanced) {
      progress(currentProgress, 'Enhanced: กำลังตรวจสอบ...');
      const validationLevel = options?.validationLevel ?? ValidationLevel.ENHANCED;

      try {
        results.push(...runEnhancedReconciliation(
          wbMth, costCsvMth, glCsvMth, stmtLines, 'MTH', validationLevel,
        ));
        results.push(...runEnhancedReconciliation(
          wbYtd, costCsvYtd, glCsvYtd, stmtLines, 'YTD', validationLevel,
        ));
      } catch (err) {
        console.error('Enhanced error:', err);
      }
      currentProgress = 80;
    }

    // ==========================================
    // 5. Combined (pl_reconciliation_combined.py)
    // ==========================================
    if (flags.combined && files['combinedExcel']) {
      progress(currentProgress, 'Combined: กำลังตรวจสอบ...');
      try {
        const combinedWb = readExcel(files['combinedExcel']);
        results.push(...runCombinedReconciliation(combinedWb, glCsvMth, glCsvYtd));
      } catch (err) {
        console.error('Combined error:', err);
      }
    }

    progress(100, 'เสร็จสิ้น');
    post({ type: 'DONE', results });
  } catch (err: unknown) {
    const message = err instanceof Error
      ? `${err.message}\n${(err as Error).stack ?? ''}`
      : String(err);
    post({ type: 'ERROR', message });
  }
};
