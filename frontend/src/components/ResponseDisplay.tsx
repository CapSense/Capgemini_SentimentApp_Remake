// Hey AJ, this is your place to paste your code for the AI-response box.
// ResponseDisplay.tsx: This component will display the AI-generated Phi-3 model response with a "Copy" button and handle API calls.


/*
note for myself from AI: Yes, that could very well be the reason. If the ResponseDisplay.tsx file is currently blank or does not
contain a default export, you will encounter the "has no default export" error when trying to import it
in your WebApp.tsx file. SO IGNORE ERROR. actually dummy code is below, otherwise you cant run dev environment
 */

import React from 'react';

interface Result {
  response: string;
}

interface Props {
  results: Result[];
}

const ResponseDisplay: React.FC<Props> = ({ results }) => {
  // Handle case where results is empty
  if (!results || results.length === 0) {
    return (
      <div className="mt-4 p-3 border rounded">
        <p className="text-muted">AI-generated response will appear here</p>
      </div>
    );
  }

  // Display all results (responses)
  return (
    <div className="mt-4">
      <h5>AI-generated response:</h5>
      {results.map((result, index) => (
        <div key={index} className="p-3 border rounded mb-2">
          <p>{result.response}</p>
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
