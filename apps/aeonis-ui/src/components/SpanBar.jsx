import React, { useState } from 'react';

const SpanBar = ({ span, totalDuration, minStartTime, depth }) => {
  const [isHovered, setIsHovered] = useState(false);

  const startTime = new Date(span.start_time).getTime();
  const endTime = new Date(span.end_time).getTime();
  const duration = endTime - startTime;

  const leftOffset = ((startTime - minStartTime) / totalDuration) * 100;
  const barWidth = (duration / totalDuration) * 100;

  // Simple color coding based on span name
  const getColor = () => {
    if (span.name.includes('db') || span.name.includes('query')) return 'bg-teal-500';
    if (span.name.includes('http') || span.name.includes('request')) return 'bg-sky-500';
    if (span.error) return 'bg-red-500';
    return 'bg-indigo-500';
  };

  return (
    <div 
      className="relative my-1 p-2 rounded-md transition-all ease-in-out duration-200"
      style={{ marginLeft: `${depth * 20}px` }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex justify-between items-center mb-1">
        <span className="font-mono text-sm truncate">{span.name}</span>
        <span className="text-xs text-gray-400 font-mono">{duration.toFixed(2)}ms</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-4">
        <div
          className={`h-4 rounded-full ${getColor()}`}
          style={{
            marginLeft: `${leftOffset}%`,
            width: `${barWidth}%`,
          }}
        />
      </div>
      {isHovered && (
        <div className="absolute z-10 mt-2 p-3 bg-gray-800 border border-gray-600 rounded-lg shadow-xl text-xs w-auto">
          <p><strong className="text-indigo-400">Span ID:</strong> {span.span_id}</p>
          <p><strong className="text-indigo-400">Trace ID:</strong> {span.trace_id}</p>
          <p><strong className="text-indigo-400">Start:</strong> {new Date(span.start_time).toISOString()} ({startTime}ms)</p>
          <p><strong className="text-indigo-400">End:</strong> {new Date(span.end_time).toISOString()} ({endTime}ms)</p>
          {span.parent_span_id && <p><strong className="text-indigo-400">Parent:</strong> {span.parent_span_id}</p>}
          {span.attributes && <pre className="mt-2 bg-gray-900 p-2 rounded overflow-auto">{JSON.stringify(span.attributes, null, 2)}</pre>}
          {span.error && <pre className="mt-2 bg-red-900 p-2 rounded text-red-200">{JSON.stringify(span.error, null, 2)}</pre>}
        </div>
      )}
    </div>
  );
};

export default SpanBar;
