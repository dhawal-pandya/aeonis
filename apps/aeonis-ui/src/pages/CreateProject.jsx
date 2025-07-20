import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function CreateProject() {
  const [projectName, setProjectName] = useState('');
  const [repoUrl, setRepoUrl] = useState('');
  const [isPrivate, setIsPrivate] = useState(false);
  const [sshKey, setSshKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleCreate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const body = {
      name: projectName,
      git_repo_url: repoUrl,
      is_private: isPrivate,
      git_ssh_key: isPrivate ? sshKey : null,
    };

    try {
      const response = await fetch('http://localhost:8000/v1/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create project');
      }
      const data = await response.json();
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 text-white min-h-screen flex flex-col items-center justify-center p-8">
      <div className="w-full max-w-2xl">
        <h1 className="text-4xl font-bold text-center text-indigo-400 mb-8">Create a New Aeonis Project</h1>
        
        {!result ? (
          <form onSubmit={handleCreate} className="bg-gray-800 p-8 rounded-lg shadow-lg">
            <div className="mb-6">
              <label htmlFor="projectName" className="block text-lg font-medium text-gray-300 mb-2">Project Name</label>
              <input
                id="projectName"
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="e.g., My Awesome App"
                required
                className="w-full bg-gray-700 text-white p-3 rounded-md border-2 border-gray-600 focus:border-indigo-500"
              />
            </div>
            <div className="mb-6">
              <label htmlFor="repoUrl" className="block text-lg font-medium text-gray-300 mb-2">Git Repository URL (Optional)</label>
              <input
                id="repoUrl"
                type="text"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="e.g., https://github.com/my-org/my-repo.git"
                className="w-full bg-gray-700 text-white p-3 rounded-md border-2 border-gray-600 focus:border-indigo-500"
              />
            </div>

            {/* Private Repo Accordion */}
            <div className="bg-gray-700 rounded-lg p-4 mb-8">
                <div className="flex items-center">
                    <input
                        id="isPrivate"
                        type="checkbox"
                        checked={isPrivate}
                        onChange={(e) => setIsPrivate(e.target.checked)}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-500 rounded"
                    />
                    <label htmlFor="isPrivate" className="ml-3 block text-lg font-medium text-gray-300">
                        This is a private repository
                    </label>
                </div>
                {isPrivate && (
                    <div className="mt-4">
                        <label htmlFor="sshKey" className="block text-lg font-medium text-gray-300 mb-2">SSH Private Key</label>
                        <p className="text-sm text-gray-400 mb-2">Provide the SSH private key to allow Aeonis to clone your repository. The key will be stored securely.</p>
                        <textarea
                            id="sshKey"
                            value={sshKey}
                            onChange={(e) => setSshKey(e.target.value)}
                            placeholder="Begins with -----BEGIN OPENSSH PRIVATE KEY-----"
                            required={isPrivate}
                            className="w-full bg-gray-600 text-white p-3 rounded-md border-2 border-gray-500 focus:border-indigo-500 h-48 font-mono"
                        />
                    </div>
                )}
            </div>

            <button type="submit" disabled={loading} className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg text-lg">
              {loading ? 'Creating...' : 'Create Project'}
            </button>
          </form>
        ) : (
          <div className="bg-gray-800 p-8 rounded-lg shadow-lg text-center">
            <h2 className="text-3xl font-bold text-green-400 mb-6">Project Created Successfully!</h2>
            <div className="text-left space-y-4">
              <div>
                <p className="text-lg font-medium text-gray-300">Project ID:</p>
                <code className="block bg-gray-700 p-3 rounded-md text-indigo-300 text-lg break-all">{result.id}</code>
              </div>
              <div>
                <p className="text-lg font-medium text-gray-300">API Key:</p>
                <p className="text-sm text-gray-500 mb-1">Use this key in the `X-Aeonis-API-Key` header of your SDK.</p>
                <code className="block bg-gray-700 p-3 rounded-md text-indigo-300 text-lg break-all">{result.api_key}</code>
              </div>
            </div>
          </div>
        )}

        {error && <p className="text-red-400 mt-4 text-center">{error}</p>}

        <div className="mt-8 text-center">
          <Link to="/" className="text-indigo-400 hover:underline">← Back to Home</Link>
        </div>
      </div>
    </div>
  );
}

export default CreateProject;
