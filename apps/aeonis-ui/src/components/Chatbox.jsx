import { useState } from 'react';

const Chatbox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { sender: 'user', text: input }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8001/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ message: input }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An error occurred.');
      }

      const data = await response.json();
      setMessages([...newMessages, { sender: 'ai', text: data.response }]);
    } catch (e) {
      setError(e.message);
      setMessages([...newMessages, { sender: 'ai', text: `Error: ${e.message}`, isError: true }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg h-[70vh] flex flex-col">
      <h2 className="text-2xl font-semibold mb-4 border-b-2 border-gray-700 pb-2">AI Chat</h2>
      <div className="flex-grow overflow-y-auto mb-4 pr-2">
        <div className="space-y-4">
          {messages.map((msg, index) => (
            <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`p-3 rounded-lg max-w-lg ${
                  msg.sender === 'user'
                    ? 'bg-indigo-600 text-white'
                    : msg.isError
                    ? 'bg-red-800 text-red-100'
                    : 'bg-gray-700 text-white'
                }`}
              >
                <p style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="p-3 rounded-lg bg-gray-700 text-white">
                <p>Thinking...</p>
              </div>
            </div>
          )}
        </div>
      </div>
      {error && !loading && (
        <div className="text-red-400 mb-2">
          <p>Could not get a response. Please try again.</p>
        </div>
      )}
      <div className="flex items-center border-t-2 border-gray-700 pt-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !loading && handleSend()}
          placeholder="Ask a question about your traces..."
          className="flex-grow bg-gray-700 text-white placeholder-gray-500 p-3 rounded-md border-2 border-gray-600 focus:border-indigo-500 focus:ring-indigo-500 transition"
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-900 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-md transition ml-4"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default Chatbox;
