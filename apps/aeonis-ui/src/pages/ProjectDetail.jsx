import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import TraceDetailView from '../components/TraceDetailView';
import Chatbox from '../components/Chatbox';

function ProjectDetail() {
  const { projectId } = useParams();
  const [traces, setTraces] = useState([]);
  const [selectedTrace, setSelectedTrace] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTraces = async () => {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    setTraces([]);
    setSelectedTrace(null);

    try {
      const response = await fetch(`http://localhost:8000/v1/projects/${projectId}/traces`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const tracesById = data.reduce((acc, span) => {
        if (!acc[span.trace_id]) acc[span.trace_id] = [];
        acc[span.trace_id].push(span);
        return acc;
      }, {});
      const traceList = Object.values(tracesById).map(spans => spans.find(s => !s.parent_span_id) || spans[0]);
      setTraces(traceList);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchTraceDetails = async (traceId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/v1/traces/${traceId}`);
      if (!response.ok) throw new Error('Failed to fetch trace details');
      const data = await response.json();
      setSelectedTrace(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchTraces();
  }, [projectId]);

  return (
    <div className="bg-gray-900 text-white min-h-screen font-sans p-8">
      <div className="max-w-8xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-indigo-400">Project Dashboard</h1>
          <p className="text-lg text-gray-500">{projectId}</p>
          <Link to="/projects" className="text-indigo-400 hover:underline">← Back to All Projects</Link>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Trace Visualization */}
          <div>
            {error && (
              <div className="bg-red-800 p-3 rounded-lg mb-4" role="alert">
                <strong>Error:</strong> {error}
              </div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="md:col-span-1 bg-gray-800 p-6 rounded-lg shadow-lg">
                <h2 className="text-2xl font-semibold mb-4">Traces</h2>
                <button onClick={fetchTraces} disabled={loading} className="w-full mb-4 bg-indigo-600 py-2 rounded-md">
                  {loading ? 'Refreshing...' : 'Refresh Traces'}
                </button>
                <div className="space-y-2 h-[60vh] overflow-y-auto">
                  {traces.map((trace) => (
                    <div key={trace.trace_id} onClick={() => fetchTraceDetails(trace.trace_id)} className="p-3 bg-gray-700 rounded-md cursor-pointer hover:bg-indigo-500">
                      <p className="font-bold truncate">{trace.name}</p>
                      <p className="text-sm text-gray-400">{new Date(trace.start_time).toLocaleString()}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div className="md:col-span-2 bg-gray-800 p-6 rounded-lg shadow-lg">
                <h2 className="text-2xl font-semibold mb-4">Selected Trace Details</h2>
                <div className="h-[60vh] overflow-y-auto">
                  {selectedTrace ? <TraceDetailView spans={selectedTrace} /> : <p>Select a trace to see details.</p>}
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: AI Chatbox */}
          <div>
            <Chatbox projectId={projectId} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProjectDetail;
