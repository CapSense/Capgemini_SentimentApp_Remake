import React from 'react';

interface Result {
  response: string;
  originalText: string;
}

interface Props {
  results: Result[];
}

const ResponseDisplay: React.FC<Props> = ({ results }) => {
  if (!results || results.length === 0) {
    return (
      <div className="mt-4 p-3 border rounded bg-white">
        <p className="text-muted">AI-generated response will appear here</p>
      </div>
    );
  }

  return (
    <div className="mt-4">
      <h5>All AI-generated responses:</h5>
      {results.map((result, index) => (
        <div key={index} className="p-3 border rounded mb-3 bg-white">
          <strong>Feedback {index + 1}</strong>
          <p className="mb-1"><em>User said:</em> {result.originalText}</p>
          <p><em>AI Response:</em> {result.response}</p>
          <button
            className="btn btn-sm btn-outline-secondary"
            onClick={() => navigator.clipboard.writeText(result.response)}
          >
            Copy
          </button>
        </div>
      ))}
    </div>
  );
};

export default ResponseDisplay;