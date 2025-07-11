import { useState } from 'react';
import TraceDetailView from './components/TraceDetailView';
import Chatbox from './components/Chatbox';

function App() {
  const [projectId, setProjectId] = useState('9df1c007-08e0-45fb-ad99-2471f672a4bc'); // Default for convenience
  const [traces, setTraces] = useState([]);
  const [selectedTrace, setSelectedTrace] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTraces = async () => {
    if (!projectId) {
      setError('Please enter a Project ID.');
      return;
    }
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
        if (!acc[span.trace_id]) {
          acc[span.trace_id] = [];
        }
        acc[span.trace_id].push(span);
        return acc;
      }, {});
      const traceList = Object.values(tracesById).map(spans => {
        const rootSpan = spans.find(s => !s.parent_span_id);
        return rootSpan || spans[0];
      });
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
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSelectedTrace(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 text-white min-h-screen font-sans p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-12 text-center">
          <h1 className="text-5xl font-bold text-indigo-400 mb-2">Aeonis</h1>
          <p className="text-xl text-gray-400">AI-Powered Observability</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Trace Visualization */}
          <div>
            <div className="bg-gray-800 p-6 rounded-lg shadow-lg mb-8">
              <div className="flex items-center space-x-4">
                <input
                  type="text"
                  value={projectId}
                  onChange={(e) => setProjectId(e.target.value)}
                  placeholder="Enter Project ID"
                  className="flex-grow bg-gray-700 text-white placeholder-gray-500 p-3 rounded-md border-2 border-gray-600 focus:border-indigo-500 focus:ring-indigo-500 transition"
                />
                <button
                  onClick={fetchTraces}
                  disabled={loading}
                  className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-900 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-md transition"
                >
                  {loading ? 'Loading...' : 'Fetch Traces'}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-800 border border-red-600 text-red-100 px-4 py-3 rounded-lg relative mb-6" role="alert">
                <strong className="font-bold">Error: </strong>
                <span className="block sm:inline">{error}</span>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="md:col-span-1 bg-gray-800 p-6 rounded-lg shadow-lg">
                <h2 className="text-2xl font-semibold mb-4 border-b-2 border-gray-700 pb-2">Traces</h2>
                <div className="space-y-2 h-[40vh] overflow-y-auto">
                  {traces.map((trace) => (
                    <div
                      key={trace.trace_id}
                      onClick={() => fetchTraceDetails(trace.trace_id)}
                      className="p-3 bg-gray-700 rounded-md cursor-pointer hover:bg-indigo-500 transition"
                    >
                      <p className="font-bold truncate">{trace.name}</p>
                      <p className="text-sm text-gray-400">{new Date(trace.start_time).toLocaleString()}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="md:col-span-2 bg-gray-800 p-6 rounded-lg shadow-lg">
                <h2 className="text-2xl font-semibold mb-4 border-b-2 border-gray-700 pb-2">Selected Trace Details</h2>
                <div className="h-[40vh] overflow-y-auto">
                  {selectedTrace ? (
                    <TraceDetailView spans={selectedTrace} />
                  ) : (
                    <p className="text-gray-500">Select a trace to see details.</p>
                  )}
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

export default App;
