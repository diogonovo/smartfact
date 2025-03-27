import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, AreaChart, Area, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ScatterChart, Scatter, ZAxis
} from 'recharts';
import { Activity, AlertTriangle, Thermometer, Zap } from 'lucide-react';

// Dados simulados para o monitoramento de máquinas
const generateMockData = () => {
  // Dados de temperatura ao longo do tempo
  const temperatureData = Array.from({ length: 24 }, (_, i) => {
    const hour = i;
    return {
      hora: `${hour}:00`,
      torno: 65 + Math.random() * 15,
      fresadora: 60 + Math.random() * 10,
      injetora: 70 + Math.random() * 20,
      compressor: 55 + Math.random() * 8
    };
  });

  // Dados de vibração ao longo do tempo
  const vibrationData = Array.from({ length: 24 }, (_, i) => {
    const hour = i;
    return {
      hora: `${hour}:00`,
      torno: 0.5 + Math.random() * 0.8,
      fresadora: 0.3 + Math.random() * 0.5,
      injetora: 0.7 + Math.random() * 1.2,
      compressor: 0.8 + Math.random() * 1.5
    };
  });

  // Dados de consumo de energia ao longo do tempo
  const energyData = Array.from({ length: 24 }, (_, i) => {
    const hour = i;
    return {
      hora: `${hour}:00`,
      torno: 20 + Math.random() * 10,
      fresadora: 15 + Math.random() * 8,
      injetora: 30 + Math.random() * 15,
      compressor: 25 + Math.random() * 12
    };
  });

  // Dados de correlação entre temperatura e vibração
  const correlationData = Array.from({ length: 50 }, () => {
    const temp = 50 + Math.random() * 30;
    const baseVibration = 0.2 + (temp - 50) * 0.03;
    return {
      temperatura: temp,
      vibracao: baseVibration + Math.random() * 0.5,
      consumo: 10 + temp * 0.3 + Math.random() * 10
    };
  });

  // Lista de máquinas
  const machines = [
    { id: 1, name: 'Torno CNC #1', type: 'torno_cnc', status: 'operational', lastMaintenance: '15/03/2025', nextMaintenance: '15/06/2025', efficiency: 92 },
    { id: 2, name: 'Fresadora #2', type: 'fresadora', status: 'maintenance', lastMaintenance: '20/03/2025', nextMaintenance: '20/06/2025', efficiency: 85 },
    { id: 3, name: 'Injetora #1', type: 'injetora_plastico', status: 'operational', lastMaintenance: '10/02/2025', nextMaintenance: '10/05/2025', efficiency: 88 },
    { id: 4, name: 'Robô Industrial #3', type: 'robo_industrial', status: 'operational', lastMaintenance: '05/03/2025', nextMaintenance: '05/06/2025', efficiency: 95 },
    { id: 5, name: 'Compressor #2', type: 'compressor', status: 'warning', lastMaintenance: '25/01/2025', nextMaintenance: '25/04/2025', efficiency: 78 },
    { id: 6, name: 'Torno CNC #2', type: 'torno_cnc', status: 'operational', lastMaintenance: '18/03/2025', nextMaintenance: '18/06/2025', efficiency: 90 },
    { id: 7, name: 'Fresadora #1', type: 'fresadora', status: 'error', lastMaintenance: '12/02/2025', nextMaintenance: '12/05/2025', efficiency: 0 },
    { id: 8, name: 'Injetora #3', type: 'injetora_plastico', status: 'operational', lastMaintenance: '22/03/2025', nextMaintenance: '22/06/2025', efficiency: 91 }
  ];

  return {
    temperatureData,
    vibrationData,
    energyData,
    correlationData,
    machines
  };
};

const MachineStatusBadge = ({ status }) => {
  let color = '';
  let text = '';

  switch (status) {
    case 'operational':
      color = 'bg-success';
      text = 'Operacional';
      break;
    case 'maintenance':
      color = 'bg-warning';
      text = 'Em Manutenção';
      break;
    case 'warning':
      color = 'bg-warning';
      text = 'Atenção';
      break;
    case 'error':
      color = 'bg-error';
      text = 'Falha';
      break;
    default:
      color = 'bg-neutral';
      text = 'Desconhecido';
  }

  return (
    <span className={`px-2 py-1 rounded-full text-xs text-white ${color}`}>
      {text}
    </span>
  );
};

const MachineMonitoring = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedMachine, setSelectedMachine] = useState(null);
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    // Simulando uma chamada de API
    const fetchData = async () => {
      setLoading(true);
      try {
        // Em um cenário real, isso seria uma chamada à API
        const mockData = generateMockData();
        setData(mockData);
        // Selecionar a primeira máquina por padrão
        if (mockData.machines.length > 0) {
          setSelectedMachine(mockData.machines[0]);
        }
      } catch (error) {
        console.error('Erro ao buscar dados:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleMachineSelect = (machine) => {
    setSelectedMachine(machine);
  };

  const handleTimeRangeChange = (range) => {
    setTimeRange(range);
    // Em um cenário real, isso recarregaria os dados para o intervalo de tempo selecionado
  };

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Monitoramento de Máquinas</h1>
        <p className="text-gray-600">Acompanhe em tempo real os parâmetros operacionais das máquinas</p>
      </div>

      {/* Filtros e seleção de intervalo de tempo */}
      <div className="flex flex-col md:flex-row justify-between mb-6">
        <div className="mb-4 md:mb-0">
          <label className="block text-sm font-medium text-gray-700 mb-1">Intervalo de Tempo</label>
          <div className="flex space-x-2">
            <button 
              className={`px-3 py-1 rounded-md text-sm ${timeRange === '1h' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'}`}
              onClick={() => handleTimeRangeChange('1h')}
            >
              1h
            </button>
            <button 
              className={`px-3 py-1 rounded-md text-sm ${timeRange === '6h' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'}`}
              onClick={() => handleTimeRangeChange('6h')}
            >
              6h
            </button>
            <button 
              className={`px-3 py-1 rounded-md text-sm ${timeRange === '24h' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'}`}
              onClick={() => handleTimeRangeChange('24h')}
            >
              24h
            </button>
            <button 
              className={`px-3 py-1 rounded-md text-sm ${timeRange === '7d' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'}`}
              onClick={() => handleTimeRangeChange('7d')}
            >
              7d
            </button>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Atualização</label>
          <select className="border border-gray-300 rounded-md px-3 py-1 text-sm">
            <option value="5">A cada 5 segundos</option>
            <option value="30">A cada 30 segundos</option>
            <option value="60">A cada 1 minuto</option>
            <option value="300">A cada 5 minutos</option>
          </select>
        </div>
      </div>

      {/* Layout principal: lista de máquinas à esquerda, detalhes à direita */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Lista de máquinas */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-lg font-semibold mb-4">Máquinas</h2>
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {data.machines.map((machine) => (
                <div 
                  key={machine.id}
                  className={`p-3 rounded-md cursor-pointer transition-colors ${
                    selectedMachine && selectedMachine.id === machine.id 
                      ? 'bg-primary bg-opacity-10 border-l-4 border-primary' 
                      : 'hover:bg-gray-100'
                  }`}
                  onClick={() => handleMachineSelect(machine)}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{machine.name}</span>
                    <MachineStatusBadge status={machine.status} />
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    Tipo: {machine.type.replace('_', ' ')}
                  </div>
                  <div className="text-sm text-gray-500">
                    Eficiência: {machine.efficiency}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Detalhes da máquina selecionada */}
        <div className="lg:col-span-3">
          {selectedMachine ? (
            <div className="space-y-6">
              {/* Cabeçalho com informações da máquina */}
              <div className="bg-white rounded-lg shadow-md p-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h2 className="text-xl font-semibold">{selectedMachine.name}</h2>
                    <p className="text-gray-600">Tipo: {selectedMachine.type.replace('_', ' ')}</p>
                  </div>
                  <MachineStatusBadge status={selectedMachine.status} />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  <div className="border-r border-gray-200 pr-4">
                    <p className="text-sm text-gray-500">Última Manutenção</p>
                    <p className="font-medium">{selectedMachine.lastMaintenance}</p>
                  </div>
                  <div className="border-r border-gray-200 pr-4">
                    <p className="text-sm text-gray-500">Próxima Manutenção</p>
                    <p className="font-medium">{selectedMachine.nextMaintenance}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Eficiência</p>
                    <p className="font-medium">{selectedMachine.efficiency}%</p>
                  </div>
                </div>
              </div>

              {/* Cards de parâmetros atuais */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-lg shadow-md p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-500 text-sm">Temperatura</p>
                      <p className="text-2xl font-bold mt-1">72.5 °C</p>
                      <p className="text-xs text-warning mt-1">
                        +5.2 °C nas últimas 2 horas
                      </p>
                    </div>
                    <div className="p-3 rounded-full bg-error bg-opacity-10">
                      <Thermometer className="h-6 w-6 text-error" />
                    </div>
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-md p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-500 text-sm">Vibração</p>
                      <p className="text-2xl font-bold mt-1">0.82 mm/s</p>
                      <p className="text-xs text-success mt-1">
                        -0.15 mm/s nas últimas 2 horas
                      </p>
                    </div>
                    <div className="p-3 rounded-full bg-warning bg-opacity-10">
                      <Activity className="h-6 w-6 text-warning" />
                    </div>
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-md p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-500 text-sm">Consumo de Energia</p>
                      <p className="text-2xl font-bold mt-1">24.8 kW</p>
                      <p className="text-xs text-error mt-1">
                        +2.3 kW nas últimas 2 horas
                      </p>
                    </div>
                    <div className="p-3 rounded-full bg-primary bg-opacity-10">
                      <Zap className="h-6 w-6 text-primary" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Gráficos */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Gráfico de temperatura */}
                <div className="bg-white rounded-lg shadow-md p-4">
                  <h3 className="text-lg font-semibold mb-4">Temperatura</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={data.temperatureData}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="hora" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey={selectedMachine.type.split('_')[0]} 
                          stroke="#f87272" 
                          activeDot={{ r: 8 }} 
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Gráfico de vibração */}
                <div className="bg-white rounded-lg shadow-md p-4">
                  <h3 className="text-lg font-semibold mb-4">Vibração</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={data.vibrationData}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="hora" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey={selectedMachine.type.split('_')[0]} 
                          stroke="#fbbd23" 
                          activeDot={{ r: 8 }} 
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Gráfico de consumo de energia */}
                <div className="bg-white rounded-lg shadow-md p-4">
                  <h3 className="text-lg font-semibold mb-4">Consumo de Energia</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart
                        data={data.energyData}
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="hora" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Area 
                          type="monotone" 
                          dataKey={selectedMachine.type.split('_')[0]} 
                          stroke="#0ea5e9" 
                          fill="#0ea5e9" 
                          fillOpacity={0.3} 
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Gráfico de correlação */}
                <div className="bg-white rounded-lg shadow-md p-4">
                  <h3 className="text-lg font-semibold mb-4">Correlação Temperatura vs. Vibração</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <ScatterChart
                        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          type="number" 
                          dataKey="temperatura" 
                          name="Temperatura" 
                          unit="°C" 
                        />
                        <YAxis 
                          type="number" 
                          dataKey="vibracao" 
                          name="Vibração" 
                          unit="mm/s" 
                        />
                        <ZAxis 
                          type="number" 
                          dataKey="consumo" 
                          range={[50, 400]} 
                          name="Consumo" 
                          unit="kW" 
                        />
                        <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                        <Legend />
                        <Scatter 
                          name="Parâmetros" 
                          data={data.correlationData} 
                          fill="#7c3aed" 
                        />
                      </ScatterChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Alertas para esta máquina */}
              <div className="bg-white rounded-lg shadow-md p-4">
                <h3 className="text-lg font-semibold mb-4">Alertas Recentes</h3>
                {selectedMachine.status === 'operational' ? (
                  <div className="text-center py-4">
                    <p className="text-gray-500">Nenhum alerta recente para esta máquina.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {selectedMachine.status === 'warning' && (
                      <div className="flex items-start p-3 bg-warning bg-opacity-10 rounded-md">
                        <AlertTriangle className="h-5 w-5 text-warning mr-2 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="font-medium">Temperatura acima do normal</p>
                          <p className="text-sm text-gray-600">A temperatura está 15% acima do valor normal de operação. Recomenda-se verificar o sistema de refrigeração.</p>
                          <p className="text-xs text-gray-500 mt-1">Detectado há 2 horas</p>
                        </div>
                      </div>
                    )}
                    {selectedMachine.status === 'maintenance' && (
                      <div className="flex items-start p-3 bg-warning bg-opacity-10 rounded-md">
                        <Wrench className="h-5 w-5 text-warning mr-2 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="font-medium">Manutenção preventiva em andamento</p>
                          <p className="text-sm text-gray-600">Manutenção programada sendo realizada. Previsão de conclusão: 2 horas.</p>
                          <p className="text-xs text-gray-500 mt-1">Iniciada há 1 hora</p>
                        </div>
                      </div>
                    )}
                    {selectedMachine.status === 'error' && (
                      <div className="flex items-start p-3 bg-error bg-opacity-10 rounded-md">
                        <AlertTriangle className="h-5 w-5 text-error mr-2 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="font-medium">Falha crítica detectada</p>
                          <p className="text-sm text-gray-600">Motor principal apresentou falha. Manutenção corretiva necessária com urgência.</p>
                          <p className="text-xs text-gray-500 mt-1">Detectado há 30 minutos</p>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <p className="text-gray-500">Selecione uma máquina para visualizar seus detalhes.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MachineMonitoring;
