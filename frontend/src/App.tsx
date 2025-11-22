/**
 * Main App Component
 */

import React from 'react';
import { Layout, Button, Space, Typography, Avatar } from 'antd';
import { LogoutOutlined, UserOutlined } from '@ant-design/icons';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ReportProvider } from './contexts/ReportContext';
import { Login } from './components/Login';
import { FilterPanel } from './components/FilterPanel';
import { ReportViewer } from './components/ReportViewer';

const { Header, Content } = Layout;
const { Title, Text } = Typography;

const AppContent: React.FC = () => {
  const { user, isAuthenticated, logout, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Space direction="vertical" align="center">
          <Title level={3}>กำลังโหลด...</Title>
        </Space>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <ReportProvider>
      <Layout style={{ minHeight: '100vh' }}>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Space>
            <Title level={4} style={{ margin: 0 }}>
              📊 ระบบรายงานผลดำเนินงาน
            </Title>
          </Space>

          <Space>
            <Avatar icon={<UserOutlined />} />
            <div>
              <Text strong>{user?.email}</Text>
              <br />
              <Text type="secondary" style={{ fontSize: 12 }}>
                {user?.domain}
              </Text>
            </div>
            <Button
              icon={<LogoutOutlined />}
              onClick={logout}
              type="text"
            >
              ออกจากระบบ
            </Button>
          </Space>
        </Header>

        <Content style={{ padding: '24px', background: '#f0f2f5' }}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <FilterPanel />
            <ReportViewer />
          </Space>
        </Content>
      </Layout>
    </ReportProvider>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};
