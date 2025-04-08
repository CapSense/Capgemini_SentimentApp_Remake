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

const WebApp: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<AnalysisResponse[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);

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
            const rows = text.split('\n').map(row => row.split(',')[0].replace(/"/g, ''));
            messages.push(...rows.filter(row => row));
          } else if (file.name.endsWith('.json')) {
            const jsonData = JSON.parse(text);
            messages.push(...jsonData.map((item: any) => item.message || item));
          }
          const batchResults = await Promise.all(messages.map(async msg => {
            const res = await axios.post<AnalysisResponse>('http://localhost:5000/batch-analyze', { text: msg });
            return { ...res.data, originalText: msg };
          }));
          setResults(batchResults);
          setSelectedIndex(0);
        } catch (error) {
          console.error('Error parsing file:', error);
        }
      };
      reader.readAsText(file);
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
    <div className="web-app row">
      <div className="col-12 d-flex justify-content-between align-items-center mb-3 px-4">
      </div>

      <div className="col-md-6">
        <form onSubmit={handleAnalyze}>
          <input type="file" accept=".csv,.json" onChange={handleFileChange} className="form-control mb-2" />
          <button type="submit" className="btn btn-success">Analyze & Generate</button>
        </form>

        {results.length > 0 && (
          <select
            className="form-select my-2"
            value={selectedIndex}
            onChange={(e) => setSelectedIndex(Number(e.target.value))}
          >
            {results.map((_, index) => (
              <option key={index} value={index}>
                Feedback {index + 1}
              </option>
            ))}
          </select>
        )}
        <div >
          <ResponseDisplay results={results} />
        </div>
        <button className="btn btn-primary mt-2">Approve & Send</button>
      </div>

      {/* sentiment analysis report */}
      <div className="col-md-6">
        <div className="card p-3 mb-3">
          <h4 className="text-center">Sentiment Analysis Report</h4>
          <ClassificationDetector classification={current.classification} />
          <EmotionDetector emotion={current.emotion} />
          <SarcasmDetector sarcasm={current.sarcasm} />
          <AspectsDetector aspects={current.aspects} />
        </div>
      </div>
    </div>
  );
};

export default WebApp;
