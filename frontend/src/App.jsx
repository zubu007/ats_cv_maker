import { useMemo, useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function base64ToBlob(base64, contentType = 'application/pdf') {
  const byteCharacters = atob(base64);
  const byteArrays = [];

  for (let offset = 0; offset < byteCharacters.length; offset += 512) {
    const slice = byteCharacters.slice(offset, offset + 512);
    const byteNumbers = new Array(slice.length);

    for (let i = 0; i < slice.length; i += 1) {
      byteNumbers[i] = slice.charCodeAt(i);
    }

    byteArrays.push(new Uint8Array(byteNumbers));
  }

  return new Blob(byteArrays, { type: contentType });
}

const fallbackPdfMessage =
  'Improved PDF will appear here after running "Improve CV" once the API returns a PDF payload.';

export default function App() {
  const [cvFileName, setCvFileName] = useState('');
  const [cvPayload, setCvPayload] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [improvementResult, setImprovementResult] = useState(null);
  const [pdfUrl, setPdfUrl] = useState('');
  const [error, setError] = useState('');
  const [loadingAction, setLoadingAction] = useState('');

  const hasPendingAction = Boolean(loadingAction);
  const hasData = analysisResult || improvementResult;

  const scoreRows = useMemo(() => {
    const rows = [];
    if (analysisResult?.ats_score) {
      const ats = analysisResult.ats_score;
      rows.push({
        label: 'Current ATS Score',
        percentage: ats.percentage,
        required: `${ats.matched_required}/${ats.total_required}`,
        optional: `${ats.matched_optional}/${ats.total_optional}`,
      });
    }

    if (improvementResult?.original_score) {
      const original = improvementResult.original_score;
      rows.push({
        label: 'Original Score (Improve run)',
        percentage: original.percentage,
        required: `${original.matched_required}/${original.total_required}`,
        optional: `${original.matched_optional}/${original.total_optional}`,
      });
    }

    if (improvementResult?.estimated_new_score) {
      const est = improvementResult.estimated_new_score;
      rows.push({
        label: 'Estimated Improved Score',
        percentage: est.percentage,
        required: `${est.matched_required}/${est.total_required}`,
        optional: `${est.matched_optional}/${est.total_optional}`,
      });
    }

    return rows;
  }, [analysisResult, improvementResult]);

  const handleFile = (file) => {
    if (!file) return;
    if (file.type !== 'application/pdf') {
      setError('Please drop a PDF file');
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result;
      // Strip the data URL prefix so the API receives pure base64.
      const base64 = result.split(',')[1];
      setCvPayload(base64);
      setCvFileName(file.name);
      setError('');
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer?.files?.[0];
    handleFile(file);
  };

  const handleBrowse = (event) => {
    const file = event.target.files?.[0];
    handleFile(file);
  };

  const doRequest = async (endpoint, body, actionLabel) => {
    setLoadingAction(actionLabel);
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const errorPayload = await response.json().catch(() => ({}));
        throw new Error(errorPayload.detail || 'API request failed');
      }

      return await response.json();
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoadingAction('');
    }
  };

  const handleAnalyze = async () => {
    if (!cvPayload || !jobDescription.trim()) {
      setError('Add a PDF CV and paste a job description to continue.');
      return;
    }

    const payload = {
      cv_content: cvPayload,
      job_description: jobDescription.trim(),
      include_skills: true,
      include_experience: true,
      max_keywords: 50,
    };

    const data = await doRequest('/api/v1/analyze', payload, 'analyze');
    if (data) {
      setAnalysisResult(data);
    }
  };

  const handleImprove = async () => {
    if (!cvPayload || !jobDescription.trim()) {
      setError('Add a PDF CV and paste a job description to continue.');
      return;
    }

    const payload = {
      cv_content: cvPayload,
      job_description: jobDescription.trim(),
      max_keywords_to_add: 10,
      include_experience: true,
      use_spacy: true,
    };

    const data = await doRequest('/api/v1/improve', payload, 'improve');
    if (data) {
      setImprovementResult(data);

      if (data.improved_pdf_base64) {
        const blob = base64ToBlob(data.improved_pdf_base64);
        setPdfUrl(URL.createObjectURL(blob));
      } else if (data.improved_pdf_url) {
        setPdfUrl(data.improved_pdf_url);
      }
    }
  };

  const primaryButtonClasses =
    'px-5 py-3 rounded-xl text-sm font-semibold uppercase tracking-wide transition flex items-center justify-center gap-2';

  return (
    <div className="min-h-screen pb-20">
      <div className="max-w-6xl mx-auto px-6 pt-14">
        <header className="flex flex-col gap-4">
          <span className="inline-flex w-fit items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold text-teal uppercase tracking-[0.2em]">
            ATS CV Maker
          </span>
          <div className="flex flex-col gap-3">
            <h1 className="text-4xl md:text-5xl font-semibold text-white">
              Analyze and Improve CVs for Any Job in Minutes
            </h1>
            <p className="text-slate-300 max-w-3xl">
              Drop a PDF, paste the role description, and instantly see ATS scores. Run an improvement pass to estimate how much higher your score can go and preview the upgraded PDF when the backend returns it.
            </p>
            <div className="flex flex-wrap gap-3 text-sm text-slate-300">
              <span className="rounded-full bg-white/5 px-3 py-2 border border-white/10">API: {API_BASE_URL}</span>
              <span className="rounded-full bg-white/5 px-3 py-2 border border-white/10">Endpoints: /api/v1/analyze, /api/v1/improve</span>
            </div>
          </div>
        </header>

        <main className="mt-10 grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr] gap-6 items-start">
          <section className="glass rounded-3xl p-6 shadow-glow-teal card-border">
            <div
              className="border-2 border-dashed border-white/15 rounded-2xl p-6 bg-white/5 hover:border-teal/60 transition relative"
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
            >
              <input id="cv-upload" type="file" accept="application/pdf" onChange={handleBrowse} />
              <label htmlFor="cv-upload" className="block cursor-pointer">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex flex-col gap-2">
                    <p className="text-sm uppercase tracking-[0.25em] text-slate-400">CV Upload</p>
                    <h2 className="text-2xl font-semibold text-white">Drop your PDF here</h2>
                    <p className="text-slate-300 text-sm">
                      Drag and drop a PDF CV or click to browse. File is encoded to base64 and sent as `cv_content`.
                    </p>
                    {cvFileName && (
                      <span className="mt-2 inline-flex w-fit items-center gap-2 rounded-full bg-teal/10 px-3 py-2 text-sm text-teal border border-teal/30">
                        Ready: {cvFileName}
                      </span>
                    )}
                  </div>
                  <div className="h-16 w-16 rounded-2xl bg-teal/10 border border-teal/30 flex items-center justify-center text-xl text-teal font-semibold">
                    PDF
                  </div>
                </div>
              </label>
            </div>

            <div className="mt-6">
              <p className="text-sm uppercase tracking-[0.25em] text-slate-400 mb-2">Job Description</p>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job description here..."
                className="w-full h-40 rounded-2xl glass card-border p-4 text-base text-white bg-white/5 focus:outline-none focus:ring-2 focus:ring-teal/60"
              />
            </div>

            {error && (
              <div className="mt-4 rounded-2xl border border-red-500/40 bg-red-500/10 text-red-100 px-4 py-3 text-sm">
                {error}
              </div>
            )}

            <div className="mt-6 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={handleAnalyze}
                disabled={hasPendingAction}
                className={`${primaryButtonClasses} bg-teal text-ink shadow-glow-teal hover:scale-[1.01] disabled:opacity-60`}
              >
                {loadingAction === 'analyze' ? 'Analyzing...' : 'Analyze CV'}
              </button>
              <button
                type="button"
                onClick={handleImprove}
                disabled={hasPendingAction}
                className={`${primaryButtonClasses} bg-white/10 border border-white/20 text-white shadow-glow-lavender hover:border-white/40 disabled:opacity-60`}
              >
                {loadingAction === 'improve' ? 'Improving...' : 'Improve CV'}
              </button>
            </div>
          </section>

          <section className="glass rounded-3xl p-6 shadow-glow-lavender card-border space-y-4">
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Live Scores</p>
                <h3 className="text-2xl font-semibold text-white">ATS + Estimate</h3>
              </div>
              {hasPendingAction && (
                <span className="text-sm text-teal">Working...</span>
              )}
            </div>

            {scoreRows.length > 0 ? (
              <div className="overflow-hidden rounded-2xl border border-white/10">
                <table className="min-w-full text-sm">
                  <thead className="bg-white/10 text-slate-200">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold">Metric</th>
                      <th className="px-4 py-3 text-left font-semibold">Percentage</th>
                      <th className="px-4 py-3 text-left font-semibold">Required</th>
                      <th className="px-4 py-3 text-left font-semibold">Optional</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {scoreRows.map((row) => (
                      <tr key={row.label} className="hover:bg-white/5 transition">
                        <td className="px-4 py-3 text-white font-medium">{row.label}</td>
                        <td className="px-4 py-3 text-teal font-semibold">{row.percentage?.toFixed?.(1) ?? row.percentage}%</td>
                        <td className="px-4 py-3 text-slate-200">{row.required}</td>
                        <td className="px-4 py-3 text-slate-200">{row.optional}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="rounded-2xl border border-dashed border-white/15 bg-white/5 px-4 py-8 text-center text-sm text-slate-400">
                Run Analyze or Improve to see live ATS numbers.
              </div>
            )}

            {analysisResult?.analysis_summary && (
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-200">
                <p className="text-xs uppercase tracking-[0.25em] text-slate-400 mb-2">Analysis Summary</p>
                <p>{analysisResult.analysis_summary}</p>
              </div>
            )}

            {improvementResult?.improvement_summary && (
              <div className="rounded-2xl border border-teal/30 bg-teal/10 p-4 text-sm text-white">
                <p className="text-xs uppercase tracking-[0.25em] text-white/70 mb-2">Improvement Summary</p>
                <p>{improvementResult.improvement_summary}</p>
              </div>
            )}
          </section>
        </main>

        <section className="mt-8 glass rounded-3xl p-6 card-border">
          <div className="flex items-center justify-between gap-2 mb-4">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Improved PDF Preview</p>
              <h3 className="text-2xl font-semibold text-white">See the upgraded CV</h3>
            </div>
            {!pdfUrl && (
              <span className="text-xs text-slate-400">{fallbackPdfMessage}</span>
            )}
          </div>

          <div className="aspect-[4/3] w-full overflow-hidden rounded-2xl border border-white/10 bg-white/5">
            {pdfUrl ? (
              <object data={pdfUrl} type="application/pdf" className="h-full w-full" aria-label="Improved CV PDF" />
            ) : (
              <div className="flex h-full items-center justify-center text-slate-400 text-sm text-center px-6">
                {fallbackPdfMessage}
              </div>
            )}
          </div>
        </section>

        <section className="mt-6 flex flex-wrap gap-3 text-sm text-slate-300">
          <span className="rounded-full bg-white/5 px-3 py-2 border border-white/10">Drag-and-drop enabled</span>
          <span className="rounded-full bg-white/5 px-3 py-2 border border-white/10">Tailwind + Vite + React</span>
          <span className="rounded-full bg-white/5 px-3 py-2 border border-white/10">Base64 payload sent as cv_content</span>
        </section>
      </div>
    </div>
  );
}
