import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function ProjectsList() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await fetch('http://localhost:8000/v1/projects');
        if (!response.ok) {
          throw new Error('Failed to fetch projects');
        }
        const data = await response.json();
        setProjects(data);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    fetchProjects();
  }, []);

  return (
    <div className="bg-gray-900 text-white min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center text-indigo-400 mb-8">Available Projects</h1>
        
        {loading && <p className="text-center">Loading projects...</p>}
        {error && <p className="text-red-400 text-center">{error}</p>}

        {!loading && !error && (
          <div className="space-y-4">
            {projects.map(project => (
              <Link 
                key={project.id} 
                to={`/projects/${project.id}`}
                className="block bg-gray-800 p-6 rounded-lg shadow-lg hover:bg-indigo-900 transition"
              >
                <h2 className="text-2xl font-bold text-indigo-400">{project.name}</h2>
                <p className="text-gray-500 break-all">ID: {project.id}</p>
              </Link>
            ))}
          </div>
        )}
        <div className="mt-8 text-center">
          <Link to="/" className="text-indigo-400 hover:underline">← Back to Home</Link>
        </div>
      </div>
    </div>
  );
}

export default ProjectsList;
