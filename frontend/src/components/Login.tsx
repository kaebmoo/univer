/**
 * Login Component with OTP Authentication
 */

import React, { useState } from 'react';
import { Alert, Button, Card, Form, Input, Space, Typography } from 'antd';
import { MailOutlined, SafetyOutlined, LoginOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';

const { Title, Text } = Typography;

export const Login: React.FC = () => {
  const { requestOTP, verifyOTP, isLoading, error, clearError } = useAuth();
  const [step, setStep] = useState<'email' | 'otp'>('email');
  const [email, setEmail] = useState<string>('');
  const [otpExpiry, setOtpExpiry] = useState<number>(300);

  const [emailForm] = Form.useForm();
  const [otpForm] = Form.useForm();

  // Debug: Watch step changes
  React.useEffect(() => {
    console.log('🔔 Step state changed to:', step);
  }, [step]);

  const handleRequestOTP = async (values: { email: string }) => {
    console.log('🔵 handleRequestOTP called with email:', values.email);
    clearError();
    setEmail(values.email);

    try {
      console.log('🔵 Calling requestOTP...');
      const response = await requestOTP({ email: values.email });
      console.log('🟢 Response received:', response);
      console.log('🟢 expires_in:', response.expires_in);

      setOtpExpiry(response.expires_in);
      console.log('🟢 About to set step to otp');
      setStep('otp');
      console.log('🟢 Step set to:', 'otp');

      // Start countdown timer
      const timer = setInterval(() => {
        setOtpExpiry((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (err) {
      console.error('🔴 Error in handleRequestOTP:', err);
      // Error is handled by context
    }
  };

  const handleVerifyOTP = async (values: { otp_code: string }) => {
    clearError();

    try {
      await verifyOTP({
        email,
        otp_code: values.otp_code,
      });
      // User will be redirected automatically after successful login
    } catch (err) {
      // Error is handled by context
    }
  };

  const handleBackToEmail = () => {
    setStep('email');
    setEmail('');
    otpForm.resetFields();
    clearError();
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  console.log('🔄 Login component rendering, current step:', step);

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '20px',
      }}
    >
      <Card
        style={{
          width: '100%',
          maxWidth: 450,
          boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
          borderRadius: 12,
        }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2} style={{ marginBottom: 8 }}>
              ระบบรายงานผลดำเนินงาน
            </Title>
            <Text type="secondary">Univer Report System</Text>
          </div>

          {error && (
            <Alert
              message="Error"
              description={error}
              type="error"
              closable
              onClose={clearError}
              showIcon
            />
          )}

          {step === 'email' ? (
            <Form
              form={emailForm}
              layout="vertical"
              onFinish={handleRequestOTP}
              size="large"
            >
              <Form.Item
                name="email"
                label="Email Address"
                rules={[
                  { required: true, message: 'กรุณากรอกอีเมล' },
                  { type: 'email', message: 'รูปแบบอีเมลไม่ถูกต้อง' },
                ]}
              >
                <Input
                  prefix={<MailOutlined />}
                  placeholder="your.email@company.com"
                  autoFocus
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<SafetyOutlined />}
                  loading={isLoading}
                  block
                  size="large"
                >
                  ขอรหัส OTP
                </Button>
              </Form.Item>

              <div style={{ textAlign: 'center' }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  เราจะส่งรหัส OTP ไปที่อีเมลของคุณ
                  <br />
                  รหัส OTP จะหมดอายุภายใน 5 นาที
                </Text>
              </div>
            </Form>
          ) : (
            <Form
              form={otpForm}
              layout="vertical"
              onFinish={handleVerifyOTP}
              size="large"
            >
              <div style={{ textAlign: 'center', marginBottom: 24 }}>
                <Text>รหัส OTP ถูกส่งไปที่:</Text>
                <br />
                <Text strong style={{ fontSize: 16 }}>
                  {email}
                </Text>
                <br />
                <br />
                <Text type={otpExpiry > 0 ? 'secondary' : 'danger'}>
                  {otpExpiry > 0
                    ? `หมดอายุใน ${formatTime(otpExpiry)}`
                    : 'รหัส OTP หมดอายุแล้ว'}
                </Text>
              </div>

              <Form.Item
                name="otp_code"
                label="รหัส OTP (6 หลัก)"
                rules={[
                  { required: true, message: 'กรุณากรอกรหัส OTP' },
                  {
                    len: 6,
                    message: 'รหัส OTP ต้องมี 6 หลัก',
                  },
                  {
                    pattern: /^\d+$/,
                    message: 'รหัส OTP ต้องเป็นตัวเลขเท่านั้น',
                  },
                ]}
              >
                <Input
                  placeholder="123456"
                  maxLength={6}
                  autoFocus
                  style={{ fontSize: 24, letterSpacing: 8, textAlign: 'center' }}
                />
              </Form.Item>

              <Form.Item>
                <Space direction="vertical" style={{ width: '100%' }} size="middle">
                  <Button
                    type="primary"
                    htmlType="submit"
                    icon={<LoginOutlined />}
                    loading={isLoading}
                    disabled={otpExpiry === 0}
                    block
                    size="large"
                  >
                    เข้าสู่ระบบ
                  </Button>

                  <Button onClick={handleBackToEmail} block>
                    ย้อนกลับ / ขอรหัส OTP ใหม่
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          )}
        </Space>
      </Card>
    </div>
  );
};
