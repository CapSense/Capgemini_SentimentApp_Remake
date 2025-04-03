const ClassificationDetector = ({ classification }: { classification: string }) => {
  return (
    <section className="classification-detector card">

      <div className="btn-group" role="group">
        <input type="radio" className="btn-check" name="classification" id="pos" autoComplete="off" checked={classification === 'pos'} readOnly />
        <label className="btn btn-outline-primary" htmlFor="pos">Positive</label>

        <input type="radio" className="btn-check" name="classification" id="neut" autoComplete="off" checked={classification === 'neut'} readOnly />
        <label className="btn btn-outline-primary" htmlFor="neut">Neutral</label>

        <input type="radio" className="btn-check" name="classification" id="neg" autoComplete="off" checked={classification === 'neg'} readOnly />
        <label className="btn btn-outline-primary" htmlFor="neg">Negative</label>
      </div>
    </section>
  );
};

export default ClassificationDetector;