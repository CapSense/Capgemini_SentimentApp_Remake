const AspectsDetector = ({ aspects }: { aspects: string }) => {
  return (
    <div className="result-box border rounded p-3 mb-3">
      <strong>Aspect-based Sentiment Analysis:</strong>
      <p className="mt-2 mb-0 text-muted">{aspects || 'Awaiting analysis'}</p>
    </div>
  );
};

export default AspectsDetector;
