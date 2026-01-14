import React from 'react'

export default function PipelineCard({pipeline}){
  return (
    <div className="p-4 bg-slate-900 rounded shadow-neon-glow">
      <h3 className="text-lg text-neon">{pipeline.name}</h3>
      <p className="text-slate-400 text-sm">{pipeline.description}</p>
    </div>
  )
}
