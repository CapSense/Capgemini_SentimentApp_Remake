import React, { useState, useEffect } from 'react'

function Dashboard() {
  const [entries, setEntries] = useState([])

  useEffect(() => {
    async function fetchData() {
      try {
        const resp = await fetch('http://localhost:5000/api/dashboard')
        const data = await resp.json()
        setEntries(data)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      }
    }
    fetchData()
  }, [])

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Dashboard</h2>
      {entries.map((item, index) => (
        <div key={index} style={{ marginBottom: '1rem' }}>
          <p><strong>Customer Text:</strong> {item.customer_text}</p>
          <p><strong>Sentiment:</strong> {item.sentiment}</p>
          <p><strong>Response:</strong> {item.response_text}</p>
          <p><strong>F1 Score:</strong> {item.f1_score}</p>
          <p><strong>Created At:</strong> {item.created_at}</p>
          <hr />
        </div>
      ))}
    </div>
  )
}

export default Dashboard
