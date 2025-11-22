/**
 * ReportViewer Component with Univer Integration
 */

import React, { useEffect, useRef } from 'react';
import { Card, Empty, Spin, Alert } from 'antd';
import { FileTextOutlined } from '@ant-design/icons';
import { Univer } from '@univerjs/core';
import { defaultTheme } from '@univerjs/design';
import { UniverDocsPlugin } from '@univerjs/docs';
import { UniverDocsUIPlugin } from '@univerjs/docs-ui';
import { UniverFormulaEnginePlugin } from '@univerjs/engine-formula';
import { UniverRenderEnginePlugin } from '@univerjs/engine-render';
import { UniverSheetsPlugin } from '@univerjs/sheets';
import { UniverSheetsFormulaPlugin } from '@univerjs/sheets-formula';
import { UniverSheetsUIPlugin } from '@univerjs/sheets-ui';
import { UniverUIPlugin } from '@univerjs/ui';

import { useReport } from '../contexts/ReportContext';

export const ReportViewer: React.FC = () => {
  const { univerSnapshot, isLoading, error, currentFilter } = useReport();
  const containerRef = useRef<HTMLDivElement>(null);
  const univerRef = useRef<Univer | null>(null);

  useEffect(() => {
    if (!containerRef.current || !univerSnapshot) return;

    // Clean up previous Univer instance
    if (univerRef.current) {
      univerRef.current.dispose();
      univerRef.current = null;
    }

    // Create new Univer instance
    const univer = new Univer({
      theme: defaultTheme,
      locale: 'th-TH',
    });

    // Register plugins
    univer.registerPlugin(UniverRenderEnginePlugin);
    univer.registerPlugin(UniverFormulaEnginePlugin);
    univer.registerPlugin(UniverUIPlugin, {
      container: containerRef.current,
      header: true,
      toolbar: true,
      footer: true,
    });

    // Sheets plugins
    univer.registerPlugin(UniverSheetsPlugin);
    univer.registerPlugin(UniverSheetsUIPlugin);
    univer.registerPlugin(UniverSheetsFormulaPlugin);

    // Docs plugins
    univer.registerPlugin(UniverDocsPlugin);
    univer.registerPlugin(UniverDocsUIPlugin);

    // Create workbook from snapshot
    univer.createUnit('univer', univerSnapshot);

    univerRef.current = univer;

    // Cleanup on unmount
    return () => {
      if (univerRef.current) {
        univerRef.current.dispose();
        univerRef.current = null;
      }
    };
  }, [univerSnapshot]);

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
          ? `รายงานผลดำเนินงาน ปี ${currentFilter.year} (${currentFilter.months.length} เดือน)`
          : 'รายงานผลดำเนินงาน'
      }
      bodyStyle={{ padding: 0 }}
    >
      <div
        ref={containerRef}
        style={{
          width: '100%',
          height: 'calc(100vh - 300px)',
          minHeight: 600,
        }}
      />
    </Card>
  );
};
