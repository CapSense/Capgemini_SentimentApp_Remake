const ClassificationDetector = ({ classification }: { classification: string }) => {
  return (
    <div className="result-box border rounded p-3 mb-3">
      <strong>Feedback Classification:</strong>
      <br />
      <div className="d-flex justify-content-center mt-2">
        <div className="btn-group" role="group">
          <input
            type="radio"
            className="btn-check"
            name="classification"
            id="pos"
            autoComplete="off"
            checked={classification === 'pos'}
            readOnly
          />
          <label className="btn btn-outline-primary" htmlFor="pos">Positive</label>

          <input
            type="radio"
            className="btn-check"
            name="classification"
            id="neut"
            autoComplete="off"
            checked={classification === 'neut'}
            readOnly
          />
          <label className="btn btn-outline-primary" htmlFor="neut">Neutral</label>

          <input
            type="radio"
            className="btn-check"
            name="classification"
            id="neg"
            autoComplete="off"
            checked={classification === 'neg'}
            readOnly
          />
          <label className="btn btn-outline-primary" htmlFor="neg">Negative</label>
        </div>
      </div>
    </div>
  );
};

export default ClassificationDetector;
