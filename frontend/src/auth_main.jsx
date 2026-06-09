import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

import App from './App';
import ProtectedRoute from './components/ProtectedRoute';
import './index.css';
import AuthPage from './pages/AuthPage';
import MyDataPage from './pages/MyDataPage';
import MyJobsPage from './pages/MyJobsPage';

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
    path: '/my-data',
    element: (
      <ProtectedRoute>
        <MyDataPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/my-jobs',
    element: (
      <ProtectedRoute>
        <MyJobsPage />
      </ProtectedRoute>
    ),
  },
]);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
