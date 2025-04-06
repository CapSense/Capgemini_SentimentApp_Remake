import { useState } from 'react';
import axios from 'axios';
import EmotionDetector from './EmotionDetector';
import SarcasmDetector from './SarcasmDetector';
import ClassificationDetector from './ClassificationDetector';
import AspectsDetector from './AspectsDetector';
import ResponseDisplay from './ResponseDisplay';

interface AnalysisResponse {
  emotion: string;
  sarcasm: string;
  aspects: string;
  classification: string;
  response: string;
}

const WebApp: React.FC = () => {
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<AnalysisResponse[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setFile(e.target.files[0]);
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    const messages: string[] = [];

    if (file) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const text = e.target?.result as string;
        try {
          if (file.name.endsWith('.csv')) {
            const rows = text.split('\n').map(row => row.split(',')[0].replace(/"/g, '')); // Simple CSV parsing
            messages.push(...rows.filter(row => row));
          } else if (file.name.endsWith('.json')) {
            const jsonData = JSON.parse(text); // JSON parsing
            messages.push(...jsonData.map((item: any) => item.message || item));
          }
          const batchResults = await Promise.all(messages.map(async msg => {
            const res = await axios.post<AnalysisResponse>('/api/batch-analyze', { text: msg });
            return res.data;
          }));
          setResults(batchResults);
        } catch (error) {
          console.error('Error parsing file:', error);
        }
      };
      reader.readAsText(file);
    } else if (text) {
      const res = await axios.post<AnalysisResponse>('/api/respond', { customer_text: text });
      setResults([res.data]);
    }
  };

  return (
    <div className="web-app row">
      <div className="col-md-6">
        <form onSubmit={handleAnalyze}>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste or upload feedback"
            className="form-control mb-2"
            rows={5}
          />
          <input type="file" accept=".csv,.json" onChange={handleFileChange} className="form-control mb-2" />
          <button type="submit" className="btn btn-success">Analyze & Generate</button>
        </form>
        <ResponseDisplay results={results} />
        <button onClick={() => axios.get('/api/export-results')} className="btn btn-secondary mt-2">Export to Power BI</button>
        <button className="btn btn-primary mt-2">Approve & Send</button>
      </div>
      {/* sentiment analysis report */}
<div className="col-md-6">
  <div className="card p-3 mb-3">
    <h4 className="text-center mb-3">Sentiment Analysis Report</h4>
    <div className="mb-3">
      <div className="p-3">
        <h5 className="text-center">Feedback Classification</h5>
        <ClassificationDetector classification="Positive" />
      </div>
    </div>
    <div className="mb-3">
      <div className="p-3">
        <h5 className="text-center">Sarcasm Detector</h5>
        <SarcasmDetector sarcasm="No sarcasm detected" />
      </div>
    </div>
    <div className="mb-3">
      <div className="p-3">
        <h5 className="text-center">Emotion Detector</h5>
        <EmotionDetector emotion="N/A" />
      </div>
    </div>
    <div className="mb-3">
      <div className="p-3">
        <h5 className="text-center">Aspect-Based Sentiment Analysis</h5>
        <AspectsDetector aspects="Product quality, Service efficiency, Delivery speed" />
      </div>
    </div>
    {results.map((r, i) => (
      <div key={i} className="mb-3">
        <div className="p-3">
          <h5 className="text-center">Feedback Classification</h5>
          <ClassificationDetector classification={r.classification} />
          <h5 className="text-center">Emotion Detector</h5>
          <EmotionDetector emotion={r.emotion} />
          <h5 className="text-center">Aspect-Based Sentiment Analysis</h5>
          <AspectsDetector aspects={r.aspects} />
          <h5 className="text-center">Sarcasm Detector</h5>
          <SarcasmDetector sarcasm={r.sarcasm} />
        </div>
      </div>
    ))}
  </div>
</div>
    </div>
  );
};


export default WebApp;