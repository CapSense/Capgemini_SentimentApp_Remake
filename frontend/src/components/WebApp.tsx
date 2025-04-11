import { useState } from 'react';
import axios from 'axios';
import EmotionDetector from './EmotionDetector';
import SarcasmDetector from './SarcasmDetector';
import ClassificationDetector from './ClassificationDetector';
import AspectsDetector from './AspectsDetector';
import ResponseDisplay from './ResponseDisplay';
import '../WebApp.css';

interface AnalysisResponse {
  emotion: string;
  sarcasm: string;
  aspects: string;
  classification: string;
  response: string;
  originalText: string;
}

interface ApiResponse {
  classification: {
    sentiment: string;
    sentiment_confidence: number;
    sarcasm: boolean;
    sarcasm_confidence: number;
    emotion: string;
    emotion_confidence: number;
  };
  ai_response: {
    response_text: string;
    empathy_score: number;
  };
}

const WebApp: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<AnalysisResponse[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [csvContent, setCsvContent] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setFile(e.target.files[0]);
    setError(null);
  };

  const mapToAnalysisResponse = (apiResponse: ApiResponse, originalText: string): AnalysisResponse => {
    return {
      emotion: apiResponse.classification.emotion,
      sarcasm: apiResponse.classification.sarcasm ? 'Detected' : 'Not Detected',
      aspects: `Confidence: ${(apiResponse.classification.sentiment_confidence * 100).toFixed(0)}%`,
      classification: apiResponse.classification.sentiment.toLowerCase(),
      response: apiResponse.ai_response.response_text,
      originalText: originalText
    };
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    const messages: string[] = [];

    try {
      if (file) {
        const reader = new FileReader();
        reader.onload = async (e) => {
          const text = e.target?.result as string;
          setCsvContent(text);
          console.log("CSV content:", text);
          
          try {
            if (file.name.endsWith('.csv')) {
              const rows = text.split('\n').filter(row => row.trim().length > 0);
              
              const hasHeader = rows.length > 0 && rows[0].toLowerCase().includes('tweets') || 
                               rows[0].toLowerCase().includes('text') || 
                               rows[0].toLowerCase().includes('feedback');
              
              const startIndex = hasHeader ? 1 : 0;
              
              for (let i = startIndex; i < rows.length; i++) {
                const row = rows[i];
                if (row.includes(',')) {
                  const columns = row.split(',');
                  if (columns.length > 0 && columns[0].trim()) {
                    messages.push(columns[0].replace(/"/g, '').trim());
                  }
                } else if (row.includes(';')) {
                  const columns = row.split(';');
                  if (columns.length > 0 && columns[0].trim()) {
                    messages.push(columns[0].replace(/"/g, '').trim());
                  }
                } else if (row.includes('\t')) {
                  const columns = row.split('\t');
                  if (columns.length > 0 && columns[0].trim()) {
                    messages.push(columns[0].replace(/"/g, '').trim());
                  }
                } else if (row.trim()) {
                  messages.push(row.replace(/"/g, '').trim());
                }
              }
              
              console.log("Extracted messages:", messages);
              
              if (messages.length === 0) {
                throw new Error('No valid messages found in CSV file');
              }
              
              const res = await axios.post('/api/respond_batch', { 
                customer_texts: messages 
              });
              
              console.log("API response:", res.data);
              
              const mappedResults = res.data.map((item: any) => 
                mapToAnalysisResponse({
                  classification: item.classification,
                  ai_response: item.ai_response
                }, item.input_text)
              );
              
              setResults(mappedResults);
              setSelectedIndex(0);
            } else {
              throw new Error('Please upload a CSV file');
            }
            
            setLoading(false);
          } catch (error: any) {
            console.error('Error processing file:', error);
            setError(`Error processing file: ${error.message || 'Unknown error'}. Please check if it\'s a valid CSV and try again.`);
            setLoading(false);
          }
        };
        reader.readAsText(file);
      } else {
        setError('Please select a CSV file first');
        setLoading(false);
      }
    } catch (error: any) {
      console.error('Error during analysis:', error);
      setError(`Error during analysis: ${error.message || 'Unknown error'}. Please try again.`);
      setLoading(false);
    }
  };

  const current = results[selectedIndex] || {
    emotion: '',
    sarcasm: '',
    aspects: '',
    classification: '',
    response: '',
    originalText: ''
  };

  return (
    <div className="container-fluid p-0">
      <div className="row m-0">
        <div className="col-md-6 p-3">
          <div className="feedback-panel">
            <h5>Customer Feedback Analysis</h5>
            <form onSubmit={handleAnalyze}>
              <div className="mb-3">
                <label htmlFor="file" className="file-input-label">Choose File</label>
                <input
                  type="file"
                  id="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="form-control"
                />
                <small className="text-muted">CSV should have feedback text in the first column</small>
              </div>
              
              <button 
                type="submit" 
                className="analyze-btn"
                disabled={loading || !file}
              >
                {loading ? 'Analyzing...' : 'Analyze & Generate'}
              </button>
            </form>
            
            {error && (
              <div className="alert alert-danger mt-3">
                {error}
              </div>
            )}
            
            {csvContent && error && (
              <div className="mt-3">
                <details>
                  <summary>CSV Debug Info</summary>
                  <pre className="border p-2 mt-2" style={{ maxHeight: '150px', overflow: 'auto' }}>
                    {csvContent}
                  </pre>
                </details>
              </div>
            )}
            
            <div className="response-area mt-4">
              <p className="text-muted">
                {results.length > 0 
                  ? current.response 
                  : "AI-generated response will appear here"}
              </p>
            </div>
            
            {results.length > 0 && (
              <button className="approve-btn">
                Approve & Send
              </button>
            )}
          </div>
        </div>
        
        <div className="col-md-6 p-3">
          <div className="sentiment-report">
            <h5 className="text-center mb-4">Sentiment Analysis Report</h5>
            
            <ClassificationDetector classification={current.classification} />
            <EmotionDetector emotion={current.emotion} />
            <SarcasmDetector sarcasm={current.sarcasm} />
            <AspectsDetector aspects={current.aspects} />
          </div>
          
          {results.length > 1 && (
            <div className="mt-3">
              <label htmlFor="feedback-selector" className="form-label">Select Feedback Item:</label>
              <select
                id="feedback-selector"
                className="form-select"
                value={selectedIndex}
                onChange={(e) => setSelectedIndex(Number(e.target.value))}
              >
                {results.map((_, index) => (
                  <option key={index} value={index}>
                    Feedback {index + 1}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WebApp;