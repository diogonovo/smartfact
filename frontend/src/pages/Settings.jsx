import React from 'react';
import { Sliders } from 'lucide-react';

const Settings = () => {
  return (
    <div className="container mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Configurações</h1>
        <p className="text-gray-600">Personalize o sistema de análise de máquinas industriais</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configurações do Sistema */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Sliders className="h-5 w-5 mr-2" />
              Configurações do Sistema
            </h2>
            
            <div className="space-y-6">
              {/* Configurações Gerais */}
              <div>
                <h3 className="text-md font-medium mb-3 text-gray-700">Configurações Gerais</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Intervalo de Atualização de Dados
                    </label>
                    <select className="w-full border border-gray-300 rounded-md px-3 py-2">
                      <option value="5">A cada 5 segundos</option>
                      <option value="30">A cada 30 segundos</option>
                      <option value="60" selected>A cada 1 minuto</option>
                      <option value="300">A cada 5 minutos</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tema da Interface
                    </label>
                    <div className="flex space-x-4">
                      <label className="inline-flex items-center">
                        <input type="radio" name="theme" value="light" className="form-radio" checked />
                        <span className="ml-2">Claro</span>
                      </label>
                      <label className="inline-flex items-center">
                        <input type="radio" name="theme" value="dark" className="form-radio" />
                        <span className="ml-2">Escuro</span>
                      </label>
                      <label className="inline-flex items-center">
                        <input type="radio" name="theme" value="system" className="form-radio" />
                        <span className="ml-2">Sistema</span>
                      </label>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Idioma
                    </label>
                    <select className="w-full border border-gray-300 rounded-md px-3 py-2">
                      <option value="pt-BR" selected>Português (Brasil)</option>
                      <option value="en-US">English (US)</option>
                      <option value="es">Español</option>
                    </select>
                  </div>
                </div>
              </div>
              
              {/* Configurações de Notificações */}
              <div>
                <h3 className="text-md font-medium mb-3 text-gray-700">Notificações</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Notificações de Anomalias</span>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" value="" className="sr-only peer" checked />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Notificações de Manutenção</span>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" value="" className="sr-only peer" checked />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Notificações por E-mail</span>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" value="" className="sr-only peer" />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Limiar de Alerta para Anomalias
                    </label>
                    <select className="w-full border border-gray-300 rounded-md px-3 py-2">
                      <option value="0.6">0.6 (Sensível)</option>
                      <option value="0.7" selected>0.7 (Padrão)</option>
                      <option value="0.8">0.8 (Rigoroso)</option>
                      <option value="0.9">0.9 (Muito rigoroso)</option>
                    </select>
                  </div>
                </div>
              </div>
              
              {/* Configurações de Modelos */}
              <div>
                <h3 className="text-md font-medium mb-3 text-gray-700">Modelos de Machine Learning</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Modelo de Detecção de Anomalias
                    </label>
                    <select className="w-full border border-gray-300 rounded-md px-3 py-2">
                      <option value="isolation_forest" selected>Isolation Forest</option>
                      <option value="lof">Local Outlier Factor</option>
                      <option value="ocsvm">One-Class SVM</option>
                      <option value="autoencoder">Autoencoder</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Modelo de Previsão de Falhas
                    </label>
                    <select className="w-full border border-gray-300 rounded-md px-3 py-2">
                      <option value="random_forest">Random Forest</option>
                      <option value="xgboost" selected>XGBoost</option>
                      <option value="lstm">LSTM</option>
                      <option value="ensemble">Ensemble</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Frequência de Retreinamento
                    </label>
                    <select className="w-full border border-gray-300 rounded-md px-3 py-2">
                      <option value="daily">Diariamente</option>
                      <option value="weekly" selected>Semanalmente</option>
                      <option value="monthly">Mensalmente</option>
                      <option value="quarterly">Trimestralmente</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-6 flex justify-end space-x-3">
              <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md">
                Restaurar Padrões
              </button>
              <button className="px-4 py-2 bg-primary text-white rounded-md">
                Salvar Configurações
              </button>
            </div>
          </div>
        </div>
        
        {/* Perfil e Integrações */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">Perfil do Usuário</h2>
            
            <div className="flex flex-col items-center mb-6">
              <div className="h-24 w-24 rounded-full bg-primary flex items-center justify-center text-white text-2xl font-bold mb-3">
                JD
              </div>
              <h3 className="text-lg font-medium">João da Silva</h3>
              <p className="text-sm text-gray-600">Administrador</p>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nome
                </label>
                <input 
                  type="text" 
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  value="João da Silva"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  E-mail
                </label>
                <input 
                  type="email" 
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  value="joao.silva@empresa.com.br"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cargo
                </label>
                <input 
                  type="text" 
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  value="Gerente de Manutenção"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Departamento
                </label>
                <input 
                  type="text" 
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  value="Produção"
                />
              </div>
              
              <button className="w-full px-4 py-2 bg-primary text-white rounded-md">
                Atualizar Perfil
              </button>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-semibold mb-4">Integrações</h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="h-10 w-10 rounded bg-blue-500 flex items-center justify-center text-white font-bold mr-3">
                    S
                  </div>
                  <div>
                    <p className="font-medium">SAP</p>
                    <p className="text-xs text-gray-600">Sistema ERP</p>
                  </div>
                </div>
                <div className="text-sm text-green-600 font-medium">Conectado</div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="h-10 w-10 rounded bg-orange-500 flex items-center justify-center text-white font-bold mr-3">
                    P
                  </div>
                  <div>
                    <p className="font-medium">Power BI</p>
                    <p className="text-xs text-gray-600">Visualização de Dados</p>
                  </div>
                </div>
                <div className="text-sm text-green-600 font-medium">Conectado</div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="h-10 w-10 rounded bg-gray-500 flex items-center justify-center text-white font-bold mr-3">
                    M
                  </div>
                  <div>
                    <p className="font-medium">MQTT</p>
                    <p className="text-xs text-gray-600">Protocolo IoT</p>
                  </div>
                </div>
                <div className="text-sm text-gray-600 font-medium">Desconectado</div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="h-10 w-10 rounded bg-purple-500 flex items-center justify-center text-white font-bold mr-3">
                    K
                  </div>
                  <div>
                    <p className="font-medium">Kafka</p>
                    <p className="text-xs text-gray-600">Streaming de Dados</p>
                  </div>
                </div>
                <div className="text-sm text-gray-600 font-medium">Desconectado</div>
              </div>
              
              <button className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-md">
                Gerenciar Integrações
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
