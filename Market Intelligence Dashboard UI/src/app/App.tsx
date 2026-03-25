import { RouterProvider } from 'react-router';
import { router } from './routes';
import { useEffect } from 'react';

export default function App() {
  useEffect(() => {
    // Enable dark mode globally
    document.documentElement.classList.add('dark');
  }, []);

  return <RouterProvider router={router} />;
}