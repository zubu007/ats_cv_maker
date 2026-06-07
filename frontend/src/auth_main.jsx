import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import App from './App';
import ProtectedRoute from './components/ProtectedRoute';
import './index.css';
import AuthPage from './pages/AuthPage';
import CoverLetter from './pages/CoverLetter';
import MyDataPage from './pages/MyDataPage';

const router = createBrowserRouter([
  {
    path: '/auth',
    element: <AuthPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <App />
      </ProtectedRoute>
    ),
  },
  {
    path: '/cover-letter',
    element: (
      <ProtectedRoute>
        <CoverLetter />
      </ProtectedRoute>
    ),
  },
  {
    path: '/my-data',
    element: (
      <ProtectedRoute>
        <MyDataPage />
      </ProtectedRoute>
    ),
  },
]);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
