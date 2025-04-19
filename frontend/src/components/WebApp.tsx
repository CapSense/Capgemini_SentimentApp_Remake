
import { useState } from 'react';
import axios from 'axios';
import EmotionDetector from './EmotionDetector';
import SarcasmDetector from './SarcasmDetector';
import ClassificationDetector from './ClassificationDetector';
import AspectsDetector from './AspectsDetector';
import ResponseDisplay from './ResponseDisplay';
import '../WebApp.css';
import handleFeedbackSubmission from '../utils/index-feedback-handler'; // Step 2 done

interface AnalysisResponse {
  emotion: string;
  sarcasm: string;
  aspects: string;
  classification: string;
  response: string;
  originalText: string;
  f1Score?: number;
  status?: string;
}

const WebApp: React.FC = () => {
  const [results, setResults] = useState<AnalysisResponse[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [feedbackStatus, setFeedbackStatus] = useState<string | null>(null);

  const current = results[selectedIndex] || {
    emotion: '',
    sarcasm: '',
    aspects: '',
    classification: '',
    response: '',
    originalText: '',
    f1Score: 0
  };

  const handleApprove = () => {
    handleFeedbackSubmission('approved', selectedIndex, results, setFeedbackStatus);
  };

  const handleReject = () => {
    handleFeedbackSubmission('rejected', selectedIndex, results, setFeedbackStatus);
  };

  return (
    <>
      {/* Render Buttons */}
      <button className="approve-btn" onClick={handleApprove}>Approve</button>
      <button className="reject-btn" onClick={handleReject}>Reject</button>

      {feedbackStatus && <p>{feedbackStatus}</p>}
    </>
  );
};

export default WebApp;
