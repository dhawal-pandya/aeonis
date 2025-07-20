import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="bg-gray-900 text-white min-h-screen flex flex-col items-center justify-center font-sans p-8">
      <div className="text-center">
        <header className="mb-12">
          <h1 className="text-6xl font-bold text-indigo-400 mb-4">Welcome to Aeonis</h1>
          <p className="text-2xl text-gray-400">The future of AI-Powered Observability and DevSecOps</p>
        </header>

        <main className="max-w-4xl mx-auto mb-12">
          <p className="text-lg text-gray-300 leading-relaxed">
            Aeonis is a next-generation observability platform that goes beyond traditional monitoring. It links your runtime trace data directly to your source code, enabling an AI-powered assistant to answer complex questions about performance, security, and code quality. Understand the impact of every commit, debug issues with natural language, and gain deep insights into your application's behavior.
          </p>
        </main>

        <footer className="flex items-center justify-center space-x-6">
          <Link to="/projects/new" className="bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-8 rounded-lg text-xl transition">
            Create New Project
          </Link>
          <Link to="/projects" className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 px-8 rounded-lg text-xl transition">
            View Existing Projects
          </Link>
        </footer>
      </div>
    </div>
  );
}

export default Home;
