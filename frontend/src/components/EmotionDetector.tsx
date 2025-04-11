const EmotionDetector = ({ emotion }: { emotion: string }) => {
  return (
    <div className="result-box border rounded p-3 mb-3">
      <strong>Emotion Detection:</strong>
      <p className="mt-2 mb-0 text-muted">{emotion || 'Awaiting analysis'}</p>
    </div>
  );
};

export default EmotionDetector;