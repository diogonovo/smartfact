import React from 'react';
import { Menu, Bell, User } from 'lucide-react';

const Navbar = ({ sidebarOpen, setSidebarOpen }) => {
  return (
    <header className="bg-base-100 shadow-sm z-10">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <button
              type="button"
              className="md:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-500 hover:text-gray-600 hover:bg-gray-100 focus:outline-none"
              onClick={() => setSidebarOpen(true)}
            >
              <span className="sr-only">Abrir menu lateral</span>
              <Menu className="h-6 w-6" />
            </button>
            <div className="hidden md:block">
              <h1 className="text-xl font-semibold text-gray-800">Análise de Máquinas Industriais</h1>
            </div>
          </div>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <button className="p-1 rounded-full text-gray-500 hover:text-gray-600 hover:bg-gray-100 focus:outline-none">
                <span className="sr-only">Ver notificações</span>
                <Bell className="h-6 w-6" />
              </button>
            </div>
            <div className="ml-3 relative">
              <div>
                <button className="flex items-center max-w-xs rounded-full text-gray-500 hover:text-gray-600 hover:bg-gray-100 focus:outline-none p-1">
                  <span className="sr-only">Abrir menu de usuário</span>
                  <User className="h-6 w-6" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
