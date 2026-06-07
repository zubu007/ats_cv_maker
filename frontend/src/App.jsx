import { Link } from 'react-router-dom';
import { useEffect, useMemo, useState } from 'react';

import { apiRequest } from './auth/api';

const STARTER_SECTIONS = [
  'personal_info',
  'professional_summary',
  'skills',
  'work_experience',
  'education',
  'projects',
  'certifications',
  'additional',
];

function sectionLabelFromKey(sectionKey) {
  return sectionKey
    .split('_')
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function normalizeSectionName(input) {
  return input.trim().toLowerCase().replace(/\s+/g, '_');
}

function readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const dataUrl = String(reader.result || '');
        resolve(dataUrl.split(',')[1] || '');
      } catch {
        reject(new Error('Could not read file.'));
      }
    };
    reader.onerror = () => reject(new Error('Could not read file.'));
    reader.readAsDataURL(file);
  });
}

export default function App() {
  const [user, setUser] = useState(null);
  const [sections, setSections] = useState({});
  const [hasUploadedCv, setHasUploadedCv] = useState(false);
  const [cvFileName, setCvFileName] = useState('');
  const [newSectionName, setNewSectionName] = useState('');

  const [loadingDashboard, setLoadingDashboard] = useState(true);
  const [processingUpload, setProcessingUpload] = useState(false);
  const [savingSections, setSavingSections] = useState(false);
  const [error, setError] = useState('');

  const [uploadPromptDismissed, setUploadPromptDismissed] = useState(false);

  const sectionEntries = useMemo(
    () => Object.entries(sections),
    [sections],
  );

  useEffect(() => {
    let mounted = true;

    async function loadDashboard() {
      setLoadingDashboard(true);
      setError('');

      try {
        const [currentUser, workspace] = await Promise.all([
          apiRequest('/api/v1/auth/me'),
          apiRequest('/api/v1/cv/workspace'),
        ]);

        if (!mounted) {
          return;
        }

        setUser(currentUser);
        setSections(workspace?.sections || {});
        setHasUploadedCv(Boolean(workspace?.has_uploaded_cv));
        setCvFileName(workspace?.cv_file_name || '');
      } catch (err) {
        if (mounted) {
          setError(err.message || 'Could not load your dashboard.');
        }
      } finally {
        if (mounted) {
          setLoadingDashboard(false);
        }
      }
    }

    loadDashboard();

    return () => {
      mounted = false;
    };
  }, []);

  const setSectionValue = (sectionKey, content) => {
    setSections((prev) => ({
      ...prev,
      [sectionKey]: content,
    }));
  };

  const removeSection = (sectionKey) => {
    setSections((prev) => {
      const next = { ...prev };
      delete next[sectionKey];
      return next;
    });
  };

  const addSection = () => {
    const normalized = normalizeSectionName(newSectionName);
    if (!normalized) {
      setError('Add a section name first.');
      return;
    }

    if (sections[normalized] !== undefined) {
      setError('This section already exists.');
      return;
    }

    setSections((prev) => ({
      ...prev,
      [normalized]: '',
    }));
    setNewSectionName('');
    setError('');
  };

  const createStarterSections = () => {
    setSections((prev) => {
      const next = { ...prev };
      STARTER_SECTIONS.forEach((sectionName) => {
        if (next[sectionName] === undefined) {
          next[sectionName] = '';
        }
      });
      return next;
    });
  };

  const saveSections = async () => {
    setSavingSections(true);
    setError('');

    try {
      const workspace = await apiRequest('/api/v1/cv/workspace', {
        method: 'PUT',
        body: { sections },
      });

      setSections(workspace?.sections || {});
      setHasUploadedCv(Boolean(workspace?.has_uploaded_cv));
      setCvFileName(workspace?.cv_file_name || '');
    } catch (err) {
      setError(err.message || 'Could not save sections.');
    } finally {
      setSavingSections(false);
    }
  };

  const resetUploadedCv = async () => {
    setError('');

    try {
      const workspace = await apiRequest('/api/v1/cv/workspace/reset', {
        method: 'POST',
      });

      setSections(workspace?.sections || {});
      setHasUploadedCv(false);
      setCvFileName('');
    } catch (err) {
      setError(err.message || 'Could not reset uploaded CV state.');
    }
  };

  const uploadCv = async (file) => {
    if (!file) {
      return;
    }

    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF CV.');
      return;
    }

    setProcessingUpload(true);
    setError('');

    try {
      const cvBase64 = await readFileAsBase64(file);
      const workspace = await apiRequest('/api/v1/cv/workspace/upload', {
        method: 'POST',
        body: {
          cv_base64: cvBase64,
          file_name: file.name,
        },
      });

      setSections(workspace?.sections || {});
      setHasUploadedCv(Boolean(workspace?.has_uploaded_cv));
      setCvFileName(workspace?.cv_file_name || file.name);
      setUploadPromptDismissed(true);
    } catch (err) {
      setError(err.message || 'Could not process CV upload.');
    } finally {
      setProcessingUpload(false);
    }
  };

  const handleDrop = async (event) => {
    event.preventDefault();
    const file = event.dataTransfer?.files?.[0];
    await uploadCv(file);
  };

  const handleBrowse = async (event) => {
    const file = event.target.files?.[0];
    await uploadCv(file);
  };

  if (loadingDashboard) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center text-slate-300">
        Loading your workspace...
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 space-y-6">
      <header className="glass rounded-3xl p-6 card-border">
        <p className="text-xs uppercase tracking-[0.2em] text-teal">ATS CV Maker</p>
        <h1 className="mt-3 text-3xl md:text-4xl font-semibold text-white">
          Welcome, {user?.first_name || 'there'}
        </h1>
        <p className="mt-2 text-slate-300">
          Build your CV workspace by uploading a PDF or manually editing sections.
        </p>

        <div className="mt-4 flex flex-wrap gap-3 text-sm text-slate-300">
          <Link to="/cover-letter" className="rounded-full border border-white/15 px-3 py-1.5 hover:border-teal/60">
            Cover Letter
          </Link>
          <Link to="/my-data" className="rounded-full border border-white/15 px-3 py-1.5 hover:border-teal/60">
            My Data
          </Link>
          {hasUploadedCv && cvFileName && (
            <span className="rounded-full border border-teal/30 bg-teal/10 px-3 py-1.5 text-teal">
              CV: {cvFileName}
            </span>
          )}
        </div>
      </header>

      {!hasUploadedCv && !uploadPromptDismissed && (
        <section
          className="glass rounded-3xl p-6 card-border border-2 border-dashed border-white/20 bg-white/5 relative"
          onDrop={handleDrop}
          onDragOver={(event) => event.preventDefault()}
        >
          <button
            type="button"
            onClick={() => setUploadPromptDismissed(true)}
            className="absolute top-3 right-3 rounded-full border border-white/20 px-3 py-1 text-xs text-slate-300"
          >
            Close
          </button>

          <p className="text-xs uppercase tracking-[0.2em] text-teal">First-time setup</p>
          <h2 className="mt-3 text-2xl font-semibold text-white">Drag and drop your CV PDF</h2>
          <p className="mt-2 text-sm text-slate-300 max-w-3xl">
            We will extract sections with AI and build editable section blocks automatically.
          </p>

          <div className="mt-5 flex flex-wrap gap-3">
            <input id="main-cv-upload" type="file" accept="application/pdf" className="hidden" onChange={handleBrowse} />
            <label
              htmlFor="main-cv-upload"
              className="cursor-pointer rounded-xl bg-teal px-4 py-3 text-ink text-sm font-semibold uppercase tracking-[0.06em]"
            >
              Upload CV
            </label>
            <button
              type="button"
              onClick={() => {
                setUploadPromptDismissed(true);
                createStarterSections();
              }}
              className="rounded-xl border border-white/20 px-4 py-3 text-sm text-slate-200"
            >
              Skip and fill manually
            </button>
          </div>

          {processingUpload && (
            <p className="mt-4 text-sm text-teal">Processing CV and extracting sections with AI...</p>
          )}
        </section>
      )}

      {error && (
        <div className="rounded-2xl border border-red-500/40 bg-red-500/10 text-red-100 px-4 py-3 text-sm">
          {error}
        </div>
      )}

      {uploadPromptDismissed && !hasUploadedCv && (
        <section className="glass rounded-3xl p-6 card-border">
          <div className="flex flex-wrap gap-3 items-center justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-white">Manual CV section editor</h2>
              <p className="mt-1 text-slate-300 text-sm">
                Add section blocks yourself or upload a CV any time.
              </p>
            </div>
            <div className="flex gap-3">
              <input id="secondary-cv-upload" type="file" accept="application/pdf" className="hidden" onChange={handleBrowse} />
              <label
                htmlFor="secondary-cv-upload"
                className="cursor-pointer rounded-xl border border-white/20 px-4 py-2.5 text-sm text-slate-200"
              >
                Upload CV instead
              </label>
              <button
                type="button"
                onClick={createStarterSections}
                className="rounded-xl border border-teal/30 bg-teal/10 px-4 py-2.5 text-sm text-teal"
              >
                Add starter sections
              </button>
            </div>
          </div>

          {processingUpload && (
            <p className="mt-4 text-sm text-teal">Processing CV and extracting sections with AI...</p>
          )}
        </section>
      )}

      <section className="glass rounded-3xl p-6 card-border">
        <div className="flex flex-wrap gap-3 items-center justify-between">
          <h2 className="text-2xl font-semibold text-white">CV Sections</h2>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={saveSections}
              disabled={savingSections}
              className="rounded-xl bg-teal px-4 py-2.5 text-sm text-ink font-semibold uppercase tracking-[0.06em] disabled:opacity-60"
            >
              {savingSections ? 'Saving...' : 'Save sections'}
            </button>
            {hasUploadedCv && (
              <button
                type="button"
                onClick={resetUploadedCv}
                className="rounded-xl border border-white/20 px-4 py-2.5 text-sm text-slate-200"
              >
                Clear uploaded CV state
              </button>
            )}
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-3">
          <input
            value={newSectionName}
            onChange={(event) => setNewSectionName(event.target.value)}
            placeholder="New section name (e.g. volunteer experience)"
            className="w-full md:w-80 rounded-xl bg-white/5 border border-white/15 px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-teal/60"
          />
          <button
            type="button"
            onClick={addSection}
            className="rounded-xl border border-white/20 px-4 py-2.5 text-sm text-slate-200"
          >
            Add section
          </button>
        </div>

        {sectionEntries.length === 0 ? (
          <div className="mt-8 rounded-2xl border border-white/10 bg-white/5 p-5 text-slate-300">
            No sections yet. Upload a CV to auto-generate sections or add one manually.
          </div>
        ) : (
          <div className="mt-6 grid grid-cols-1 gap-4">
            {sectionEntries.map(([sectionKey, sectionContent]) => (
              <article key={sectionKey} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <h3 className="text-lg font-semibold text-white">{sectionLabelFromKey(sectionKey)}</h3>
                  <button
                    type="button"
                    onClick={() => removeSection(sectionKey)}
                    className="rounded-lg border border-red-400/40 px-3 py-1.5 text-xs text-red-200"
                  >
                    Remove section
                  </button>
                </div>

                <textarea
                  value={sectionContent}
                  onChange={(event) => setSectionValue(sectionKey, event.target.value)}
                  className="mt-3 w-full min-h-36 rounded-xl bg-black/20 border border-white/15 px-4 py-3 text-slate-100 focus:outline-none focus:ring-2 focus:ring-teal/60"
                  placeholder="Add section details..."
                />
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
