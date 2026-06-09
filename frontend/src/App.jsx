import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import { apiRequest } from './auth/api';

const HOME_STATE_STORAGE_KEY = 'ats_cv_home_state_v2';

function loadPersistedHomeState() {
  try {
    const rawValue = sessionStorage.getItem(HOME_STATE_STORAGE_KEY);
    if (!rawValue) {
      return {
        job_description: '',
        keywords: [],
        company_name: '',
        position: '',
        has_generated_cv: false,
        has_generated_cover_letter: false,
        cover_letter_text: '',
      };
    }

    const parsed = JSON.parse(rawValue);
    return {
      job_description: String(parsed.job_description || ''),
      keywords: Array.isArray(parsed.keywords) ? parsed.keywords.map((entry) => String(entry || '')) : [],
      company_name: String(parsed.company_name || ''),
      position: String(parsed.position || ''),
      has_generated_cv: Boolean(parsed.has_generated_cv),
      has_generated_cover_letter: Boolean(parsed.has_generated_cover_letter),
      cover_letter_text: String(parsed.cover_letter_text || ''),
    };
  } catch {
    return {
      job_description: '',
      keywords: [],
      company_name: '',
      position: '',
      has_generated_cv: false,
      has_generated_cover_letter: false,
      cover_letter_text: '',
    };
  }
}

function base64ToBlobUrl(base64, mimeType = 'application/pdf') {
  const binary = atob(String(base64 || ''));
  const bytes = new Uint8Array(binary.length);

  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }

  const blob = new Blob([bytes], { type: mimeType });
  return URL.createObjectURL(blob);
}

export default function App() {
  const initialState = loadPersistedHomeState();

  const [user, setUser] = useState(null);
  const [jobDescription, setJobDescription] = useState(initialState.job_description);
  const [keywords, setKeywords] = useState(initialState.keywords);
  const [companyName, setCompanyName] = useState(initialState.company_name);
  const [position, setPosition] = useState(initialState.position);
  const [hasGeneratedCv, setHasGeneratedCv] = useState(initialState.has_generated_cv);
  const [hasGeneratedCoverLetter, setHasGeneratedCoverLetter] = useState(initialState.has_generated_cover_letter);
  const [coverLetterText, setCoverLetterText] = useState(initialState.cover_letter_text);

  const [analyzing, setAnalyzing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generatingCoverLetter, setGeneratingCoverLetter] = useState(false);
  const [addingToJobs, setAddingToJobs] = useState(false);

  const [error, setError] = useState('');
  const [status, setStatus] = useState('');
  const [jobAddMessage, setJobAddMessage] = useState('');

  const [pdfUrl, setPdfUrl] = useState('');
  const [pdfFileName, setPdfFileName] = useState('enhanced_cv.pdf');
  const [coverLetterPdfUrl, setCoverLetterPdfUrl] = useState('');
  const [coverLetterPdfFileName, setCoverLetterPdfFileName] = useState('cover_letter.pdf');

  useEffect(() => {
    let mounted = true;

    async function loadUser() {
      try {
        const currentUser = await apiRequest('/api/v1/auth/me');
        if (mounted) {
          setUser(currentUser);
        }
      } catch {
        if (mounted) {
          setUser(null);
        }
      }
    }

    loadUser();

    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    try {
      sessionStorage.setItem(
        HOME_STATE_STORAGE_KEY,
        JSON.stringify({
          job_description: jobDescription,
          keywords,
          company_name: companyName,
          position,
          has_generated_cv: hasGeneratedCv,
          has_generated_cover_letter: hasGeneratedCoverLetter,
          cover_letter_text: coverLetterText,
        }),
      );
    } catch {
      // Ignore storage failures.
    }
  }, [jobDescription, keywords, companyName, position, hasGeneratedCv, hasGeneratedCoverLetter, coverLetterText]);

  useEffect(() => {
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
      if (coverLetterPdfUrl) {
        URL.revokeObjectURL(coverLetterPdfUrl);
      }
    };
  }, [pdfUrl, coverLetterPdfUrl]);

  const keywordsCsv = useMemo(() => keywords.join(', '), [keywords]);

  const analyzeJobDescription = async () => {
    if (!jobDescription.trim()) {
      setError('Please paste a job description first.');
      return;
    }

    setAnalyzing(true);
    setError('');
    setJobAddMessage('');
    setStatus('Analyzing job description and extracting company, position, and relevant skills...');

    try {
      const response = await apiRequest('/api/v1/cv/enhance/analyze-jd', {
        method: 'POST',
        body: { job_description: jobDescription },
      });

      setKeywords(Array.isArray(response?.keywords) ? response.keywords : []);
      setCompanyName(String(response?.company_name || ''));
      setPosition(String(response?.position || ''));
      setStatus('JD analysis complete.');
    } catch (err) {
      setError(err.message || 'Could not analyze the job description.');
      setStatus('');
    } finally {
      setAnalyzing(false);
    }
  };

  const generateEnhancedCv = async () => {
    if (!jobDescription.trim()) {
      setError('Please paste a job description first.');
      return;
    }

    setGenerating(true);
    setError('');
    setJobAddMessage('');
    setStatus('Generating updated CV PDF with merged skill keywords...');

    try {
      const response = await apiRequest('/api/v1/cv/enhance/generate-pdf', {
        method: 'POST',
        body: {
          job_description: jobDescription,
          keywords,
        },
      });

      const nextKeywords = Array.isArray(response?.keywords_used) ? response.keywords_used : keywords;
      setKeywords(nextKeywords);

      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }

      const nextPdfUrl = base64ToBlobUrl(response?.pdf_base64 || '');
      setPdfUrl(nextPdfUrl);
      setPdfFileName(response?.pdf_file_name || 'enhanced_cv.pdf');
      setHasGeneratedCv(true);
      setStatus('CV generated. Download is ready.');
    } catch (err) {
      setError(err.message || 'Could not generate CV PDF.');
      setStatus('');
    } finally {
      setGenerating(false);
    }
  };

  const generateCoverLetter = async () => {
    if (!jobDescription.trim()) {
      setError('Please paste a job description first.');
      return;
    }

    setGeneratingCoverLetter(true);
    setError('');
    setStatus('Generating cover letter from your My Data profile and job description...');

    try {
      const response = await apiRequest('/api/v1/cv/enhance/generate-cover-letter', {
        method: 'POST',
        body: { job_description: jobDescription },
      });

      if (coverLetterPdfUrl) {
        URL.revokeObjectURL(coverLetterPdfUrl);
      }

      const nextPdfUrl = base64ToBlobUrl(response?.pdf_base64 || '');
      setCoverLetterPdfUrl(nextPdfUrl);
      setCoverLetterPdfFileName(response?.pdf_file_name || 'cover_letter.pdf');
      setCoverLetterText(String(response?.cover_letter_text || ''));
      setHasGeneratedCoverLetter(true);
      setStatus('Cover letter generated. Download is ready.');
    } catch (err) {
      setError(err.message || 'Could not generate cover letter.');
      setStatus('');
    } finally {
      setGeneratingCoverLetter(false);
    }
  };

  const addToMyJobs = async () => {
    setAddingToJobs(true);
    setError('');
    setJobAddMessage('');

    try {
      await apiRequest('/api/v1/jobs/add-from-jd', {
        method: 'POST',
        body: {
          company_name: companyName,
          position,
          status: 'Applied',
        },
      });
      setJobAddMessage('Added to My Jobs with status Applied.');
    } catch (err) {
      setError(err.message || 'Could not add this job to My Jobs.');
    } finally {
      setAddingToJobs(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 space-y-6">
      <header className="glass rounded-3xl p-6 card-border">
        <p className="text-xs uppercase tracking-[0.2em] text-teal">CV Enhancement</p>
        <h1 className="mt-3 text-3xl md:text-4xl font-semibold text-white">
          Welcome, {user?.first_name || 'there'}
        </h1>
        <p className="mt-2 text-slate-300">
          Paste the job description, analyze key terms, then generate a refreshed CV and cover letter.
        </p>

        <div className="mt-4 flex flex-wrap gap-3 text-sm text-slate-300">
          <Link to="/my-data" className="rounded-full border border-white/15 px-3 py-1.5 hover:border-teal/60">
            My Data
          </Link>
          <Link to="/my-jobs" className="rounded-full border border-white/15 px-3 py-1.5 hover:border-teal/60">
            My Jobs
          </Link>
        </div>
      </header>

      <section className="glass rounded-3xl p-6 card-border space-y-4">
        <h2 className="text-2xl font-semibold text-white">Job Description</h2>
        <textarea
          value={jobDescription}
          onChange={(event) => setJobDescription(event.target.value)}
          placeholder="Paste the full job description here..."
          className="w-full h-72 rounded-xl bg-black/20 border border-white/15 px-4 py-3 text-slate-100 overflow-y-auto"
        />
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={analyzeJobDescription}
            disabled={analyzing || generating || generatingCoverLetter || addingToJobs}
            className="rounded-xl bg-teal px-4 py-3 text-ink text-sm font-semibold uppercase tracking-[0.06em] disabled:opacity-60"
          >
            {analyzing ? 'Analyzing...' : 'Analyze JD'}
          </button>
        </div>

        {(companyName || position) && (
          <div className="rounded-2xl border border-white/15 bg-white/5 p-4 text-sm text-slate-200">
            <p>
              <span className="text-slate-400">Company:</span> {companyName || 'Not found in JD'}
            </p>
            <p className="mt-1">
              <span className="text-slate-400">Position:</span> {position || 'Not found in JD'}
            </p>
          </div>
        )}

        {status && <p className="text-sm text-teal">{status}</p>}
        {error && (
          <div className="rounded-2xl border border-red-500/40 bg-red-500/10 text-red-100 px-4 py-3 text-sm">
            {error}
          </div>
        )}
      </section>

      <section className="glass rounded-3xl p-6 card-border space-y-4">
        <h2 className="text-2xl font-semibold text-white">Relevant Keywords</h2>
        <p className="text-sm text-slate-300">
          {keywords.length > 0 ? keywordsCsv : 'No keywords yet. Run analysis first.'}
        </p>

        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={generateEnhancedCv}
            disabled={generating || analyzing || generatingCoverLetter || addingToJobs}
            className="rounded-xl bg-teal px-4 py-3 text-ink text-sm font-semibold uppercase tracking-[0.06em] disabled:opacity-60"
          >
            {generating ? 'Generating CV...' : 'Generate Updated CV PDF'}
          </button>
          <button
            type="button"
            onClick={generateCoverLetter}
            disabled={generatingCoverLetter || analyzing || generating || addingToJobs}
            className="rounded-xl border border-white/20 px-4 py-3 text-sm text-slate-100 disabled:opacity-60"
          >
            {generatingCoverLetter ? 'Generating Cover Letter...' : 'Generate Cover Letter'}
          </button>
        </div>

        {pdfUrl && (
          <a
            href={pdfUrl}
            download={pdfFileName}
            className="inline-flex rounded-xl border border-white/20 px-4 py-3 text-sm text-slate-100"
          >
            Download {pdfFileName}
          </a>
        )}

        {coverLetterPdfUrl && (
          <a
            href={coverLetterPdfUrl}
            download={coverLetterPdfFileName}
            className="inline-flex rounded-xl border border-white/20 px-4 py-3 text-sm text-slate-100"
          >
            Download {coverLetterPdfFileName}
          </a>
        )}
      </section>

      {hasGeneratedCoverLetter && coverLetterText && (
        <section className="glass rounded-3xl p-6 card-border space-y-4">
          <h2 className="text-2xl font-semibold text-white">Cover Letter Preview</h2>
          <p className="text-sm text-slate-200 whitespace-pre-wrap">{coverLetterText}</p>
        </section>
      )}

      {hasGeneratedCv && (
        <section className="glass rounded-3xl p-6 card-border space-y-4">
          <h2 className="text-2xl font-semibold text-white">Did you apply to the job?</h2>
          <p className="text-sm text-slate-300">
            Add this application to My Jobs with today&apos;s date and status set to Applied.
          </p>
          <button
            type="button"
            onClick={addToMyJobs}
            disabled={addingToJobs || analyzing || generating || generatingCoverLetter}
            className="rounded-xl bg-teal px-4 py-3 text-ink text-sm font-semibold uppercase tracking-[0.06em] disabled:opacity-60"
          >
            {addingToJobs ? 'Adding...' : 'Add to my jobs'}
          </button>
          {jobAddMessage && <p className="text-sm text-teal">{jobAddMessage}</p>}
        </section>
      )}
    </div>
  );
}
