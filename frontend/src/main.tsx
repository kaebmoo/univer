/**
 * Main Entry Point
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';

// Ant Design styles
import 'antd/dist/reset.css';

// Univer styles
import '@univerjs/design/lib/index.css';
import '@univerjs/ui/lib/index.css';
import '@univerjs/sheets-ui/lib/index.css';
import '@univerjs/sheets-formula/lib/index.css';
import '@univerjs/docs-ui/lib/index.css';

// Custom styles
import './style.css';

ReactDOM.createRoot(document.getElementById('app')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
