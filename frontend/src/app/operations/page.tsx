"use client";

import React, { useState, useEffect } from "react";

export default function OperationsCenter() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    // In production, this hits /api/v1/enterprise/operations/health
    setHealth({
      status: "healthy",
      regions: { "us-east-1": "healthy", "eu-central-1": "healthy" },
      redis_cluster: "connected",
      event_store: "writable",
      active_agents: 142,
      pending_sagas: 12
    });
  }, []);

  if (!health) return <div className="p-8 text-white">Loading Enterprise State...</div>;

  return (
    <div className="p-8 bg-slate-900 min-h-screen text-slate-100 font-sans">
      <header className="mb-8 border-b border-slate-700 pb-4">
        <h1 className="text-3xl font-bold text-white">Global Operations Center</h1>
        <p className="text-slate-400 mt-2">CHAYA v1.0 Multi-Region Dashboard</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* KPI Cards */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-sm">
          <h3 className="text-slate-400 text-sm font-medium">Global Health</h3>
          <div className="mt-2 flex items-center">
            <span className="h-3 w-3 rounded-full bg-emerald-500 mr-2"></span>
            <span className="text-2xl font-bold text-emerald-400">HEALTHY</span>
          </div>
        </div>

        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-sm">
          <h3 className="text-slate-400 text-sm font-medium">Active Agents</h3>
          <div className="mt-2 text-2xl font-bold text-blue-400">{health.active_agents}</div>
        </div>

        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-sm">
          <h3 className="text-slate-400 text-sm font-medium">Redis Cluster</h3>
          <div className="mt-2 text-2xl font-bold text-purple-400">CONNECTED</div>
        </div>

        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-sm">
          <h3 className="text-slate-400 text-sm font-medium">Suspended Sagas</h3>
          <div className="mt-2 text-2xl font-bold text-amber-400">{health.pending_sagas}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Region Map Mock */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
          <h3 className="text-lg font-bold mb-4">Multi-Region Deployments</h3>
          <ul className="space-y-4">
            {Object.entries(health.regions).map(([region, status]) => (
              <li key={region} className="flex justify-between items-center p-3 bg-slate-900 rounded border border-slate-700">
                <span className="font-mono">{region}</span>
                <span className="text-emerald-400 font-bold uppercase">{String(status)}</span>
              </li>
            ))}
          </ul>
        </div>
        
        {/* Recent Domain Events */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
          <h3 className="text-lg font-bold mb-4">Live Event Store Ledger</h3>
          <div className="space-y-3 font-mono text-sm">
            <div className="text-blue-400">[us-east-1] ToolExecutionCompleted: Salesforce.create_case</div>
            <div className="text-emerald-400">[eu-central-1] AgentSpawned: RESEARCHER</div>
            <div className="text-purple-400">[us-east-1] WorkflowSuspended: Saga_881</div>
            <div className="text-red-400">[eu-central-1] SecurityAlertRaised: Failed MFA attempt</div>
            <div className="text-blue-400">[us-east-1] SemanticCacheHit: latency_saved=420ms</div>
          </div>
        </div>
      </div>
    </div>
  );
}
