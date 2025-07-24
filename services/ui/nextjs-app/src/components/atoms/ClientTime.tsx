// Client-side time component to prevent hydration issues
import { useEffect, useState } from 'react';

interface ClientTimeProps {
  format?: 'time' | 'date' | 'datetime';
  fallback?: string;
}

export const ClientTime: React.FC<ClientTimeProps> = ({ 
  format = 'time', 
  fallback = '--:--:--' 
}) => {
  const [time, setTime] = useState<string>(fallback);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    
    const updateTime = () => {
      const now = new Date();
      switch (format) {
        case 'time':
          setTime(now.toLocaleTimeString());
          break;
        case 'date':
          setTime(now.toLocaleDateString());
          break;
        case 'datetime':
          setTime(now.toLocaleString());
          break;
        default:
          setTime(now.toLocaleTimeString());
      }
    };

    // Initial update
    updateTime();
    
    // Update every second for time display
    const interval = setInterval(updateTime, 1000);
    
    return () => clearInterval(interval);
  }, [format]);

  // Return fallback during SSR to prevent hydration mismatch
  if (!mounted) {
    return <>{fallback}</>;
  }

  return <>{time}</>;
};

export default ClientTime;
