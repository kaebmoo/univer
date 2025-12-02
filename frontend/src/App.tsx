/**
 * Main App Component
 */

import React from 'react';
import { Layout, Button, Space, Typography, Avatar } from 'antd';
import { LogoutOutlined, UserOutlined } from '@ant-design/icons';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Login } from './components/Login';
import { ReportListViewer } from './components/ReportListViewer';

const { Header, Content } = Layout;
const { Title, Text } = Typography;

const AppContent: React.FC = () => {
  const { user, isAuthenticated, logout, isLoading } = useAuth();

  // Don't show loading screen during login flow
  // Let Login component handle its own loading state
  if (!isAuthenticated) {
    return <Login />;
  }

  // Only show loading screen for authenticated operations
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

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          background: '#fff',
          padding: '0 24px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: 'auto',
          minHeight: 64,
          lineHeight: 'normal',
        }}
      >
        <Space>
          <Title level={4} style={{ margin: 0 }}>
            📊 ระบบรายงานผลดำเนินงาน
          </Title>
        </Space>

        <Space align="center" size="middle">
          <Avatar icon={<UserOutlined />} />
          <div style={{ lineHeight: 1.4, minWidth: 150 }}>
            <div>
              <Text strong style={{ display: 'block' }}>{user?.email}</Text>
            </div>
            <div>
              <Text type="secondary" style={{ fontSize: 12, display: 'block' }}>
                {user?.domain}
              </Text>
            </div>
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
        <ReportListViewer />
      </Content>
    </Layout>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};
