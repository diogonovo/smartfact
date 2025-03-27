import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import { Wrench, Calendar, Clock, AlertTriangle, Download } from 'lucide-react';

// Dados simulados para manutenção preditiva
const generateMockData = () => {
  // Dados de previsão de falhas para os próximos dias
  const failurePredictions = Array.from({ length: 30 }, (_, i) => {
    const day = i + 1;
    const date = new Date();
    date.setDate(date.getDate() + i);
    
    return {
      dia: `${date.getDate()}/${date.getMonth() + 1}`,
      probabilidade: Math.min(0.05 + (i * 0.015) + (Math.random() * 0.05), 0.95)
    };
  });

  // Dados de vida útil restante
  const remainingUsefulLife = [
    { name: 'Torno CNC #1', rul: 1250, status: 'healthy' },
    { name: 'Fresadora #2', rul: 820, status: 'warning' },
    { name: 'Injetora #1', rul: 1500, status: 'healthy' },
    { name: 'Robô Industrial #3', rul: 950, status: 'healthy' },
    { name: 'Compressor #2', rul: 350, status: 'critical' },
    { name: 'Torno CNC #2', rul: 1100, status: 'healthy' },
    { name: 'Fresadora #1', rul: 480, status: 'warning' },
    { name: 'Injetora #3', rul: 1300, status: 'healthy' }
  ];

  // Dados de componentes com maior risco de falha
  const componentFailureRisk = [
    { name: 'Motor', risco: 75 },
    { name: 'Rolamento', risco: 62 },
    { name: 'Bomba Hidráulica', risco: 48 },
    { name: 'Sistema Elétrico', risco: 35 },
    { name: 'Válvula', risco: 28 }
  ];

  // Dados de distribuição de tipos de manutenção
  const maintenanceTypeDistribution = [
    { name: 'Preventiva', value: 45, color: '#36d399' },
    { name: 'Preditiva', value: 30, color: '#3abff8' },
    { name: 'Corretiva', value: 15, color: '#f87272' },
    { name: 'Rotineira', value: 10, color: '#fbbd23' }
  ];

  // Dados de custo de manutenção ao longo do tempo
  const maintenanceCostTrend = Array.from({ length: 12 }, (_, i) => {
    const month = i + 1;
    return {
      mes: `${month < 10 ? '0' : ''}${month}/25`,
      preventiva: 15000 + Math.random() * 5000,
      corretiva: 25000 + Math.random() * 10000 - (i * 500)
    };
  });

  // Cronograma de manutenção
  const maintenanceSchedule = [
    { 
      id: 1, 
      machine: 'Torno CNC #1', 
      type: 'Preventiva', 
      date: '2025-04-15', 
      estimatedDuration: 4, 
      priority: 'medium',
      components: ['Motor', 'Rolamentos', 'Sistema de Refrigeração']
    },
    { 
      id: 2, 
      machine: 'Fresadora #2', 
      type: 'Preditiva', 
      date: '2025-04-05', 
      estimatedDuration: 6, 
      priority: 'high',
      components: ['Bomba Hidráulica', 'Válvulas de Controle']
    },
    { 
      id: 3, 
      machine: 'Compressor #2', 
      type: 'Corretiva', 
      date: '2025-03-30', 
      estimatedDuration: 8, 
      priority: 'critical',
      components: ['Motor', 'Sistema de Pressão', 'Filtros']
    },
    { 
      id: 4, 
      machine: 'Injetora #1', 
      type: 'Preventiva', 
      date: '2025-04-20', 
      estimatedDuration: 3, 
      priority: 'low',
      components: ['Sistema Elétrico', 'Sensores']
    },
    { 
      id: 5, 
      machine: 'Fresadora #1', 
      type: 'Preditiva', 
      date: '2025-04-10', 
      estimatedDuration: 5, 
      priority: 'high',
      components: ['Rolamentos', 'Eixos', 'Sistema de Lubrificação']
    }
  ];

  return {
    failurePredictions,
    remainingUsefulLife,
    componentFailureRisk,
    maintenanceTypeDistribution,
    maintenanceCostTrend,
    maintenanceSchedule
  };
};

const PriorityBadge = ({ priority }) => {
  let color = '';
  let text = '';

  switch (priority) {
    case 'critical':
      color = 'bg-error';
      text = 'Crítica';
      break;
    case 'high':
      color = 'bg-warning';
      text = 'Alta';
      break;
    case 'medium':
      color = 'bg-info';
      text = 'Média';
      break;
    case 'low':
      color = 'bg-success';
      text = 'Baixa';
      break;
    default:
      color = 'bg-neutral';
      text = 'Indefinida';
  }

  return (
    <span className={`px-2 py-1 rounded-full text-xs text-white ${color}`}>
      {text}
    </span>
  );
};

const MaintenanceTypeBadge = ({ type }) => {
  let color = '';

  switch (type) {
    case 'Preventiva':
      color = 'bg-success';
      break;
    case 'Preditiva':
      color = 'bg-info';
      break;
    case 'Corretiva':
      color = 'bg-error';
      break;
    case 'Rotineira':
      color = 'bg-warning';
      break;
    default:
      color = 'bg-neutral';
  }

  return (
    <span className={`px-2 py-1 rounded-full text-xs text-white ${color}`}>
      {type}
    </span>
  );
};

const PredictiveMaintenance = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');
  const [filterPriority, setFilterPriority] = useState('all');
  const [selectedMachine, setSelectedMachine] = useState(null);

  useEffect(() => {
    // Simulando uma chamada de API
    const fetchData = async () => {
      setLoading(true);
      try {
        // Em um cenário real, isso seria uma chamada à API
        const mockData = generateMockData();
        setData(mockData);
      } catch (error) {
        console.error('Erro ao buscar dados:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleTimeRangeChange = (range) => {
    setTimeRange(range);
    // Em um cenário real, isso recarregaria os dados para o intervalo de tempo selecionado
  };

  const handleFilterChange = (priority) => {
    setFilterPriority(priority);
  };

  const handleMachineSelect = (machine) => {
    setSelectedMachine(machine);
  };

  const filteredSchedule = data?.maintenanceSchedule.filter(item => {
    if (filterPriority !== 'all' && item.priority !== filterPriority) {
      return false;
    }
    return true;
  });

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
        <h1 className="text-2xl font-bold text-gray-800">Manutenção Preditiva</h1>
        <p className="text-gray-600">Planeje manutenções com base em previsões de falhas e vida útil restante</p>
      </div>

      {/* Filtros e seleção de intervalo de tempo */}
      <div className="flex flex-col md:flex-row justify-between mb-6">
        <div className="mb-4 md:mb-0">
          <label className="block text-sm font-medium text-gray-700 mb-1">Horizonte de Previsão</label>
          <div className="flex space-x-2">
            <button 
              className={`px-3 py-1 rounded-md text-sm ${timeRange === '7d' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'}`}
              onClick={() => handleTimeRangeChange('7d')}
            >
              7d
            </button>
            <button 
              className={`px-3 py-1 rounded-md text-sm ${timeRange === '14d' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'}`}
              onClick={() => handleTimeRangeChange('14d')}
            >
              14d
            </button>
            <button 
              className={`px-3 py-1 rounded-md text-sm ${timeRange === '30d' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'}`}
              onClick={() => handleTimeRangeChange('30d')}
            >
              30d
            </button>
            <button 
              className={`px-3 py-1 rounded-md text-sm ${timeRange === '90d' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'}`}
              onClick={() => handleTimeRangeChange('90d')}
            >
              90d
            </button>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Modelo de Previsão</label>
          <select className="border border-gray-300 rounded-md px-3 py-1 text-sm">
            <option value="ensemble">Ensemble (Padrão)</option>
            <option value="random_forest">Random Forest</option>
            <option value="lstm">LSTM</option>
            <option value="xgboost">XGBoost</option>
          </select>
        </div>
      </div>

      {/* Cards de estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Manutenções Programadas</p>
              <p className="text-2xl font-bold mt-1">12</p>
              <p className="text-xs text-success mt-1">
                +3 em relação ao mês anterior
              </p>
            </div>
            <div className="p-3 rounded-full bg-primary bg-opacity-10">
              <Calendar className="h-6 w-6 text-primary" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Tempo Médio Entre Falhas</p>
              <p className="text-2xl font-bold mt-1">1.250h</p>
              <p className="text-xs text-success mt-1">
                +5% em relação ao mês anterior
              </p>
            </div>
            <div className="p-3 rounded-full bg-success bg-opacity-10">
              <Clock className="h-6 w-6 text-success" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Custo de Manutenção</p>
              <p className="text-2xl font-bold mt-1">R$ 45.320</p>
              <p className="text-xs text-error mt-1">
                -12% em relação ao mês anterior
              </p>
            </div>
            <div className="p-3 rounded-full bg-error bg-opacity-10">
              <Wrench className="h-6 w-6 text-error" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Máquinas em Risco</p>
              <p className="text-2xl font-bold mt-1">3</p>
              <p className="text-xs text-warning mt-1">
                +1 em relação ao mês anterior
              </p>
            </div>
            <div className="p-3 rounded-full bg-warning bg-opacity-10">
              <AlertTriangle className="h-6 w-6 text-warning" />
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Gráfico de previsão de falhas */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Previsão de Falhas (Próximos 30 dias)</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={data.failurePredictions}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="dia" />
                <YAxis domain={[0, 1]} tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                <Tooltip formatter={(value) => `${(value * 100).toFixed(1)}%`} />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="probabilidade" 
                  name="Probabilidade de Falha" 
                  stroke="#f87272" 
                  activeDot={{ r: 8 }} 
                />
                {/* Linha de referência para o limiar de alerta */}
                <ReferenceLine y={0.7} stroke="red" strokeDasharray="3 3" label="Limiar de Alerta" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico de vida útil restante */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Vida Útil Restante (horas)</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.remainingUsefulLife}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                layout="vertical"
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={100} />
                <Tooltip />
                <Legend />
                <Bar dataKey="rul" name="Horas Restantes">
                  {data.remainingUsefulLife.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={
                        entry.status === 'critical' ? '#f87272' : 
                        entry.status === 'warning' ? '#fbbd23' : 
                        '#36d399'
                      } 
                    />
                  ))}
                </Bar>
                {/* Linha de referência para o limiar crítico */}
                <ReferenceLine x={500} stroke="red" strokeDasharray="3 3" label="Limiar Crítico" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico de componentes com maior risco de falha */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Componentes com Maior Risco de Falha</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.componentFailureRisk}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar 
                  dataKey="risco" 
                  name="Risco de Falha (%)" 
                  fill="#7c3aed"
                  background={{ fill: '#eee' }}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico de distribuição de tipos de manutenção */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Distribuição de Tipos de Manutenção</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.maintenanceTypeDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {data.maintenanceTypeDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico de tendência de custo de manutenção */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Tendência de Custo de Manutenção</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={data.maintenanceCostTrend}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="mes" />
                <YAxis />
                <Tooltip formatter={(value) => `R$ ${value.toFixed(2)}`} />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="preventiva" 
                  name="Manutenção Preventiva" 
                  stackId="1"
                  stroke="#36d399" 
                  fill="#36d399" 
                  fillOpacity={0.6} 
                />
                <Area 
                  type="monotone" 
                  dataKey="corretiva" 
                  name="Manutenção Corretiva" 
                  stackId="1"
                  stroke="#f87272" 
                  fill="#f87272" 
                  fillOpacity={0.6} 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Economia estimada */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Economia Estimada com Manutenção Preditiva</h2>
          <div className="flex flex-col items-center justify-center h-64">
            <div className="text-5xl font-bold text-success">R$ 120.500</div>
            <p className="text-gray-600 mt-2">Economia anual estimada</p>
            <div className="grid grid-cols-3 gap-4 w-full mt-6">
              <div className="text-center">
                <p className="text-xl font-semibold">-35%</p>
                <p className="text-sm text-gray-600">Tempo de Inatividade</p>
              </div>
              <div className="text-center">
                <p className="text-xl font-semibold">-28%</p>
                <p className="text-sm text-gray-600">Custo de Manutenção</p>
              </div>
              <div className="text-center">
                <p className="text-xl font-semibold">+15%</p>
                <p className="text-sm text-gray-600">Vida Útil dos Equipamentos</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Cronograma de manutenção */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
          <h2 className="text-lg font-semibold">Cronograma de Manutenção</h2>
          <div className="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-2 mt-2 md:mt-0">
            <div className="flex space-x-1">
              <button 
                className={`px-3 py-1 rounded-md text-xs ${filterPriority === 'all' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => handleFilterChange('all')}
              >
                Todas
              </button>
              <button 
                className={`px-3 py-1 rounded-md text-xs ${filterPriority === 'critical' ? 'bg-error text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => handleFilterChange('critical')}
              >
                Crítica
              </button>
              <button 
                className={`px-3 py-1 rounded-md text-xs ${filterPriority === 'high' ? 'bg-warning text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => handleFilterChange('high')}
              >
                Alta
              </button>
              <button 
                className={`px-3 py-1 rounded-md text-xs ${filterPriority === 'medium' ? 'bg-info text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => handleFilterChange('medium')}
              >
                Média
              </button>
              <button 
                className={`px-3 py-1 rounded-md text-xs ${filterPriority === 'low' ? 'bg-success text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => handleFilterChange('low')}
              >
                Baixa
              </button>
            </div>
            <button className="flex items-center px-3 py-1 bg-gray-200 text-gray-700 rounded-md text-sm">
              <Download className="h-4 w-4 mr-1" />
              Exportar
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="table w-full">
            <thead>
              <tr>
                <th>ID</th>
                <th>Máquina</th>
                <th>Tipo</th>
                <th>Data</th>
                <th>Duração Est.</th>
                <th>Prioridade</th>
                <th>Componentes</th>
                <th>Ação</th>
              </tr>
            </thead>
            <tbody>
              {filteredSchedule.map((item) => (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td>{item.machine}</td>
                  <td>
                    <MaintenanceTypeBadge type={item.type} />
                  </td>
                  <td>{new Date(item.date).toLocaleDateString('pt-BR')}</td>
                  <td>{item.estimatedDuration}h</td>
                  <td>
                    <PriorityBadge priority={item.priority} />
                  </td>
                  <td>
                    <div className="flex flex-wrap gap-1">
                      {item.components.map((component, idx) => (
                        <span 
                          key={idx} 
                          className="px-2 py-0.5 bg-gray-200 text-gray-700 rounded-full text-xs"
                        >
                          {component}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td>
                    <button className="btn btn-xs btn-primary">Detalhes</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filteredSchedule.length === 0 && (
          <div className="text-center py-4">
            <p className="text-gray-500">Nenhuma manutenção encontrada com os filtros atuais.</p>
          </div>
        )}
      </div>

      {/* Recomendações de manutenção */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">Recomendações de Manutenção</h2>
        <div className="space-y-4">
          <div className="p-4 border-l-4 border-error bg-error bg-opacity-10 rounded-r-md">
            <div className="flex items-start">
              <AlertTriangle className="h-5 w-5 text-error mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">Compressor #2 requer manutenção urgente</p>
                <p className="text-sm text-gray-600">O sistema detectou um padrão de vibração anormal que indica falha iminente no motor. Recomenda-se manutenção corretiva imediata.</p>
                <p className="text-xs text-gray-500 mt-1">Probabilidade de falha: 85% nos próximos 7 dias</p>
              </div>
            </div>
          </div>
          <div className="p-4 border-l-4 border-warning bg-warning bg-opacity-10 rounded-r-md">
            <div className="flex items-start">
              <Wrench className="h-5 w-5 text-warning mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">Fresadora #2 necessita substituição de componentes</p>
                <p className="text-sm text-gray-600">A bomba hidráulica está apresentando sinais de desgaste acelerado. Recomenda-se substituição preventiva nas próximas 2 semanas.</p>
                <p className="text-xs text-gray-500 mt-1">Vida útil restante estimada: 820 horas</p>
              </div>
            </div>
          </div>
          <div className="p-4 border-l-4 border-info bg-info bg-opacity-10 rounded-r-md">
            <div className="flex items-start">
              <Calendar className="h-5 w-5 text-info mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">Torno CNC #1 programado para manutenção preventiva</p>
                <p className="text-sm text-gray-600">Manutenção preventiva programada para 15/04/2025. Inclui verificação do motor, rolamentos e sistema de refrigeração.</p>
                <p className="text-xs text-gray-500 mt-1">Duração estimada: 4 horas</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PredictiveMaintenance;
