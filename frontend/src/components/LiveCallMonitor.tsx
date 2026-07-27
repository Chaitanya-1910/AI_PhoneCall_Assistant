"use client";

import React, { useEffect, useState } from "react";

interface SpeechSegment {
  speaker: "CALLER" | "AI";
  text: string;
  timestamp: string;
  emotion?: string;
}

export default function LiveCallMonitor({ sessionId }: { sessionId: string }) {
  const [segments, setSegments] = useState<SpeechSegment[]>([]);

  useEffect(() => {
    // In production, this connects to a WebSocket provided by the Dashboard Service
    const ws = new WebSocket(`ws://localhost:8000/api/v1/monitor/${sessionId}`);
    
    ws.onmessage = (event) => {
      const newSegment = JSON.parse(event.data);
      setSegments((prev) => [...prev, newSegment]);
    };

    return () => ws.close();
  }, [sessionId]);

  return (
    <div className="flex flex-col h-full bg-slate-900 text-white p-4 rounded-xl shadow-lg border border-slate-700">
      <h2 className="text-xl font-bold mb-4">Live Call: {sessionId}</h2>
      
      <div className="flex-1 overflow-y-auto space-y-4">
        {segments.map((seg, idx) => (
          <div 
            key={idx} 
            className={`flex flex-col max-w-[80%] ${seg.speaker === "CALLER" ? "self-end items-end" : "self-start items-start"}`}
          >
            <span className="text-xs text-slate-400 mb-1">
              {seg.speaker} {seg.emotion && `• [${seg.emotion}]`}
            </span>
            <div className={`p-3 rounded-lg ${seg.speaker === "CALLER" ? "bg-blue-600" : "bg-slate-700"}`}>
              {seg.text}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
