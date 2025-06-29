import { useState } from 'react';

function App() {
  const [projectId, setProjectId] = useState('');
  const [traces, setTraces] = useState([]);
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

    try {
      // IMPORTANT: Replace with the actual URL of your Aeonis server
      const response = await fetch(`http://localhost:8000/v1/traces/projects/${projectId}/traces`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setTraces(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 text-white min-h-screen font-sans p-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-12 text-center">
          <h1 className="text-5xl font-bold text-indigo-400 mb-2">Aeonis</h1>
        </header>

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

        <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold mb-4 border-b-2 border-gray-700 pb-2">Results</h2>
          {traces.length > 0 ? (
            <pre className="bg-gray-900 p-4 rounded-md overflow-x-auto">
              {JSON.stringify(traces, null, 2)}
            </pre>
          ) : (
            <p className="text-gray-500">No traces to display. Enter a Project ID and click "Fetch Traces".</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
