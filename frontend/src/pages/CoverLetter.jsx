import { useState } from 'react';
import { Link } from 'react-router-dom';

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


export default function CoverLetter() {
  const [cvFileName, setCvFileName] = useState('');
  const [cvPayload, setCvPayload] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [coverLetterText, setCoverLetterText] = useState('');
  const [pdfUrl, setPdfUrl] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [rendering, setRendering] = useState(false);

  const handleFile = (file) => {
    if (!file) return;
    if (file.type !== 'application/pdf') {
      setError('Please drop a PDF file');
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result;
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

  const handleGenerate = async () => {
    if (!cvPayload || !jobDescription.trim()) {
      setError('Add a PDF CV and paste a job description to continue.');
      return;
    }

    setLoading(true);
    setError('');
    setPdfUrl(''); // Clear previous PDF

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/generate-cover-letter`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cv_content: cvPayload,
          job_description: jobDescription.trim(),
        }),
      });

      if (!response.ok) {
        const errorPayload = await response.json().catch(() => ({}));
        throw new Error(errorPayload.detail || 'API request failed');
      }

      const data = await response.json();
      setCoverLetterText(data.cover_letter_text);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRenderPDF = async () => {
    if (!coverLetterText.trim()) {
      setError('No cover letter text to render.');
      return;
    }

    setRendering(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/render-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: coverLetterText.trim(),
        }),
      });

      if (!response.ok) {
        const errorPayload = await response.json().catch(() => ({}));
        throw new Error(errorPayload.detail || 'Failed to render PDF');
      }

      const data = await response.json();
      if (data.pdf) {
        // Clean up previous URL
        if (pdfUrl) {
          URL.revokeObjectURL(pdfUrl);
        }
        
        const blob = base64ToBlob(data.pdf);
        const url = URL.createObjectURL(blob);
        setPdfUrl(url);
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setRendering(false);
    }
  };

  const primaryButtonClasses =
    'px-5 py-3 rounded-xl text-sm font-semibold uppercase tracking-wide transition flex items-center justify-center gap-2';

  return (
    <div className="min-h-screen pb-20">
      <div className="max-w-6xl mx-auto px-6 pt-14">
        <header className="flex flex-col gap-4">
          <span className="inline-flex w-fit items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold text-teal uppercase tracking-[0.2em]">
            <Link to="/">ATS CV Maker</Link> / Cover Letter
          </span>
          <div className="flex flex-col gap-3">
            <h1 className="text-4xl md:text-5xl font-semibold text-white">
              Generate a Personalized Cover Letter
            </h1>
            <p className="text-slate-300 max-w-3xl">
              Upload your CV and paste a job description to generate a tailored cover letter in seconds. The generated cover letter will highlight your most relevant skills and experiences.
            </p>
          </div>
        </header>

        <main className="mt-10 flex flex-col gap-6">
          {/* Upload Section */}
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
                onClick={handleGenerate}
                disabled={loading}
                className={`${primaryButtonClasses} bg-teal text-ink shadow-glow-teal hover:scale-[1.01] disabled:opacity-60`}
              >
                {loading ? 'Generating...' : 'Generate Cover Letter'}
              </button>
            </div>
          </section>

          {/* Editable Cover Letter Text Section */}
          {coverLetterText && (
            <section className="glass rounded-3xl p-6 shadow-glow-lavender card-border">
              <h3 className="text-2xl font-semibold text-white mb-4">Generated Cover Letter</h3>
              <p className="text-sm text-slate-400 mb-4">Edit the text below as needed, then click "Render PDF" to generate the PDF version.</p>
              <textarea
                value={coverLetterText}
                onChange={(e) => setCoverLetterText(e.target.value)}
                className="w-full h-96 rounded-2xl glass card-border p-4 text-base text-white bg-white/5 focus:outline-none focus:ring-2 focus:ring-purple-500/60 font-mono"
                placeholder="Your cover letter will appear here..."
              />
              
              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  type="button"
                  onClick={handleRenderPDF}
                  disabled={rendering}
                  className={`${primaryButtonClasses} bg-purple-600 text-white shadow-glow-purple hover:scale-[1.01] disabled:opacity-60`}
                >
                  {rendering ? 'Rendering...' : 'Render PDF'}
                </button>
              </div>
            </section>
          )}

          {/* PDF Preview Section */}
          {pdfUrl && (
            <section className="glass rounded-3xl p-6 shadow-glow-teal card-border">
              <h3 className="text-2xl font-semibold text-white mb-4">PDF Preview (A4 Size)</h3>
              <div className="aspect-[1/1.414] w-full max-w-3xl mx-auto overflow-hidden rounded-2xl border border-white/10 bg-white/5">
                <object data={pdfUrl} type="application/pdf" className="h-full w-full" aria-label="Cover Letter PDF" />
              </div>
              <div className="mt-4 flex justify-center">
                <a
                  href={pdfUrl}
                  download="cover-letter.pdf"
                  className={`${primaryButtonClasses} bg-teal text-ink shadow-glow-teal hover:scale-[1.01]`}
                >
                  Download PDF
                </a>
              </div>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
