/**
 * ReportViewer Component with Univer Integration
 */

import React, { useEffect, useRef } from 'react';
import { Card, Empty, Spin, Alert, Button, Space, message } from 'antd';
import { FileTextOutlined, DownloadOutlined } from '@ant-design/icons';
import { createUniver } from '@univerjs/presets';
import { UniverSheetsPreset } from '@univerjs/preset-sheets-core';
import '@univerjs/presets/lib/styles/preset-sheets-core.css';

import { useReport } from '../contexts/ReportContext';

export const ReportViewer: React.FC = () => {
  const { univerSnapshot, isLoading, error, currentFilter, exportReport } = useReport();
  const containerRef = useRef<HTMLDivElement>(null);
  const univerRef = useRef<any>(null);

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
    if (!containerRef.current || !univerSnapshot) return;

    // Clean up previous Univer instance
    if (univerRef.current) {
      univerRef.current.dispose();
      univerRef.current = null;
    }

    // Create Univer instance using preset
    const { univerAPI } = createUniver({
      locale: 'en-US',
      presets: [
        UniverSheetsPreset({
          container: containerRef.current,
        }),
      ],
    });

    // Create workbook from snapshot
    univerAPI.createUniverSheet(univerSnapshot);

    univerRef.current = univerAPI;

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
