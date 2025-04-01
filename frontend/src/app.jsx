import React, { useState } from 'react'

function App() {
  const [customerText, setCustomerText] = useState('')
  const [responseData, setResponseData] = useState(null)

  const handleSend = async () => {
    try {
      const resp = await fetch('http://localhost:5000/api/respond', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_text: customerText })
      })
      const data = await resp.json()
      setResponseData(data)
    } catch (error) {
      console.error('Error sending data:', error)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'row', height: '100vh' }}>
      {/* Left side: text area for user input */}
      <div style={{ flex: 1, padding: '1rem', borderRight: '1px solid #ccc' }}>
        <h2>Input Customer Feedback</h2>
        <textarea
          rows="10"
          style={{ width: '100%' }}
          value={customerText}
          onChange={e => setCustomerText(e.target.value)}
        />
        <br />
        <button onClick={handleSend}>Approve &amp; Send</button>
      </div>

      {/* Right side: analysis results */}
      <div style={{ flex: 1, padding: '1rem' }}>
        <h2>Analysis &amp; Response</h2>
        {responseData ? (
          <div>
            <p><strong>Detected Sentiment:</strong> {responseData.sentiment_results?.sentiment}</p>
            <p><strong>Confidence:</strong> {responseData.sentiment_results?.confidence}</p>
            <p><strong>F1 Score:</strong> {responseData.f1_score}</p>
            <p><strong>AI Response:</strong> {responseData.ai_response?.response_text}</p>
            <p><strong>Empathy Score:</strong> {responseData.ai_response?.empathy_score}</p>
          </div>
        ) : (
          <p>No analysis yet.</p>
        )}
      </div>
    </div>
  )
}

export default App
