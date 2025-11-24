/**
 * FilterPanel Component
 */

import React, { useEffect, useState } from 'react';
import { Card, Form, Select, Button, Space, Alert, Checkbox, Row, Col } from 'antd';
import { FilterOutlined, FileSearchOutlined } from '@ant-design/icons';
import { useReport } from '../contexts/ReportContext';
import type { ReportFilter } from '../types';

const { Option } = Select;

const MONTHS = [
  { value: 1, label: 'มกราคม' },
  { value: 2, label: 'กุมภาพันธ์' },
  { value: 3, label: 'มีนาคม' },
  { value: 4, label: 'เมษายน' },
  { value: 5, label: 'พฤษภาคม' },
  { value: 6, label: 'มิถุนายน' },
  { value: 7, label: 'กรกฎาคม' },
  { value: 8, label: 'สิงหาคม' },
  { value: 9, label: 'กันยายน' },
  { value: 10, label: 'ตุลาคม' },
  { value: 11, label: 'พฤศจิกายน' },
  { value: 12, label: 'ธันวาคม' },
];

export const FilterPanel: React.FC = () => {
  const {
    filterOptions,
    loadFilterOptions,
    generateUniverSnapshot,
    isLoading,
    error,
    clearError,
  } = useReport();

  const [form] = Form.useForm();
  const [selectAllGroups, setSelectAllGroups] = useState<boolean>(true);

  useEffect(() => {
    // Load filter options on mount
    loadFilterOptions();
  }, []);

  useEffect(() => {
    // Set default values when filter options are loaded
    if (filterOptions) {
      const currentYear = new Date().getFullYear();
      const currentMonth = new Date().getMonth() + 1;

      form.setFieldsValue({
        year: filterOptions.available_years.includes(currentYear)
          ? currentYear
          : filterOptions.available_years[0],
        months: [currentMonth],
        business_groups: null, // null = all groups
      });
    }
  }, [filterOptions, form]);

  const handleGenerateReport = async (values: any) => {
    clearError();

    const filter: ReportFilter = {
      year: values.year,
      months: values.months,
      business_groups: selectAllGroups ? null : values.business_groups || null,
    };

    try {
      await generateUniverSnapshot(filter);
    } catch (err) {
      // Error is handled by context
    }
  };

  const handleSelectAllMonths = () => {
    form.setFieldsValue({
      months: MONTHS.map((m) => m.value),
    });
  };

  const handleSelectQuarter = (quarter: number) => {
    const quarterMonths = {
      1: [1, 2, 3],
      2: [4, 5, 6],
      3: [7, 8, 9],
      4: [10, 11, 12],
    };
    form.setFieldsValue({
      months: quarterMonths[quarter as keyof typeof quarterMonths],
    });
  };

  const handleToggleSelectAllGroups = (checked: boolean) => {
    setSelectAllGroups(checked);
    if (checked) {
      form.setFieldsValue({ business_groups: undefined });
    }
  };

  if (!filterOptions) {
    return (
      <Card loading={isLoading}>
        <Alert
          message="กำลังโหลดตัวเลือกการกรอง..."
          type="info"
          showIcon
        />
      </Card>
    );
  }

  return (
    <Card
      title={
        <Space>
          <FilterOutlined />
          ตัวกรองรายงาน
        </Space>
      }
      extra={
        <Button
          type="primary"
          icon={<FileSearchOutlined />}
          onClick={() => form.submit()}
          loading={isLoading}
        >
          สร้างรายงาน
        </Button>
      }
      size="small"
      styles={{ body: { paddingTop: 8, paddingBottom: 8 } }}
    >
      {error && (
        <Alert
          message="เกิดข้อผิดพลาด"
          description={error}
          type="error"
          closable
          onClose={clearError}
          showIcon
          style={{ marginBottom: 8 }}
        />
      )}

      <Form
        form={form}
        layout="inline"
        onFinish={handleGenerateReport}
        size="small"
        style={{ flexWrap: 'wrap', gap: '8px' }}
      >
        <Form.Item
          name="year"
          label="ปี"
          rules={[{ required: true, message: 'กรุณาเลือกปี' }]}
          style={{ marginBottom: 8 }}
        >
          <Select placeholder="เลือกปี" style={{ width: 140 }}>
            {filterOptions.available_years.map((year) => (
              <Option key={year} value={year}>
                {year + 543} ({year})
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="months"
          label="เดือน"
          rules={[
            { required: true, message: 'กรุณาเลือกอย่างน้อย 1 เดือน' },
          ]}
          style={{ marginBottom: 8, minWidth: 250 }}
        >
          <Select
            mode="multiple"
            placeholder="เลือกเดือน"
            maxTagCount={2}
            style={{ minWidth: 200 }}
          >
            {MONTHS.map((month) => (
              <Option key={month.value} value={month.value}>
                {month.label}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Space wrap size="small" style={{ marginBottom: 8 }}>
          <Button size="small" onClick={handleSelectAllMonths}>
            ทั้งปี
          </Button>
          <Button size="small" onClick={() => handleSelectQuarter(1)}>
            Q1
          </Button>
          <Button size="small" onClick={() => handleSelectQuarter(2)}>
            Q2
          </Button>
          <Button size="small" onClick={() => handleSelectQuarter(3)}>
            Q3
          </Button>
          <Button size="small" onClick={() => handleSelectQuarter(4)}>
            Q4
          </Button>
        </Space>

        <Form.Item style={{ marginBottom: 8 }}>
          <Checkbox
            checked={selectAllGroups}
            onChange={(e) => handleToggleSelectAllGroups(e.target.checked)}
          >
            ทุกกลุ่มธุรกิจ
          </Checkbox>
        </Form.Item>

        {!selectAllGroups && (
          <Form.Item
            name="business_groups"
            label="กลุ่มธุรกิจ"
            rules={[
              {
                required: !selectAllGroups,
                message: 'กรุณาเลือกกลุ่มธุรกิจอย่างน้อย 1 กลุ่ม',
              },
            ]}
            style={{ marginBottom: 8, minWidth: 250 }}
          >
            <Select
              mode="multiple"
              placeholder="เลือกกลุ่มธุรกิจ"
              maxTagCount={2}
              style={{ minWidth: 200 }}
            >
              {filterOptions.available_business_groups.map((group) => (
                <Option key={group} value={group}>
                  {group}
                </Option>
              ))}
            </Select>
          </Form.Item>
        )}
      </Form>
    </Card>
  );
};
