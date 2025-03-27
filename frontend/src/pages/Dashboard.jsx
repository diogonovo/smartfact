import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Cell
} from 'recharts';
import { AlertTriangle, Activity, Wrench, TrendingUp } from 'lucide-react';
import axios from 'axios';

const StatCard = ({ title, value, icon, color, change }) => {
  const Icon = icon;
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-500 text-sm">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {change && (
            <p className={`text-xs mt-1 ${change > 0 ? 'text-success' : 'text-error'}`}>
              {change > 0 ? '+' : ''}{change}% em relação ao período anterior
            </p>
          )}
        </div>
        <div className={`p-3 rounded-full bg-opacity-10 ${color}`}>
          <Icon className={`h-6 w-6 ${color}`} />
        </div>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const statsRes = await axios.get('/analytics/kpis');

        const machineStatus = statsRes.data.reduce((acc, machine) => {
          const key = machine.status || 'Desconhecido';
          acc[key] = (acc[key] || 0) + 1;
          return acc;
        }, {});

        const pieData = Object.entries(machineStatus).map(([status, value]) => ({
          name: status,
          value,
          color: status === 'Operational' ? '#36d399' :
                 status === 'Manutenção' ? '#fbbd23' :
                 status === 'Falha' ? '#f87272' :
                 '#d1d5db'
        }));

        const anomaliesByMachineType = statsRes.data.map(m => ({
          name: m.machine_type,
          anomalias: m.num_anomalies
        }));

        const efficiencyByMachine = statsRes.data.map(m => ({
          name: `Máq. ${m.machine_id}`,
          eficiencia: 85 + Math.round(Math.random() * 10) // simula eficiência
        }));

        setData({
          machineStatus: pieData,
          anomaliesByMachineType,
          efficiencyByMachine,
          failurePredictions: [],
          recentAlerts: []
        });
      } catch (error) {
        console.error('Erro ao buscar dados:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

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
        <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-600">Visão geral do sistema de análise de máquinas industriais</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard title="Máquinas Monitoradas" value={data.machineStatus.reduce((sum, m) => sum + m.value, 0)} icon={Activity} color="text-primary" change={5} />
        <StatCard title="Anomalias Detectadas" value={data.anomaliesByMachineType.reduce((sum, m) => sum + m.anomalias, 0)} icon={AlertTriangle} color="text-error" change={-12} />
        <StatCard title="Manutenções Previstas" value="8" icon={Wrench} color="text-warning" change={3} />
        <StatCard title="Eficiência Média" value="87%" icon={TrendingUp} color="text-success" change={2.5} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Status das Máquinas</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.machineStatus}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {data.machineStatus.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Anomalias por Tipo de Máquina</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.anomaliesByMachineType} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="anomalias" fill="#f87272" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Eficiência por Máquina</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.efficiencyByMachine} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="eficiencia" fill="#36d399" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4">
          <h2 className="text-lg font-semibold mb-4">Previsão de Falhas (Próximos 7 dias)</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.failurePredictions} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="dia" />
                <YAxis domain={[0, 1]} tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                <Tooltip formatter={(value) => `${(value * 100).toFixed(1)}%`} />
                <Legend />
                <Line type="monotone" dataKey="probabilidade" stroke="#7c3aed" activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
