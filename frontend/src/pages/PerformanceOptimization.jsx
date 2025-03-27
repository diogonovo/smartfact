import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ScatterChart, Scatter, ZAxis, Cell, RadarChart, 
  PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import { TrendingUp, Zap, Settings, Download, Sliders } from 'lucide-react';

// Dados simulados para otimização de desempenho
const generateMockData = () => {
  // Dados de clusters de desempenho
  const performanceClusters = [
    { x: 65, y: 0.8, z: 22, cluster: 0, efficiency: 78 },
    { x: 68, y: 0.7, z: 20, cluster: 0, efficiency: 80 },
    { x: 70, y: 0.9, z: 24, cluster: 0, efficiency: 76 },
    { x: 72, y: 0.75, z: 21, cluster: 0, efficiency: 79 },
    { x: 67, y: 0.85, z: 23, cluster: 0, efficiency: 77 },
    
    { x: 80, y: 0.5, z: 18, cluster: 1, efficiency: 85 },
    { x: 82, y: 0.45, z: 17, cluster: 1, efficiency: 87 },
    { x: 79, y: 0.55, z: 19, cluster: 1, efficiency: 84 },
    { x: 81, y: 0.48, z: 16, cluster: 1, efficiency: 88 },
    { x: 83, y: 0.52, z: 18, cluster: 1, efficiency: 86 },
    
    { x: 90, y: 0.3, z: 15, cluster: 2, efficiency: 92 },
    { x: 92, y: 0.25, z: 14, cluster: 2, efficiency: 94 },
    { x: 89, y: 0.35, z: 16, cluster: 2, efficiency: 91 },
    { x: 91, y: 0.28, z: 13, cluster: 2, efficiency: 95 },
    { x: 93, y: 0.32, z: 15, cluster: 2, efficiency: 93 }
  ];

  // Dados de parâmetros ótimos
  const optimalParameters = [
    { parameter: 'Temperatura', atual: 72, otimo: 90, unidade: '°C' },
    { parameter: 'Vibração', atual: 0.8, otimo: 0.3, unidade: 'mm/s' },
    { parameter: 'Consumo de Energia', atual: 22, otimo: 15, unidade: 'kW' },
    { parameter: 'Velocidade', atual: 1800, otimo: 2200, unidade: 'RPM' },
    { parameter: 'Pressão', atual: 120, otimo: 150, unidade: 'bar' }
  ];

  // Dados de potencial de otimização por máquina
  const optimizationPotential = [
    { name: 'Torno CNC #1', potencial: 15, status: 'medium' },
    { name: 'Fresadora #2', potencial: 22, status: 'high' },
    { name: 'Injetora #1', potencial: 8, status: 'low' },
    { name: 'Robô Industrial #3', potencial: 5, status: 'low' },
    { name: 'Compressor #2', potencial: 18, status: 'medium' },
    { name: 'Torno CNC #2', potencial: 12, status: 'medium' },
    { name: 'Fresadora #1', potencial: 25, status: 'high' },
    { name: 'Injetora #3', potencial: 10, status: 'low' }
  ];

  // Dados de comparação de desempenho antes e depois da otimização
  const performanceComparison = [
    { metrica: 'Eficiência', antes: 78, depois: 92 },
    { metrica: 'Produtividade', antes: 65, depois: 85 },
    { metrica: 'Qualidade', antes: 82, depois: 95 },
    { metrica: 'Consumo de Energia', antes: 90, depois: 70 },
    { metrica: 'Tempo de Ciclo', antes: 85, depois: 65 }
  ];

  // Dados de tendência de eficiência ao longo do tempo
  const efficiencyTrend = Array.from({ length: 12 }, (_, i) => {
    const month = i + 1;
    const baseEfficiency = 75 + (i * 1.5);
    return {
      mes: `${month < 10 ? '0' : ''}${month}/25`,
      eficiencia: baseEfficiency + Math.random() * 3,
      meta: 90
    };
  });

  // Cenários de otimização
  const optimizationScenarios = [
    { 
      id: 1, 
      name: 'Cenário Padrão', 
      description: 'Configuração recomendada pelo sistema para equilíbrio entre eficiência e qualidade',
      parameters: [
        { name: 'Temperatura', value: 90, unit: '°C' },
        { name: 'Vibração', value: 0.3, unit: 'mm/s' },
        { name: 'Consumo de Energia', value: 15, unit: 'kW' },
        { name: 'Velocidade', value: 2200, unit: 'RPM' },
        { name: 'Pressão', value: 150, unit: 'bar' }
      ],
      expectedResults: {
        efficiency: 92,
        productivity: 85,
        quality: 95,
        energyConsumption: 70,
        cycleTime: 65
      }
    },
    { 
      id: 2, 
      name: 'Máxima Produtividade', 
      description: 'Configuração otimizada para máxima produtividade, com maior consumo de energia',
      parameters: [
        { name: 'Temperatura', value: 95, unit: '°C' },
        { name: 'Vibração', value: 0.4, unit: 'mm/s' },
        { name: 'Consumo de Energia', value: 18, unit: 'kW' },
        { name: 'Velocidade', value: 2500, unit: 'RPM' },
        { name: 'Pressão', value: 160, unit: 'bar' }
      ],
      expectedResults: {
        efficiency: 88,
        productivity: 95,
        quality: 85,
        energyConsumption: 85,
        cycleTime: 55
      }
    },
    { 
      id: 3, 
      name: 'Economia de Energia', 
      description: 'Configuração otimizada para menor consumo de energia, com produtividade reduzida',
      parameters: [
        { name: 'Temperatura', value: 85, unit: '°C' },
        { name: 'Vibração', value: 0.25, unit: 'mm/s' },
        { name: 'Consumo de Energia', value: 12, unit: 'kW' },
        { name: 'Velocidade', value: 1900, unit: 'RPM' },
        { name: 'Pressão', value: 140, unit: 'bar' }
      ],
      expectedResults: {
        efficiency: 86,
        productivity: 75,
        quality: 90,
        energyConsumption: 55,
        cycleTime: 75
      }
    }
  ];

  return {
    performanceClusters,
    optimalParameters,
    optimizationPotential,
    performanceComparison,
    efficiencyTrend,
    optimizationScenarios
  };
};

const PotentialBadge = ({ potential }) => {
  let color = '';
  let text = '';

  if (potential > 20) {
    color = 'bg-error';
    text = 'Alto';
  } else if (potential > 10) {
    color = 'bg-warning';
    text = 'Médio';
  } else {
    color = 'bg-success';
    text = 'Baixo';
  }

  return (
    <span className={`px-2 py-1 rounded-full text-xs text-white ${color}`}>
      {text}
    </span>
  );
};

const PerformanceOptimization = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedMachine, setSelectedMachine] = useState(null);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [clusterView, setClusterView] = useState('3d');

  useEffect(() => {
    // Simulando uma chamada de API
    const fetchData = async () => {
      setLoading(true);
      try {
        // Em um cenário real, isso seria uma chamada à API
        const mockData = generateMockData();
        setData(mockData);
        // Selecionar o primeiro cenário por padrão
        if (mockData.optimizationScenarios.length > 0) {
          setSelectedScenario(mockData.optimizationScenarios[0]);
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

  const handleScenarioSelect = (scenario) => {
    setSelectedScenario(scenario);
  };

  const handleClusterViewChange = (view) => {
    setClusterView(view);
  };

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Calcular a média de eficiência atual e otimizada
  const avgCurrentEfficiency = data.optimizationPotential.reduce((sum, item) => sum + (100 - item.potencial), 0) / data.optimizationPotential.length;
  const avgOptimizedEfficiency = data.optimizationPotential.reduce((sum, item) => sum + 100, 0) / data.optimizationPotential.length;

  // Preparar dados para o gráfico de radar
  const radarData = [
    {
      subject: 'Eficiência',
      A: selectedScenario?.expectedResults.efficiency || 0,
      fullMark: 100,
    },
    {
      subject: 'Produtividade',
      A: selectedScenario?.expectedResults.productivity || 0,
      fullMark: 100,
    },
    {
      subject: 'Qualidade',
      A: selectedScenario?.expectedResults.quality || 0,
      fullMark: 100,
    },
    {
      subject: 'Economia de Energia',
      A: 100 - (selectedScenario?.expectedResults.energyConsumption || 0),
      fullMark: 100,
    },
    {
      subject: 'Velocidade',
      A: 100 - (selectedScenario?.expectedResults.cycleTime || 0),
      fullMark: 100,
    },
  ];

  return (
    <div className="container mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Otimização de Desempenho</h1>
        <p className="text-gray-600">Identifique parâmetros ótimos de operação para maximizar a eficiência das máquinas</p>
      </div>

      {/* Cards de estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Eficiência Média Atual</p>
              <p className="text-2xl font-bold mt-1">{avgCurrentEfficiency.toFixed(1)}%</p>
              <p className="text-xs text-success mt-1">
                +2.5% em relação ao mês anterior
              </p>
            </div>
            <div className="p-3 rounded-full bg-primary bg-opacity-10">
              <TrendingUp className="h-6 w-6 text-primary" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Eficiência Potencial</p>
              <p className="text-2xl font-bold mt-1">{avgOptimizedEfficiency.toFixed(1)}%</p>
              <p className="text-xs text-success mt-1">
                +{(avgOptimizedEfficiency - avgCurrentEfficiency).toFixed(1)}% de ganho potencial
              </p>
            </div>
            <div className="p-3 rounded-full bg-success bg-opacity-10">
              <TrendingUp className="h-6 w-6 text-success" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Economia Potencial</p>
              <p className="text-2xl font-bold mt-1">R$ 85.200</p>
              <p className="text-xs text-success mt-1">
                Economia anual estimada
              </p>
            </div>
            <div className="p-3 rounded-full bg-success bg-opacity-10">
              <Zap className="h-6 w-6 text-success" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">Máquinas Otimizáveis</p>
              <p className="text-2xl font-bold mt-1">8</p>
              <p className="text-xs text-warning mt-1">
                3 com alto potencial de otimização
              </p>
            </div>
            <div className="p-3 rounded-full bg-warning bg-opacity-10">
              <Settings className="h-6 w-6 text-warning" />
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Gráfico de clusters de desempenho */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Clusters de Desempenho</h2>
            <div className="flex space-x-2">
              <button 
                className={`px-3 py-1 rounded-md text-xs ${clusterView === '3d' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => handleClusterViewChange('3d')}
              >
                3D
              </button>
              <button 
                className={`px-3 py-1 rounded-md text-xs ${clusterView === '2d' ? 'bg-primary text-white' : 'bg-gray-200 text-gray-700'}`}
                onClick={() => handleClusterViewChange('2d')}
              >
                2D
              </button>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  type="number" 
                  dataKey="x" 
                  name="Temperatura" 
                  unit="°C" 
                />
                <YAxis 
                  type="number" 
                  dataKey="y" 
                  name="Vibração" 
                  unit="mm/s" 
                />
                {clusterView === '3d' && (
                  <ZAxis 
                    type="number" 
                    dataKey="z" 
                    range={[60, 400]} 
                    name="Consumo" 
                    unit="kW" 
                  />
                )}
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Legend />
                <Scatter 
                  name="Parâmetros Operacionais" 
                  data={data.performanceClusters} 
                  fill="#8884d8"
                >
                  {data.performanceClusters.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={
                        entry.cluster === 0 ? '#f87272' : 
                        entry.cluster === 1 ? '#fbbd23' : 
                        '#36d399'
                      } 
                    />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center mt-2 text-sm">
            <div className="flex items-center mr-4">
              <div className="w-3 h-3 rounded-full bg-error mr-1"></div>
              <span>Cluster 1 (Baixa Eficiência)</span>
            </div>
            <div className="flex items-center mr-4">
              <div className="w-3 h-3 rounded-full bg-warning mr-1"></div>
              <span>Cluster 2 (Média Eficiência)</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-success mr-1"></div>
              <span>Cluster 3 (Alta Eficiência)</span>
            </div>
          </div>
        </div>

        {/* Gráfico de parâmetros ótimos */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Parâmetros Ótimos vs. Atuais</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.optimalParameters}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                layout="vertical"
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="parameter" type="category" width={150} />
                <Tooltip 
                  formatter={(value, name) => [
                    `${value} ${data.optimalParameters.find(p => p.parameter === name)?.unidade || ''}`,
                    name === 'atual' ? 'Valor Atual' : 'Valor Ótimo'
                  ]}
                />
                <Legend />
                <Bar dataKey="atual" name="Valor Atual" fill="#f87272" />
                <Bar dataKey="otimo" name="Valor Ótimo" fill="#36d399" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico de potencial de otimização por máquina */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Potencial de Otimização por Máquina</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.optimizationPotential}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 30]} />
                <Tooltip formatter={(value) => [`${value}%`, 'Potencial de Otimização']} />
                <Legend />
                <Bar 
                  dataKey="potencial" 
                  name="Potencial de Otimização (%)" 
                  fill="#7c3aed"
                >
                  {data.optimizationPotential.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={
                        entry.potencial > 20 ? '#f87272' : 
                        entry.potencial > 10 ? '#fbbd23' : 
                        '#36d399'
                      } 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico de comparação de desempenho */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Comparação de Desempenho</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data.performanceComparison}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                layout="vertical"
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 100]} />
                <YAxis dataKey="metrica" type="category" width={150} />
                <Tooltip formatter={(value) => [`${value}%`, '']} />
                <Legend />
                <Bar dataKey="antes" name="Antes da Otimização" fill="#f87272" />
                <Bar dataKey="depois" name="Depois da Otimização" fill="#36d399" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico de tendência de eficiência */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Tendência de Eficiência</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={data.efficiencyTrend}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="mes" />
                <YAxis domain={[70, 100]} />
                <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, '']} />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="eficiencia" 
                  name="Eficiência" 
                  stroke="#0ea5e9" 
                  activeDot={{ r: 8 }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="meta" 
                  name="Meta" 
                  stroke="#f87272" 
                  strokeDasharray="5 5" 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico de radar para cenário selecionado */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Perfil do Cenário de Otimização</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis angle={30} domain={[0, 100]} />
                <Radar
                  name="Desempenho"
                  dataKey="A"
                  stroke="#8884d8"
                  fill="#8884d8"
                  fillOpacity={0.6}
                />
                <Tooltip formatter={(value) => [`${value}%`, '']} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Cenários de otimização */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
          <h2 className="text-lg font-semibold">Cenários de Otimização</h2>
          <div className="flex space-x-2 mt-2 md:mt-0">
            <button className="flex items-center px-3 py-1 bg-primary text-white rounded-md text-sm">
              <Sliders className="h-4 w-4 mr-1" />
              Criar Novo Cenário
            </button>
            <button className="flex items-center px-3 py-1 bg-gray-200 text-gray-700 rounded-md text-sm">
              <Download className="h-4 w-4 mr-1" />
              Exportar
            </button>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {data.optimizationScenarios.map((scenario) => (
            <div 
              key={scenario.id}
              className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                selectedScenario && selectedScenario.id === scenario.id 
                  ? 'border-primary bg-primary bg-opacity-5' 
                  : 'border-gray-200 hover:border-primary'
              }`}
              onClick={() => handleScenarioSelect(scenario)}
            >
              <h3 className="font-semibold text-lg">{scenario.name}</h3>
              <p className="text-sm text-gray-600 mt-1">{scenario.description}</p>
              <div className="mt-3">
                <div className="flex justify-between text-sm">
                  <span>Eficiência:</span>
                  <span className="font-medium">{scenario.expectedResults.efficiency}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Produtividade:</span>
                  <span className="font-medium">{scenario.expectedResults.productivity}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Consumo de Energia:</span>
                  <span className="font-medium">{scenario.expectedResults.energyConsumption}%</span>
                </div>
              </div>
              {selectedScenario && selectedScenario.id === scenario.id && (
                <div className="mt-2 text-right">
                  <button className="text-primary text-sm font-medium">Aplicar Cenário</button>
                </div>
              )}
            </div>
          ))}
        </div>

        {selectedScenario && (
          <div className="border-t pt-4">
            <h3 className="font-semibold text-lg mb-3">Detalhes do Cenário: {selectedScenario.name}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Parâmetros Recomendados</h4>
                <div className="overflow-x-auto">
                  <table className="table w-full">
                    <thead>
                      <tr>
                        <th>Parâmetro</th>
                        <th className="text-right">Valor</th>
                        <th className="text-right">Unidade</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedScenario.parameters.map((param, idx) => (
                        <tr key={idx}>
                          <td>{param.name}</td>
                          <td className="text-right">{param.value}</td>
                          <td className="text-right">{param.unit}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Resultados Esperados</h4>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <span className="w-1/2">Eficiência:</span>
                    <div className="w-1/2">
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div 
                          className="h-2.5 rounded-full bg-success" 
                          style={{ width: `${selectedScenario.expectedResults.efficiency}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-500">{selectedScenario.expectedResults.efficiency}%</span>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="w-1/2">Produtividade:</span>
                    <div className="w-1/2">
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div 
                          className="h-2.5 rounded-full bg-primary" 
                          style={{ width: `${selectedScenario.expectedResults.productivity}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-500">{selectedScenario.expectedResults.productivity}%</span>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="w-1/2">Qualidade:</span>
                    <div className="w-1/2">
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div 
                          className="h-2.5 rounded-full bg-info" 
                          style={{ width: `${selectedScenario.expectedResults.quality}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-500">{selectedScenario.expectedResults.quality}%</span>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="w-1/2">Consumo de Energia:</span>
                    <div className="w-1/2">
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div 
                          className="h-2.5 rounded-full bg-warning" 
                          style={{ width: `${selectedScenario.expectedResults.energyConsumption}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-500">{selectedScenario.expectedResults.energyConsumption}%</span>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="w-1/2">Tempo de Ciclo:</span>
                    <div className="w-1/2">
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div 
                          className="h-2.5 rounded-full bg-error" 
                          style={{ width: `${selectedScenario.expectedResults.cycleTime}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-500">{selectedScenario.expectedResults.cycleTime}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-4 flex justify-end space-x-2">
              <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md">Editar Cenário</button>
              <button className="px-4 py-2 bg-primary text-white rounded-md">Aplicar Cenário</button>
            </div>
          </div>
        )}
      </div>

      {/* Potencial de otimização por máquina */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">Potencial de Otimização por Máquina</h2>
        <div className="overflow-x-auto">
          <table className="table w-full">
            <thead>
              <tr>
                <th>Máquina</th>
                <th>Eficiência Atual</th>
                <th>Eficiência Potencial</th>
                <th>Potencial de Ganho</th>
                <th>Prioridade</th>
                <th>Ação</th>
              </tr>
            </thead>
            <tbody>
              {data.optimizationPotential.map((machine, idx) => (
                <tr key={idx}>
                  <td>{machine.name}</td>
                  <td>{100 - machine.potencial}%</td>
                  <td>100%</td>
                  <td>
                    <span className={
                      machine.potencial > 20 ? 'text-error' : 
                      machine.potencial > 10 ? 'text-warning' : 
                      'text-success'
                    }>
                      +{machine.potencial}%
                    </span>
                  </td>
                  <td>
                    <PotentialBadge potential={machine.potencial} />
                  </td>
                  <td>
                    <button className="btn btn-xs btn-primary">Otimizar</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recomendações de otimização */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">Recomendações de Otimização</h2>
        <div className="space-y-4">
          <div className="p-4 border-l-4 border-error bg-error bg-opacity-10 rounded-r-md">
            <div className="flex items-start">
              <TrendingUp className="h-5 w-5 text-error mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">Fresadora #1 tem alto potencial de otimização</p>
                <p className="text-sm text-gray-600">Ajustar a temperatura para 90°C e reduzir a vibração para 0.3 mm/s pode aumentar a eficiência em 25%.</p>
                <p className="text-xs text-gray-500 mt-1">Economia anual estimada: R$ 28.500</p>
              </div>
            </div>
          </div>
          <div className="p-4 border-l-4 border-warning bg-warning bg-opacity-10 rounded-r-md">
            <div className="flex items-start">
              <Zap className="h-5 w-5 text-warning mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">Torno CNC #1 pode reduzir consumo de energia</p>
                <p className="text-sm text-gray-600">Reduzir o consumo de energia de 22kW para 15kW mantendo a mesma produtividade com ajustes nos parâmetros operacionais.</p>
                <p className="text-xs text-gray-500 mt-1">Economia anual estimada: R$ 15.800</p>
              </div>
            </div>
          </div>
          <div className="p-4 border-l-4 border-info bg-info bg-opacity-10 rounded-r-md">
            <div className="flex items-start">
              <Settings className="h-5 w-5 text-info mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">Compressor #2 pode melhorar desempenho com manutenção</p>
                <p className="text-sm text-gray-600">Uma manutenção preventiva seguida de ajustes nos parâmetros operacionais pode aumentar a eficiência em 18%.</p>
                <p className="text-xs text-gray-500 mt-1">Economia anual estimada: R$ 22.300</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceOptimization;
