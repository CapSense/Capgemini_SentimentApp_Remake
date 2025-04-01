import React, { useState } from 'react'
import axios from 'axios'
import EmotionDetector from './EmotionDetector'

interface AnalysisResponse {
  classification?: {
    sentiment?: string
    sentiment_confidence?: number
    sarcasm?: boolean
    sarcasm_confidence?: number
    emotion?: string
    emotion_confidence?: number
  }
  ai_response?: {
    response_text?: string
    empathy_score?: number
  }
}

// A single result object after analyzing text
interface SingleResult {
  inputText: string
  classification?: string
  response?: string
}

const WebApp: React.FC = () => {
  const [text, setText] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [results, setResults] = useState<AnalysisResponse[]>([])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setFile(e.target.files[0])
  }

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault()

    // If user uploaded a file, parse it and do batch
    if (file) {
      const reader = new FileReader()
      reader.onload = async (ev) => {
        const textContent = ev.target?.result as string
        try {
          let messages: string[] = []
          if (file.name.endsWith('.csv')) {
            // Very simple CSV parsing, first column only
            const rows = textContent
              .split('\n')
              .map((row) => row.split(',')[0].replace(/"/g, '').trim())
              .filter((row) => row)
            messages = rows
          } else if (file.name.endsWith('.json')) {
            // JSON array of objects or strings
            const jsonData = JSON.parse(textContent)
            // Expect each item has .message or is a string
            messages = jsonData.map((item: any) => item.message || item)
          }

          // Now call /api/respond_batch
          // We'll do it in a single request:
          const batchPayload = { customer_texts: messages }
          const batchResp = await axios.post<AnalysisResponse[]>(
            'http://localhost:5000/api/respond_batch',
            batchPayload
          )
          setResults(batchResp.data)
        } catch (error) {
          console.error('Error parsing file or batch request:', error)
        }
      }
      reader.readAsText(file)
    } else if (text) {
      // Single text approach
      const payload = { customer_text: text }
      try {
        const resp = await axios.post<AnalysisResponse>(
          'http://localhost:5000/api/respond',
          payload
        )
        setResults([resp.data]) // store single result as array
      } catch (error) {
        console.error('Error sending single text request:', error)
      }
    }
  }

  return (
    <div className="row">
      <div className="col-md-6">
        <form onSubmit={handleAnalyze}>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste or upload feedback"
            className="form-control mb-2"
            rows={5}
          />
          <input
            type="file"
            accept=".csv,.json"
            onChange={handleFileChange}
            className="form-control mb-2"
          />
          <button type="submit" className="btn btn-success">
            Analyze & Generate
          </button>
        </form>

        <div className="mt-3">
          <h5>AI-generated response:</h5>
          {results.map((r, i) => (
            <p key={i}>
              {r.ai_response?.response_text ?? 'No response yet'}
            </p>
          ))}
        </div>

        {/* If you have an endpoint for exporting results: */}
        <button
          onClick={() => axios.get('http://localhost:5000/export-results')}
          className="btn btn-secondary mt-2"
        >
          Export to Power BI
        </button>
        <button className="btn btn-primary mt-2">Approve &amp; Send</button>
      </div>

      <div className="col-md-6">
        <h4>Sentiment Analysis Report</h4>
        {results.map((r, i) => {
          const c = r.classification
          return (
            <div key={i}>
              <p>Sentiment: {c?.sentiment} (conf: {c?.sentiment_confidence})</p>
              <p>Sarcasm: {c?.sarcasm ? 'Yes' : 'No'} (conf: {c?.sarcasm_confidence})</p>
              <p>Emotion: {c?.emotion} (conf: {c?.emotion_confidence})</p>
              <p>Empathy Score: {r.ai_response?.empathy_score}</p>
              <EmotionDetector emotion={c?.emotion || ''} />
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default WebApp
