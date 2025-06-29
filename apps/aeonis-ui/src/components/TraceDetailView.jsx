import React from 'react';
import SpanBar from './SpanBar';

const TraceDetailView = ({ spans }) => {
  if (!spans || spans.length === 0) {
    return <p className="text-gray-500">No spans to display for this trace.</p>;
  }

  // 1. Find the root span and calculate total duration
  let rootSpan = null;
  let minStartTime = new Date(spans[0].start_time).getTime();
  let maxEndTime = new Date(spans[0].end_time).getTime();

  spans.forEach(span => {
    const startTime = new Date(span.start_time).getTime();
    const endTime = new Date(span.end_time).getTime();
    if (startTime < minStartTime) minStartTime = startTime;
    if (endTime > maxEndTime) maxEndTime = endTime;
    if (!span.parent_span_id) {
      rootSpan = span;
    }
  });

  const totalDuration = maxEndTime - minStartTime;

  // 2. Build a tree structure from the flat list of spans
  const spanMap = new Map(spans.map(s => [s.span_id, { ...s, children: [] }]));
  const tree = [];

  spanMap.forEach(span => {
    if (span.parent_span_id && spanMap.has(span.parent_span_id)) {
      spanMap.get(span.parent_span_id).children.push(span);
    } else {
      tree.push(span); // This will be the root span(s)
    }
  });

  // 3. Render the tree recursively
  const renderSpanTree = (span, depth) => {
    return (
      <div key={span.span_id}>
        <SpanBar span={span} totalDuration={totalDuration} minStartTime={minStartTime} depth={depth} />
        {span.children.sort((a, b) => new Date(a.start_time) - new Date(b.start_time)).map(child => renderSpanTree(child, depth + 1))}
      </div>
    );
  };

  return (
    <div>
      <h3 className="text-lg font-semibold mb-2">Trace Waterfall</h3>
      <div className="bg-gray-900 p-4 rounded-md">
        {tree.sort((a, b) => new Date(a.start_time) - new Date(b.start_time)).map(root => renderSpanTree(root, 0))}
      </div>
    </div>
  );
};

export default TraceDetailView;
