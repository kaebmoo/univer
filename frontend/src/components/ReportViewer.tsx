/**
 * ReportViewer Component with Univer Integration
 */

import React, { useEffect, useRef, useState } from 'react';
import { Card, Empty, Spin, Alert, Button, Space, message } from 'antd';
import { FileTextOutlined, DownloadOutlined } from '@ant-design/icons';
import { Univer, UniverInstanceType, LocaleType, Tools } from '@univerjs/core';
import { defaultTheme } from '@univerjs/design';
import { UniverDocsPlugin } from '@univerjs/docs';
import { UniverDocsUIPlugin } from '@univerjs/docs-ui';
import { UniverFormulaEnginePlugin } from '@univerjs/engine-formula';
import { UniverRenderEnginePlugin } from '@univerjs/engine-render';
import { UniverSheetsPlugin } from '@univerjs/sheets';
import { UniverSheetsFormulaPlugin } from '@univerjs/sheets-formula';
import { UniverSheetsUIPlugin } from '@univerjs/sheets-ui';
import { UniverUIPlugin } from '@univerjs/ui';
import { UniverSheetsNumfmtPlugin } from '@univerjs/sheets-numfmt';
import { UniverSheetsNumfmtUIPlugin } from '@univerjs/sheets-numfmt-ui';

// CSS Imports

import '@univerjs/design/lib/index.css'
import '@univerjs/ui/lib/index.css'
import '@univerjs/docs-ui/lib/index.css'
import '@univerjs/sheets-ui/lib/index.css'
import '@univerjs/sheets-formula-ui/lib/index.css'
import '@univerjs/sheets-numfmt-ui/lib/index.css'

import { useReport } from '../contexts/ReportContext';

const MONTH_NAMES_TH_SHORT = [
  'ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.',
  'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'
];

export const ReportViewer: React.FC = () => {
  const { univerSnapshot, isLoading, error, currentFilter, exportReport } = useReport();
  const containerRef = useRef<HTMLDivElement>(null);
  const univerRef = useRef<Univer | null>(null);
  const [containerKey, setContainerKey] = useState(0);

  const getMonthRangeLabel = () => {
    if (!currentFilter || !currentFilter.months || currentFilter.months.length === 0) {
      return '';
    }

    const sortedMonths = [...currentFilter.months].sort((a, b) => a - b);
    const thaiYear = currentFilter.year + 543;

    if (sortedMonths.length === 1) {
      return `${MONTH_NAMES_TH_SHORT[sortedMonths[0] - 1]} ${thaiYear}`;
    }

    const firstMonth = MONTH_NAMES_TH_SHORT[sortedMonths[0] - 1];
    const lastMonth = MONTH_NAMES_TH_SHORT[sortedMonths[sortedMonths.length - 1] - 1];

    return `${firstMonth} - ${lastMonth} ${thaiYear}`;
  };

  const handleExport = async () => {
    if (!currentFilter) {
      message.warning('กรุณาสร้างรายงานก่อนทำการ Export');
      return;
    }

    try {
      await exportReport(currentFilter);
      message.success('ดาวน์โหลดไฟล์ Excel สำเร็จ');
    } catch (err) {
      message.error('เกิดข้อผิดพลาดในการ Export');
    }
  };

  useEffect(() => {
    if (!univerSnapshot) return;

    // Dispose previous instance before creating new one
    if (univerRef.current) {
      try {
        univerRef.current.dispose();
      } catch (error) {
        console.error('Error disposing previous Univer instance:', error);
      }
      univerRef.current = null;
    }

    // Force React to create a new container element by incrementing key
    setContainerKey(prev => prev + 1);
  }, [univerSnapshot]);

  useEffect(() => {
    if (!containerRef.current || !univerSnapshot) return;

    // Use requestAnimationFrame to ensure DOM is ready after re-render
    const frameId = requestAnimationFrame(() => {
      if (!containerRef.current || !univerSnapshot) return;

      try {
        // Create new Univer instance
        const univer = new Univer({
          theme: defaultTheme,
          locale: LocaleType.EN_US,
          locales: {
            [LocaleType.EN_US]: {},
          },
        });

        // Register core plugins in correct order
        univer.registerPlugin(UniverRenderEnginePlugin);
        univer.registerPlugin(UniverUIPlugin, {
          container: containerRef.current,
        });

        // Register Docs plugins
        univer.registerPlugin(UniverDocsPlugin);
        univer.registerPlugin(UniverDocsUIPlugin);

        // Register Sheets plugins
        univer.registerPlugin(UniverSheetsPlugin);
        univer.registerPlugin(UniverSheetsUIPlugin);
        
        // Register Number Format plugins (IMPORTANT: Must be before formula plugins)
        univer.registerPlugin(UniverSheetsNumfmtPlugin);
        univer.registerPlugin(UniverSheetsNumfmtUIPlugin);

        // Register Formula plugins
        univer.registerPlugin(UniverFormulaEnginePlugin);
        univer.registerPlugin(UniverSheetsFormulaPlugin);

        // Create workbook from snapshot
        univer.createUnit(UniverInstanceType.UNIVER_SHEET, univerSnapshot);

        // Store instance reference
        univerRef.current = univer;
      } catch (error) {
        console.error('Error creating Univer instance:', error);
      }
    });

    // Cleanup function
    return () => {
      cancelAnimationFrame(frameId);

      // Dispose Univer instance on unmount
      if (univerRef.current) {
        try {
          univerRef.current.dispose();
        } catch (error) {
          console.error('Error disposing Univer on cleanup:', error);
        }
        univerRef.current = null;
      }
    };
  }, [containerKey, univerSnapshot]);

  if (error) {
    return (
      <Card>
        <Alert
          message="เกิดข้อผิดพลาดในการโหลดรายงาน"
          description={error}
          type="error"
          showIcon
        />
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <Spin size="large" tip="กำลังสร้างรายงาน..." />
        </div>
      </Card>
    );
  }

  if (!univerSnapshot) {
    return (
      <Card>
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="กรุณาเลือกตัวกรองและกดสร้างรายงาน"
          icon={<FileTextOutlined style={{ fontSize: 48 }} />}
        />
      </Card>
    );
  }

  return (
    <Card
      title={
        currentFilter
          ? `รายงานผลดำเนินงาน ${getMonthRangeLabel()}`
          : 'รายงานผลดำเนินงาน'
      }
      extra={
        univerSnapshot && currentFilter && (
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            onClick={handleExport}
            loading={isLoading}
          >
            Export to Excel
          </Button>
        )
      }
      styles={{ body: { padding: 0 } }}
    >
      <div
        key={`univer-container-${containerKey}`}
        ref={containerRef}
        style={{
          width: '100%',
          height: 'calc(100vh - 200px)',
          minHeight: 700,
        }}
      />
    </Card>
  );
};
