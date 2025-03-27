import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Activity, 
  AlertTriangle, 
  Wrench, 
  TrendingUp, 
  Settings,
  Menu,
  X
} from 'lucide-react';

const Sidebar = ({ open, setOpen }) => {
  const location = useLocation();
  
  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Monitoramento de Máquinas', href: '/machine-monitoring', icon: Activity },
    { name: 'Detecção de Anomalias', href: '/anomaly-detection', icon: AlertTriangle },
    { name: 'Manutenção Preditiva', href: '/predictive-maintenance', icon: Wrench },
    { name: 'Otimização de Desempenho', href: '/performance-optimization', icon: TrendingUp },
    { name: 'Configurações', href: '/settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile sidebar overlay */}
      <div
        className={`fixed inset-0 z-20 bg-black bg-opacity-50 transition-opacity md:hidden ${
          open ? 'opacity-100 ease-out duration-300' : 'opacity-0 ease-in duration-200 pointer-events-none'
        }`}
        onClick={() => setOpen(false)}
      />

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-30 w-64 bg-base-100 shadow-lg transform transition-transform md:translate-x-0 md:static md:h-screen ${
          open ? 'translate-x-0 ease-out duration-300' : '-translate-x-full ease-in duration-200'
        }`}
      >
        <div className="flex items-center justify-between h-16 px-4 border-b border-base-300">
          <div className="flex items-center">
            <span className="text-xl font-semibold text-primary">Industrial Analytics</span>
          </div>
          <button
            className="md:hidden rounded-md p-2 text-gray-500 hover:text-gray-600 hover:bg-gray-100"
            onClick={() => setOpen(false)}
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <nav className="mt-5 px-2 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            const Icon = item.icon;
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`group flex items-center px-2 py-2 text-base font-medium rounded-md ${
                  isActive
                    ? 'bg-primary text-white'
                    : 'text-gray-600 hover:bg-primary hover:bg-opacity-10 hover:text-primary'
                }`}
                onClick={() => setOpen(false)}
              >
                <Icon
                  className={`mr-3 h-6 w-6 ${
                    isActive ? 'text-white' : 'text-gray-400 group-hover:text-primary'
                  }`}
                />
                {item.name}
              </Link>
            );
          })}
        </nav>
        
        <div className="absolute bottom-0 w-full p-4 border-t border-base-300">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-white font-bold">
                IA
              </div>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium">Indústria 4.0</p>
              <p className="text-xs text-gray-500">Análise Inteligente</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
