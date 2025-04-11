const SarcasmDetector = ({ sarcasm }: { sarcasm: string }) => {
  return (
    <div className="result-box border rounded p-3 mb-3">
      <strong>Sarcasm Detection:</strong>
      <p className="mt-2 mb-0 text-muted">{sarcasm || 'Awaiting analysis'}</p>
    </div>
  );
};

export default SarcasmDetector;