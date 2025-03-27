import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ScatterChart, Scatter, ZAxis, Cell
} from 'recharts';
import { AlertTriangle, Search, Filter, Download } from 'lucide-react';

// Dados simulados para detecção de anomalias
const generateMockData = () => {
  // Dados de anomalias ao longo do tempo
  const anomalyTimeData = Array.from({ length: 30 }, (_, i) => {
    const day = i + 1;
    return {
      dia: `${day < 10 ? '0' : ''}${day}/03`,
      anomalias: Math.floor(Math.random() * 5),
      anomalias_graves: Math.floor(Math.random() * 2)
    };
  });

  // Dados de distribuição de scores de anomalia
  const anomalyScoreDistribution = Array.from({ length: 100 }, () => {
    return {
      score: Math.random(),
      count: Math.floor(Math.random() * 20)
    };
  });

  // Anomalias recentes
  const recentAnomalies = [
    { 
      id: 1, 
      machine: 'Torno CNC #3', 
      parameter: 'Temperatura', 
      value: 85.2, 
      expected: 70.0, 
      deviation: 21.7, 
      timestamp: '2025-03-26T14:30:00', 
      score: 0.92,
      status: 'open'
    },
    { 
      id: 2, 
      machine: 'Fresadora #2', 
      parameter: 'Vibração', 
      value: 1.8, 
      expected: 0.5, 
      deviation: 260.0, 
      timestamp: '2025-03-26T13:45:00', 
      score: 0.88,
      status: 'investigating'
    },
    { 
      id: 3, 
      machine: 'Injetora #5', 
      parameter: 'Pressão', 
      value: 145.0, 
      expected: 120.0, 
      deviation: 20.8, 
      timestamp: '2025-03-26T12:15:00', 
      score: 0.75,
      status: 'resolved'
    },
    { 
      id: 4, 
      machine: 'Compressor #1', 
      parameter: 'Temperatura', 
      value: 78.5, 
      expected: 60.0, 
      deviation: 30.8, 
      timestamp: '2025-03-26T11:20:00', 
      score: 0.81,
      status: 'open'
    },
    { 
      id: 5, 
      machine: 'Robô Industrial #2', 
      parameter: 'Precisão', 
      value: 0.28, 
      expected: 0.1, 
      deviation: 180.0, 
      timestamp: '2025-03-26T10:05:00', 
      score: 0.85,
      status: 'resolved'
    }
  ];

  // Dados de correlação entre parâmetros
  const parameterCorrelation = [];
  for (let i = 0; i < 50; i++) {
    const temp = 50 + Math.random() * 40;
    const vibration = 0.2 + Math.random() * 1.5;
    const isAnomaly = (temp > 80 || vibration > 1.2);
    
    parameterCorrelation.push({
      temperatura: temp,
      vibracao: vibration,
      anomalia: isAnomaly ? 1 : 0
    });
  }

  // Anomalias por tipo de máquina
  const anomaliesByMachineType = [
    { name: 'Torno CNC', value: 12, color: '#f87272' },
    { name: 'Fresadora', value: 8, color: '#fbbd23' },
    { name: 'Injetora', value: 15, color: '#36d399' },
    { name: 'Robô', value: 5, color: '#3abff8' },
    { name: 'Compressor', value: 10, color: '#7c3aed' }
  ];

  return {
    anomalyTimeData,
    anomalyScoreDistribution,
    recentAnomalies,
    parameterCorrelation,
    anomaliesByMachineType
  };
};

const AnomalyStatusBadge = ({ status }) => {
  let color = '';
  let text = '';

  switch (status) {
    case 'open':
      color = 'bg-error';
      text = 'Aberta';
      break;
    case 'investigating':
      color = 'bg-warning';
      text = 'Em Investigação';
      break;
    case 'resolved':
      color = 'bg-success';
      text = 'Resolvida';
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

const AnomalyDetection = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

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

  const handleFilterChange = (status) => {
    setFilterStatus(status);
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const filteredAnomalies = data?.recentAnomalies.filter(anomaly => {
    // Filtrar por status
    if (filterStatus !== 'all' && anomaly.status !== filterStatus) {
      return false;
    }
    
    // Filtrar por termo de busca
    if (searchTerm && !anomaly.machine.toLowerCase().includes(searchTerm.toLowerCase()) && 
        !anomaly.parameter.toLowerCase().includes(searchTerm.toLowerCase())) {
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
        <h1 className="text-2xl font-bold text-gray-800">Detecção de Anomalias</h1>
        <p className="text-gray-600">Identifique comportamentos anormais nas máquinas industriais</p>
      </div>

      {/* Filtros e seleção de intervalo de tempo */}
      <div className="flex flex-col md:flex-row justify-between mb-6">
        <div className="mb-4 md:mb-0">
          <label className="block text-sm font-medium text-gray-700 mb-1">Intervalo de Tempo</label>
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
          <label className="block text-sm font-medium text-gray-700 mb-1">Limiar de Anomalia</label>
          <select className="border border-gray-300 rounded-md px-3 py-1 text-sm">
            <option value="0.7">0.7 (Padrão)</option>
            <option value="0.8">0.8 (Rigoroso)</option>
            <option value="0.6">0.6 (Sensível)</option>
            <option value="0.9">0.9 (Muito rigoroso)</option>
          </select>
        </div>
      </div>

      {/* Cards de estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Total de Anomalias</p>
              <p className="text-2xl font-bold mt-1">42</p>
              <p className="text-xs text-error mt-1">
                +15% em relação ao período anterior
              </p>
            </div>
            <div className="p-3 rounded-full bg-error bg-opacity-10">
              <AlertTriangle className="h-6 w-6 text-error" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Anomalias Graves</p>
              <p className="text-2xl font-bold mt-1">12</p>
              <p className="text-xs text-error mt-1">
                +8% em relação ao período anterior
              </p>
            </div>
            <div className="p-3 rounded-full bg-error bg-opacity-10">
              <AlertTriangle className="h-6 w-6 text-error" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Taxa de Detecção</p>
              <p className="text-2xl font-bold mt-1">94.2%</p>
              <p className="text-xs text-success mt-1">
                +2.5% em relação ao período anterior
              </p>
            </div>
            <div className="p-3 rounded-full bg-success bg-opacity-10">
              <Search className="h-6 w-6 text-success" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Tempo Médio de Resolução</p>
              <p className="text-2xl font-bold mt-1">4.8h</p>
              <p className="text-xs text-success mt-1">
                -15% em relação ao período anterior
              </p>
            </div>
            <div className="p-3 rounded-full bg-primary bg-opacity-10">
              <Filter className="h-6 w-6 text-primary" />
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Gráfico de anomalias ao longo do tempo */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Anomalias ao Longo do Tempo</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={data.anomalyTimeData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="dia" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="anomalias" 
                  name="Anomalias" 
                  stroke="#f87272" 
                  activeDot={{ r: 8 }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="anomalias_graves" 
                  name="Anomalias Graves" 
                  stroke="#7c3aed" 
                  activeDot={{ r: 8 }} 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico de distribuição de scores de anomalia */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Distribuição de Scores de Anomalia</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.anomalyScoreDistribution}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="score" 
                  type="number" 
                  domain={[0, 1]} 
                  tickCount={11} 
                  tickFormatter={(value) => value.toFixed(1)} 
                />
                <YAxis />
                <Tooltip 
                  formatter={(value, name, props) => [value, 'Contagem']}
                  labelFormatter={(value) => `Score: ${value.toFixed(2)}`}
                />
                <Bar dataKey="count" fill="#0ea5e9" name="Contagem" />
                {/* Linha vertical para o limiar */}
                <ReferenceLine x={0.7} stroke="red" strokeDasharray="3 3" label="Limiar" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico de correlação entre parâmetros */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Correlação entre Parâmetros</h2>
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
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Legend />
                <Scatter 
                  name="Parâmetros" 
                  data={data.parameterCorrelation} 
                  fill="#7c3aed"
                  shape="circle"
                >
                  {data.parameterCorrelation.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.anomalia === 1 ? '#f87272' : '#36d399'} 
                    />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center mt-2 text-sm">
            <div className="flex items-center mr-4">
              <div className="w-3 h-3 rounded-full bg-success mr-1"></div>
              <span>Normal</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-error mr-1"></div>
              <span>Anomalia</span>
            </div>
          </div>
        </div>

        {/* Gráfico de anomalias por tipo de máquina */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Anomalias por Tipo de Máquina</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.anomaliesByMachineType}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                layout="vertical"
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" name="Anomalias">
                  {data.anomaliesByMachineType.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Lista de anomalias recentes */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
          <h2 className="text-lg font-semibold">Anomalias Recentes</h2>
          <div className="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-2 mt-2 md:mt-0">
            <div className="relative">
              <input
                type="text"
                placeholder="Buscar anomalias..."
                className="pl-8 pr-4 py-1 border border-gray-300 rounded-md text-sm"
                value={searchTerm}
                onChange={handleSearch}
              />
              <Search className="absolute left-2 top-1.5 h-4 w-4 text-gray-400" />
            </div>
            <div className="flex space-x-1">
              <button 
                className={`px-3 py-1 rounded-md text-xs ${filterStatus === 'all' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => handleFilterChange('all')}
              >
                Todas
              </button>
              <button 
                className={`px-3 py-1 rounded-md text-xs ${filterStatus === 'open' ? 'bg-error text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => handleFilterChange('open')}
              >
                Abertas
              </button>
              <button 
                className={`px-3 py-1 rounded-md text-xs ${filterStatus === 'investigating' ? 'bg-warning text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => handleFilterChange('investigating')}
              >
                Em Investigação
              </button>
              <button 
                className={`px-3 py-1 rounded-md text-xs ${filterStatus === 'resolved' ? 'bg-success text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => handleFilterChange('resolved')}
              >
                Resolvidas
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
                <th>Parâmetro</th>
                <th>Valor</th>
                <th>Esperado</th>
                <th>Desvio (%)</th>
                <th>Score</th>
                <th>Status</th>
                <th>Ação</th>
              </tr>
            </thead>
            <tbody>
              {filteredAnomalies.map((anomaly) => (
                <tr key={anomaly.id}>
                  <td>{anomaly.id}</td>
                  <td>{anomaly.machine}</td>
                  <td>{anomaly.parameter}</td>
                  <td className="text-right">{anomaly.value.toFixed(1)}</td>
                  <td className="text-right">{anomaly.expected.toFixed(1)}</td>
                  <td className="text-right">
                    <span className={anomaly.deviation > 50 ? 'text-error' : anomaly.deviation > 20 ? 'text-warning' : 'text-gray-700'}>
                      {anomaly.deviation.toFixed(1)}%
                    </span>
                  </td>
                  <td>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div 
                        className={`h-2.5 rounded-full ${
                          anomaly.score > 0.8 ? 'bg-error' : 
                          anomaly.score > 0.6 ? 'bg-warning' : 
                          'bg-success'
                        }`} 
                        style={{ width: `${anomaly.score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-500">{(anomaly.score * 100).toFixed(0)}%</span>
                  </td>
                  <td>
                    <AnomalyStatusBadge status={anomaly.status} />
                  </td>
                  <td>
                    <button className="btn btn-xs btn-primary">Detalhes</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filteredAnomalies.length === 0 && (
          <div className="text-center py-4">
            <p className="text-gray-500">Nenhuma anomalia encontrada com os filtros atuais.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnomalyDetection;
