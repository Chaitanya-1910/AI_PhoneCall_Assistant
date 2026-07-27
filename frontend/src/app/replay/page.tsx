"use client";

import React from "react";

export default function ReplayDashboard() {
  return (
    <div className="p-6 bg-slate-900 min-h-screen text-slate-100">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">Event Replay Engine</h1>
        <p className="text-slate-400">Reconstruct past calls precisely from the Event Store ledger.</p>
      </header>

      <div className="grid grid-cols-3 gap-6">
        {/* Timeline View */}
        <div className="col-span-1 bg-slate-800 p-4 rounded-lg border border-slate-700">
          <h3 className="font-semibold mb-4 text-blue-400">Event Timeline</h3>
          <ul className="space-y-3 text-sm">
            <li className="flex justify-between border-l-2 border-emerald-500 pl-3">
              <span>TranscriptReceived</span>
              <span className="text-slate-500">12:00:01</span>
            </li>
            <li className="flex justify-between border-l-2 border-blue-500 pl-3">
              <span>IntentDetected (CALLBACK)</span>
              <span className="text-slate-500">12:00:02</span>
            </li>
            <li className="flex justify-between border-l-2 border-purple-500 pl-3">
              <span>GoalCreated (COLLECT_PHONE)</span>
              <span className="text-slate-500">12:00:02</span>
            </li>
          </ul>
        </div>

        {/* State Reconstruction View */}
        <div className="col-span-2 bg-slate-800 p-4 rounded-lg border border-slate-700">
          <h3 className="font-semibold mb-4 text-emerald-400">Reconstructed Aggregate State</h3>
          <pre className="bg-slate-950 p-4 rounded text-xs text-green-400 overflow-x-auto">
{`{
  "session_id": "call_998x",
  "active_goals": [
    {
      "id": "goal_1",
      "description": "COLLECT_PHONE",
      "status": "PENDING"
    }
  ],
  "caller_emotion": "NEUTRAL",
  "knowledge_graph": {
    "nodes": [...]
  }
}`}
          </pre>
        </div>
      </div>
    </div>
  );
}
