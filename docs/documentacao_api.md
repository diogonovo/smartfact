# Documentação da API - Sistema de Análise de Máquinas Industriais com Indústria 4.0

Esta documentação descreve as APIs RESTful disponíveis no Sistema de Análise de Máquinas Industriais com Indústria 4.0. Estas APIs permitem a integração com outros sistemas e o acesso programático a todas as funcionalidades do sistema.

## Informações Gerais

- **URL Base**: `http://8000-ih0ziztfl2htse6x6jvwh-0cf19b87.manus.computer/api`
- **Formato de Resposta**: JSON
- **Autenticação**: Bearer Token (JWT)
- **Versionamento**: v1

## Endpoints Disponíveis

### Máquinas

#### Listar Máquinas

Retorna uma lista de todas as máquinas disponíveis no sistema.

- **URL**: `/machines`
- **Método**: `GET`
- **Parâmetros de Consulta**:
  - `type` (opcional): Filtrar por tipo de máquina
  - `status` (opcional): Filtrar por status da máquina
  - `limit` (opcional): Limitar número de resultados
  - `offset` (opcional): Deslocamento para paginação

**Exemplo de Requisição**:
```
GET /api/machines?type=torno&status=operational&limit=10&offset=0
```

**Exemplo de Resposta**:
```json
{
  "total": 42,
  "limit": 10,
  "offset": 0,
  "data": [
    {
      "id": 1,
      "name": "Torno CNC #1",
      "type": "torno",
      "status": "operational",
      "last_update": "2025-03-26T15:30:45Z",
      "location": "Setor A",
      "metrics": {
        "efficiency": 92,
        "uptime": 98.5,
        "temperature": 42.3
      }
    },
    ...
  ]
}
```

#### Obter Detalhes de uma Máquina

Retorna informações detalhadas sobre uma máquina específica.

- **URL**: `/machines/{id}`
- **Método**: `GET`
- **Parâmetros de URL**:
  - `id`: ID da máquina

**Exemplo de Requisição**:
```
GET /api/machines/1
```

**Exemplo de Resposta**:
```json
{
  "id": 1,
  "name": "Torno CNC #1",
  "type": "torno",
  "model": "CNC-5000",
  "manufacturer": "Industrial Machines Inc.",
  "serial_number": "TN5000-12345",
  "installation_date": "2023-05-15",
  "status": "operational",
  "last_update": "2025-03-26T15:30:45Z",
  "location": "Setor A",
  "metrics": {
    "efficiency": 92,
    "uptime": 98.5,
    "temperature": 42.3,
    "vibration": 0.05,
    "pressure": 5.2,
    "power_consumption": 4.8
  },
  "maintenance": {
    "last_maintenance": "2025-02-10",
    "next_scheduled": "2025-04-10",
    "total_maintenance_count": 12
  }
}
```

#### Obter Leituras de uma Máquina

Retorna as leituras de sensores de uma máquina específica.

- **URL**: `/machines/{id}/readings`
- **Método**: `GET`
- **Parâmetros de URL**:
  - `id`: ID da máquina
- **Parâmetros de Consulta**:
  - `start_time` (opcional): Timestamp inicial (ISO 8601)
  - `end_time` (opcional): Timestamp final (ISO 8601)
  - `metrics` (opcional): Lista de métricas separadas por vírgula
  - `interval` (opcional): Intervalo de agregação (1m, 5m, 1h, 1d)
  - `limit` (opcional): Limitar número de resultados

**Exemplo de Requisição**:
```
GET /api/machines/1/readings?start_time=2025-03-25T00:00:00Z&end_time=2025-03-26T23:59:59Z&metrics=temperature,vibration&interval=1h&limit=24
```

**Exemplo de Resposta**:
```json
{
  "machine_id": 1,
  "machine_name": "Torno CNC #1",
  "start_time": "2025-03-25T00:00:00Z",
  "end_time": "2025-03-26T23:59:59Z",
  "interval": "1h",
  "readings": [
    {
      "timestamp": "2025-03-25T00:00:00Z",
      "temperature": 41.2,
      "vibration": 0.04
    },
    {
      "timestamp": "2025-03-25T01:00:00Z",
      "temperature": 41.5,
      "vibration": 0.05
    },
    ...
  ]
}
```

### Análise

#### Listar Anomalias

Retorna uma lista de anomalias detectadas pelo sistema.

- **URL**: `/analytics/anomalies`
- **Método**: `GET`
- **Parâmetros de Consulta**:
  - `machine_id` (opcional): Filtrar por ID da máquina
  - `severity` (opcional): Filtrar por severidade (low, medium, high, critical)
  - `start_time` (opcional): Timestamp inicial (ISO 8601)
  - `end_time` (opcional): Timestamp final (ISO 8601)
  - `limit` (opcional): Limitar número de resultados
  - `offset` (opcional): Deslocamento para paginação

**Exemplo de Requisição**:
```
GET /api/analytics/anomalies?machine_id=1&severity=high&limit=10
```

**Exemplo de Resposta**:
```json
{
  "total": 3,
  "limit": 10,
  "offset": 0,
  "data": [
    {
      "id": 1,
      "machine_id": 1,
      "machine_name": "Torno CNC #1",
      "timestamp": "2025-03-26T14:35:22Z",
      "severity": "high",
      "metric": "temperature",
      "value": 78.5,
      "expected_range": {
        "min": 35.0,
        "max": 55.0
      },
      "score": 0.92,
      "description": "Temperatura acima do limite esperado",
      "possible_causes": [
        "Falha no sistema de refrigeração",
        "Sobrecarga de operação",
        "Falha no sensor de temperatura"
      ],
      "recommended_actions": [
        "Verificar sistema de refrigeração",
        "Reduzir carga de trabalho",
        "Calibrar sensor de temperatura"
      ]
    },
    ...
  ]
}
```

#### Obter Previsões de Falhas

Retorna previsões de falhas para máquinas específicas ou todas as máquinas.

- **URL**: `/analytics/predictions`
- **Método**: `GET`
- **Parâmetros de Consulta**:
  - `machine_id` (opcional): Filtrar por ID da máquina
  - `horizon` (opcional): Horizonte de previsão em dias (padrão: 30)
  - `threshold` (opcional): Limiar de probabilidade (0-1, padrão: 0.5)
  - `limit` (opcional): Limitar número de resultados

**Exemplo de Requisição**:
```
GET /api/analytics/predictions?machine_id=1&horizon=14&threshold=0.3
```

**Exemplo de Resposta**:
```json
{
  "machine_id": 1,
  "machine_name": "Torno CNC #1",
  "horizon": 14,
  "threshold": 0.3,
  "predictions": [
    {
      "day": 1,
      "date": "2025-03-27",
      "probability": 0.05,
      "components_at_risk": []
    },
    {
      "day": 2,
      "date": "2025-03-28",
      "probability": 0.08,
      "components_at_risk": []
    },
    ...
    {
      "day": 10,
      "date": "2025-04-05",
      "probability": 0.35,
      "components_at_risk": [
        {
          "name": "Rolamento",
          "probability": 0.62,
          "remaining_life": 240
        },
        {
          "name": "Sistema de Refrigeração",
          "probability": 0.41,
          "remaining_life": 320
        }
      ]
    },
    ...
  ]
}
```

#### Obter Recomendações de Otimização

Retorna recomendações de otimização para máquinas específicas ou todas as máquinas.

- **URL**: `/analytics/optimizations`
- **Método**: `GET`
- **Parâmetros de Consulta**:
  - `machine_id` (opcional): Filtrar por ID da máquina
  - `metric` (opcional): Métrica a ser otimizada (efficiency, energy, quality)
  - `limit` (opcional): Limitar número de resultados

**Exemplo de Requisição**:
```
GET /api/analytics/optimizations?machine_id=1&metric=energy
```

**Exemplo de Resposta**:
```json
{
  "machine_id": 1,
  "machine_name": "Torno CNC #1",
  "metric": "energy",
  "current_value": 4.8,
  "potential_value": 3.9,
  "improvement": 18.75,
  "recommendations": [
    {
      "parameter": "velocidade",
      "current_value": 1200,
      "recommended_value": 1050,
      "impact": 10.5,
      "confidence": 0.85
    },
    {
      "parameter": "temperatura_operacao",
      "current_value": 42.3,
      "recommended_value": 40.0,
      "impact": 5.2,
      "confidence": 0.78
    },
    {
      "parameter": "ciclo_de_trabalho",
      "current_value": 0.85,
      "recommended_value": 0.75,
      "impact": 8.3,
      "confidence": 0.92
    }
  ],
  "estimated_savings": {
    "energy_kwh": 2160,
    "cost": 1080,
    "co2_reduction": 950
  }
}
```

#### Obter Recomendações de Manutenção

Retorna recomendações de manutenção para máquinas específicas ou todas as máquinas.

- **URL**: `/analytics/maintenance`
- **Método**: `GET`
- **Parâmetros de Consulta**:
  - `machine_id` (opcional): Filtrar por ID da máquina
  - `priority` (opcional): Filtrar por prioridade (low, medium, high, critical)
  - `timeframe` (opcional): Período em dias (7, 14, 30, 90)
  - `limit` (opcional): Limitar número de resultados

**Exemplo de Requisição**:
```
GET /api/analytics/maintenance?timeframe=30&priority=high
```

**Exemplo de Resposta**:
```json
{
  "total": 2,
  "timeframe": 30,
  "data": [
    {
      "id": 1,
      "machine_id": 2,
      "machine_name": "Fresadora #2",
      "priority": "high",
      "recommended_date": "2025-04-05",
      "estimated_duration": 6,
      "components": [
        {
          "name": "Bomba Hidráulica",
          "condition": "warning",
          "remaining_life": 820,
          "replacement_recommended": true,
          "replacement_part": "BH-2000",
          "estimated_cost": 1200
        },
        {
          "name": "Válvulas de Controle",
          "condition": "warning",
          "remaining_life": 950,
          "replacement_recommended": false,
          "maintenance_action": "Limpeza e calibração"
        }
      ],
      "impact_if_delayed": {
        "failure_probability": 0.68,
        "downtime_hours": 24,
        "estimated_cost": 4800
      }
    },
    ...
  ]
}
```

### Dados

#### Obter Leituras

Retorna leituras de sensores para todas as máquinas.

- **URL**: `/data/readings`
- **Método**: `GET`
- **Parâmetros de Consulta**:
  - `start_time` (opcional): Timestamp inicial (ISO 8601)
  - `end_time` (opcional): Timestamp final (ISO 8601)
  - `metrics` (opcional): Lista de métricas separadas por vírgula
  - `machine_ids` (opcional): Lista de IDs de máquinas separados por vírgula
  - `interval` (opcional): Intervalo de agregação (1m, 5m, 1h, 1d)
  - `limit` (opcional): Limitar número de resultados

**Exemplo de Requisição**:
```
GET /api/data/readings?start_time=2025-03-26T00:00:00Z&end_time=2025-03-26T23:59:59Z&metrics=temperature,vibration&machine_ids=1,2,3&interval=1h
```

**Exemplo de Resposta**:
```json
{
  "start_time": "2025-03-26T00:00:00Z",
  "end_time": "2025-03-26T23:59:59Z",
  "interval": "1h",
  "metrics": ["temperature", "vibration"],
  "machines": [1, 2, 3],
  "readings": [
    {
      "timestamp": "2025-03-26T00:00:00Z",
      "machines": {
        "1": {
          "temperature": 41.2,
          "vibration": 0.04
        },
        "2": {
          "temperature": 38.5,
          "vibration": 0.06
        },
        "3": {
          "temperature": 40.1,
          "vibration": 0.03
        }
      }
    },
    ...
  ]
}
```

#### Obter Estatísticas

Retorna estatísticas calculadas para métricas específicas.

- **URL**: `/data/statistics`
- **Método**: `GET`
- **Parâmetros de Consulta**:
  - `start_time` (opcional): Timestamp inicial (ISO 8601)
  - `end_time` (opcional): Timestamp final (ISO 8601)
  - `metrics` (opcional): Lista de métricas separadas por vírgula
  - `machine_ids` (opcional): Lista de IDs de máquinas separados por vírgula
  - `group_by` (opcional): Agrupar por (machine, metric, day, week, month)

**Exemplo de Requisição**:
```
GET /api/data/statistics?metrics=temperature,vibration&machine_ids=1,2,3&group_by=machine
```

**Exemplo de Resposta**:
```json
{
  "metrics": ["temperature", "vibration"],
  "machines": [1, 2, 3],
  "group_by": "machine",
  "statistics": {
    "1": {
      "temperature": {
        "min": 35.2,
        "max": 52.8,
        "mean": 42.3,
        "median": 41.9,
        "std_dev": 3.2
      },
      "vibration": {
        "min": 0.02,
        "max": 0.09,
        "mean": 0.05,
        "median": 0.04,
        "std_dev": 0.01
      }
    },
    "2": {
      "temperature": {
        "min": 32.1,
        "max": 48.5,
        "mean": 38.5,
        "median": 38.2,
        "std_dev": 2.8
      },
      "vibration": {
        "min": 0.03,
        "max": 0.12,
        "mean": 0.06,
        "median": 0.05,
        "std_dev": 0.02
      }
    },
    "3": {
      "temperature": {
        "min": 34.5,
        "max": 49.2,
        "mean": 40.1,
        "median": 39.8,
        "std_dev": 3.0
      },
      "vibration": {
        "min": 0.01,
        "max": 0.08,
        "mean": 0.03,
        "median": 0.03,
        "std_dev": 0.01
      }
    }
  }
}
```

#### Obter Tendências

Retorna tendências identificadas para métricas específicas.

- **URL**: `/data/trends`
- **Método**: `GET`
- **Parâmetros de Consulta**:
  - `start_time` (opcional): Timestamp inicial (ISO 8601)
  - `end_time` (opcional): Timestamp final (ISO 8601)
  - `metrics` (opcional): Lista de métricas separadas por vírgula
  - `machine_ids` (opcional): Lista de IDs de máquinas separados por vírgula
  - `limit` (opcional): Limitar número de resultados

**Exemplo de Requisição**:
```
GET /api/data/trends?metrics=temperature,vibration&machine_ids=1,2,3
```

**Exemplo de Resposta**:
```json
{
  "metrics": ["temperature", "vibration"],
  "machines": [1, 2, 3],
  "trends": [
    {
      "machine_id": 1,
      "machine_name": "Torno CNC #1",
      "metric": "temperature",
      "trend": "increasing",
      "rate": 0.5,
      "unit": "°C/dia",
      "confidence": 0.85,
      "period": {
        "start": "2025-03-20T00:00:00Z",
        "end": "2025-03-26T23:59:59Z"
      },
      "significance": "medium",
      "description": "Aumento gradual de temperatura detectado"
    },
    {
      "machine_id": 2,
      "machine_name": "Fresadora #2",
      "metric": "vibration",
      "trend": "increasing",
      "rate": 0.01,
      "unit": "g/dia",
      "confidence": 0.92,
      "period": {
        "start": "2025-03-15T00:00:00Z",
        "end": "2025-03-26T23:59:59Z"
      },
      "significance": "high",
      "description": "Aumento significativo de vibração detectado"
    },
    ...
  ]
}
```

#### Exportar Dados

Exporta dados para formatos específicos.

- **URL**: `/data/export`
- **Método**: `POST`
- **Corpo da Requisição**:
  ```json
  {
    "start_time": "2025-03-01T00:00:00Z",
    "end_time": "2025-03-26T23:59:59Z",
    "metrics": ["temperature", "vibration", "pressure", "power_consumption"],
    "machine_ids": [1, 2, 3],
    "interval": "1h",
    "format": "csv"
  }
  ```

**Exemplo de Resposta**:
```json
{
  "export_id": "exp_12345",
  "status": "processing",
  "estimated_completion": "2025-03-26T19:35:00Z",
  "download_url": "/api/data/export/exp_12345"
}
```

Para baixar o arquivo exportado:
```
GET /api/data/export/exp_12345
```

## Códigos de Status

- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Parâmetros inválidos
- `401 Unauthorized`: Autenticação necessária
- `403 Forbidden`: Acesso negado
- `404 Not Found`: Recurso não encontrado
- `429 Too Many Requests`: Limite de taxa excedido
- `500 Internal Server Error`: Erro interno do servidor

## Autenticação

Para acessar endpoints protegidos, inclua um token JWT no cabeçalho de autorização:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Para obter um token, use o endpoint de autenticação:

- **URL**: `/auth/token`
- **Método**: `POST`
- **Corpo da Requisição**:
  ```json
  {
    "username": "usuario",
    "password": "senha"
  }
  ```

**Exemplo de Resposta**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Limites de Taxa

A API implementa limites de taxa para evitar sobrecarga:

- 100 requisições por minuto por IP
- 1000 requisições por hora por usuário autenticado

Quando o limite é excedido, a API retorna o código de status `429 Too Many Requests`.

## Versionamento

A API é versionada através do prefixo na URL. A versão atual é `v1`.

Para acessar versões específicas:

```
/api/v1/machines
/api/v2/machines
```

## Exemplos de Uso

### Python

```python
import requests
import json

# Configuração
API_BASE_URL = "http://8000-ih0ziztfl2htse6x6jvwh-0cf19b87.manus.computer/api"
TOKEN = "seu_token_jwt"

# Cabeçalhos
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Obter lista de máquinas
response = requests.get(f"{API_BASE_URL}/machines", headers=headers)
machines = response.json()
print(f"Total de máquinas: {machines['total']}")

# Obter detalhes de uma máquina específica
machine_id = 1
response = requests.get(f"{API_BASE_URL}/machines/{machine_id}", headers=headers)
machine = response.json()
print(f"Detalhes da máquina {machine['name']}:")
print(json.dumps(machine, indent=2))

# Obter anomalias de alta severidade
params = {
    "severity": "high",
    "limit": 5
}
response = requests.get(f"{API_BASE_URL}/analytics/anomalies", headers=headers, params=params)
anomalies = response.json()
print(f"Anomalias de alta severidade: {anomalies['total']}")
```

### JavaScript

```javascript
// Configuração
const API_BASE_URL = "http://8000-ih0ziztfl2htse6x6jvwh-0cf19b87.manus.computer/api";
const TOKEN = "seu_token_jwt";

// Cabeçalhos
const headers = {
  "Authorization": `Bearer ${TOKEN}`,
  "Content-Type": "application/json"
};

// Obter lista de máquinas
fetch(`${API_BASE_URL}/machines`, { headers })
  .then(response => response.json())
  .then(data => {
    console.log(`Total de máquinas: ${data.total}`);
    
    // Obter detalhes da primeira máquina
    const machineId = data.data[0].id;
    return fetch(`${API_BASE_URL}/machines/${machineId}`, { headers });
  })
  .then(response => response.json())
  .then(machine => {
    console.log(`Detalhes da máquina ${machine.name}:`);
    console.log(JSON.stringify(machine, null, 2));
    
    // Obter leituras da máquina
    const params = new URLSearchParams({
      start_time: "2025-03-26T00:00:00Z",
      end_time: "2025-03-26T23:59:59Z",
      metrics: "temperature,vibration",
      interval: "1h"
    });
    
    return fetch(`${API_BASE_URL}/machines/${machine.id}/readings?${params}`, { headers });
  })
  .then(response => response.json())
  .then(readings => {
    console.log(`Leituras obtidas: ${readings.readings.length}`);
  })
  .catch(error => console.error("Erro:", error));
```

## Considerações Finais

Esta documentação cobre os principais endpoints da API do Sistema de Análise de Máquinas Industriais com Indústria 4.0. Para informações adicionais ou suporte, entre em contato com a equipe de desenvolvimento.

---

© 2025 Industrial Analytics. Todos os direitos reservados.
