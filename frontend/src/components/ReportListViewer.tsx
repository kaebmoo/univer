import React, { useState, useEffect, useRef } from 'react';
import { List, Typography, Spin, Alert, Button, Result, Space, message } from 'antd';
import { ArrowLeftOutlined, ReloadOutlined } from '@ant-design/icons';
import { apiClient } from '../services/api';
import type { UniverSnapshot } from '../types/index.ts';

// Univer Core Imports
import { Univer, UniverInstanceType, LocaleType } from '@univerjs/core';
import { defaultTheme } from '@univerjs/design';
import { UniverRenderEnginePlugin } from '@univerjs/engine-render';
import { UniverFormulaEnginePlugin } from '@univerjs/engine-formula';
import { UniverUIPlugin } from '@univerjs/ui';
import { UniverDocsPlugin } from '@univerjs/docs';
import { UniverDocsUIPlugin } from '@univerjs/docs-ui';
import { UniverSheetsPlugin } from '@univerjs/sheets';
import { UniverSheetsUIPlugin } from '@univerjs/sheets-ui';
import { UniverSheetsFormulaPlugin } from '@univerjs/sheets-formula';
import { UniverSheetsNumfmtPlugin } from '@univerjs/sheets-numfmt';
import { UniverSheetsNumfmtUIPlugin } from '@univerjs/sheets-numfmt-ui';

const { Title } = Typography;

// This is the actual viewer component
const UniverSheetViewer: React.FC<{ file: string; onBack: () => void }> = ({ file, onBack }) => {
    const [snapshot, setSnapshot] = useState<UniverSnapshot | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [containerKey, setContainerKey] = useState(0);

    const univerRef = useRef<Univer | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const fetchSnapshot = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await apiClient.getReportSnapshot(file);
                setSnapshot(response);
            } catch (err: any) {
                setError('Failed to load report data. It may be processing or an error occurred.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchSnapshot();
    }, [file]);

    // When snapshot changes, dispose previous instance and force container re-creation
    useEffect(() => {
        if (!snapshot) return;

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
    }, [snapshot]);

    useEffect(() => {
        if (!containerRef.current || !snapshot) return;

        // Use requestAnimationFrame to ensure DOM is ready after re-render
        const frameId = requestAnimationFrame(() => {
            if (!containerRef.current || !snapshot) return;

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
                
                // Register Number Format plugins (IMPORTANT!)
                univer.registerPlugin(UniverSheetsNumfmtPlugin);
                univer.registerPlugin(UniverSheetsNumfmtUIPlugin);

                // Register Formula plugins
                univer.registerPlugin(UniverFormulaEnginePlugin);
                univer.registerPlugin(UniverSheetsFormulaPlugin);

                // Create workbook from snapshot
                univer.createUnit(UniverInstanceType.UNIVER_SHEET, snapshot);

                // Store instance reference
                univerRef.current = univer;
            } catch (error) {
                console.error('Error creating Univer instance:', error);
                setError('Failed to initialize spreadsheet viewer.');
            }
        });

        // Cleanup on component unmount
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
    }, [containerKey, snapshot]); // Re-run when snapshot data changes
    
    return (
        <div style={{ border: '1px solid #f0f0f0', borderRadius: 8, background: '#fff' }}>
            <div style={{
                padding: '16px 24px',
                borderBottom: '1px solid #f0f0f0',
                display: 'flex',
                alignItems: 'center'
            }}>
                <Button
                    icon={<ArrowLeftOutlined />}
                    onClick={onBack}
                    type="text"
                    style={{ marginRight: 16 }}
                />
                <Space direction="vertical" size={0}>
                    <Title level={4} style={{ margin: 0 }}>Report Viewer</Title>
                    <Typography.Text type="secondary">{file}</Typography.Text>
                </Space>
            </div>
             <div style={{ padding: '16px' }}>
                {loading && (
                    <div style={{textAlign: 'center', padding: '100px'}}>
                        <Spin tip="Loading sheet data..." size="large" />
                    </div>
                )}
                {error && <Result status="error" title="Could not load report" subTitle={error} />}
                {!loading && !error && snapshot && (
                    <div
                        key={`univer-container-${containerKey}`}
                        ref={containerRef}
                        style={{
                            width: '100%',
                            height: '80vh',
                            minHeight: 600
                        }}
                    />
                )}
            </div>
        </div>
    );
};


export const ReportListViewer: React.FC = () => {
    const [view, setView] = useState<'list' | 'viewer'>('list');
    const [selectedFile, setSelectedFile] = useState<string | null>(null);

    const [reports, setReports] = useState<string[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [clearingCache, setClearingCache] = useState<boolean>(false);

    useEffect(() => {
        if (view === 'list') {
            const fetchReports = async () => {
                setLoading(true);
                setError(null);
                try {
                    const response = await apiClient.getReportList();
                    setReports(response);
                } catch (err: any) {
                    setError('Failed to load report list. Please try again later.');
                    console.error(err);
                } finally {
                    setLoading(false);
                }
            };
            fetchReports();
        }
    }, [view]);

    const handleSelectReport = (filename: string) => {
        setSelectedFile(filename);
        setView('viewer');
    };

    const handleBackToList = () => {
        setSelectedFile(null);
        setView('list');
    };

    const handleClearCache = async () => {
        setClearingCache(true);
        try {
            const result = await apiClient.clearReportsCache();
            message.success(`Cache cleared: ${result.cleared_count} items removed`);
        } catch (err) {
            message.error('Failed to clear cache');
            console.error(err);
        } finally {
            setClearingCache(false);
        }
    };



    if (view === 'viewer' && selectedFile) {
        return <UniverSheetViewer file={selectedFile} onBack={handleBackToList} />;
    }

    return (
        <div style={{ background: '#fff', padding: 24, borderRadius: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <Title level={2} style={{ margin: 0 }}>Pre-generated Excel Reports</Title>
                <Button
                    icon={<ReloadOutlined />}
                    onClick={handleClearCache}
                    loading={clearingCache}
                    type="default"
                >
                    Clear Cache
                </Button>
            </div>
            {loading && <div style={{textAlign: 'center', padding: '50px'}}><Spin tip="Loading reports..." size="large" /></div>}
            {error && <Alert message="Error" description={error} type="error" showIcon />}
            {!loading && !error && (
                <List
                    bordered
                    dataSource={reports}
                    renderItem={(item) => (
                        <List.Item
                            actions={[
                                <Button type="primary" onClick={() => handleSelectReport(item)}>
                                    View
                                </Button>
                            ]}
                        >
                            <Typography.Text>{item}</Typography.Text>
                        </List.Item>
                    )}
                />
            )}
        </div>
    );
};
