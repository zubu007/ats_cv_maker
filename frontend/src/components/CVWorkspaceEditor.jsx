import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';

import { apiRequest } from '../auth/api';

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

function emptyWorkExperienceEntry() {
  return {
    company_name: '',
    location: '',
    role: '',
    start_date: '',
    end_date: '',
    currently_working: false,
    overview: '',
  };
}

function emptyEducationEntry() {
  return {
    institution_name: '',
    location: '',
    degree: '',
    start_date: '',
    end_date: '',
    currently_studying: false,
    overview: '',
  };
}

function emptyProjectEntry() {
  return {
    project_name: '',
    details: '',
  };
}

function emptyCertificationEntry() {
  return {
    certification_name: '',
    details: '',
  };
}

function emptySections() {
  return {
    personal_info: {
      name: '',
      phone: '',
      email: '',
      location: '',
    },
    professional_summary_overview: '',
    skills_overview: '',
    work_experience: [],
    education: [],
    projects: [],
    certifications: [],
    additional_overview: '',
  };
}

function splitBlocks(text) {
  return String(text || '')
    .split('\n\n')
    .map((block) => block.trim())
    .filter(Boolean);
}

function normalizeWorkExperience(raw) {
  if (Array.isArray(raw)) {
    return raw.map((entry) => ({ ...emptyWorkExperienceEntry(), ...entry }));
  }

  if (raw && typeof raw === 'object' && Array.isArray(raw.entries)) {
    return normalizeWorkExperience(raw.entries);
  }

  if (typeof raw === 'string') {
    return splitBlocks(raw).map((block) => {
      const lines = block.split('\n').map((line) => line.trim()).filter(Boolean);
      return {
        ...emptyWorkExperienceEntry(),
        company_name: lines[0] || '',
        role: lines[1] || '',
        overview: lines.slice(2).join('\n') || lines.slice(1).join('\n'),
        currently_working: /present|current/i.test(block),
      };
    });
  }

  return [];
}

function normalizeEducation(raw) {
  if (Array.isArray(raw)) {
    return raw.map((entry) => ({ ...emptyEducationEntry(), ...entry }));
  }

  if (raw && typeof raw === 'object' && Array.isArray(raw.entries)) {
    return normalizeEducation(raw.entries);
  }

  if (typeof raw === 'string') {
    return splitBlocks(raw).map((block) => {
      const lines = block.split('\n').map((line) => line.trim()).filter(Boolean);
      return {
        ...emptyEducationEntry(),
        institution_name: lines[0] || '',
        degree: lines[1] || '',
        overview: lines.slice(2).join('\n') || lines.slice(1).join('\n'),
        currently_studying: /present|current/i.test(block),
      };
    });
  }

  return [];
}

function normalizeProjects(raw) {
  if (Array.isArray(raw)) {
    return raw.map((entry) => ({ ...emptyProjectEntry(), ...entry }));
  }

  if (raw && typeof raw === 'object' && Array.isArray(raw.entries)) {
    return normalizeProjects(raw.entries);
  }

  if (typeof raw === 'string') {
    return splitBlocks(raw).map((block) => {
      const lines = block.split('\n').map((line) => line.trim()).filter(Boolean);
      return {
        ...emptyProjectEntry(),
        project_name: lines[0] || '',
        details: lines.slice(1).join('\n') || block,
      };
    });
  }

  return [];
}

function normalizeCertifications(raw) {
  if (Array.isArray(raw)) {
    return raw.map((entry) => ({ ...emptyCertificationEntry(), ...entry }));
  }

  if (raw && typeof raw === 'object' && Array.isArray(raw.entries)) {
    return normalizeCertifications(raw.entries);
  }

  if (typeof raw === 'string') {
    return splitBlocks(raw).map((block) => {
      const lines = block.split('\n').map((line) => line.trim()).filter(Boolean);
      return {
        ...emptyCertificationEntry(),
        certification_name: lines[0] || '',
        details: lines.slice(1).join('\n'),
      };
    });
  }

  return [];
}

function normalizeSections(rawSections) {
  if (!rawSections || typeof rawSections !== 'object') {
    return emptySections();
  }

  const personalRaw = rawSections.personal_info;
  const personalInfo =
    personalRaw && typeof personalRaw === 'object' && !Array.isArray(personalRaw)
      ? {
          name: String(personalRaw.name || ''),
          phone: String(personalRaw.phone || ''),
          email: String(personalRaw.email || ''),
          location: String(personalRaw.location || ''),
        }
      : { ...emptySections().personal_info };

  return {
    personal_info: personalInfo,
    professional_summary_overview: String(
      rawSections.professional_summary_overview || rawSections.professional_summary || '',
    ),
    skills_overview: String(rawSections.skills_overview || rawSections.skills || ''),
    work_experience: normalizeWorkExperience(rawSections.work_experience),
    education: normalizeEducation(rawSections.education),
    projects: normalizeProjects(rawSections.projects),
    certifications: normalizeCertifications(rawSections.certifications),
    additional_overview: String(rawSections.additional_overview || rawSections.additional || ''),
  };
}

function SectionCard({ title, children }) {
  return (
    <section className="glass rounded-3xl p-6 card-border">
      <h2 className="text-2xl font-semibold text-white">{title}</h2>
      <div className="mt-4 space-y-4">{children}</div>
    </section>
  );
}

export default function CVWorkspaceEditor() {
  const [user, setUser] = useState(null);
  const [sections, setSections] = useState(emptySections());
  const [hasUploadedCv, setHasUploadedCv] = useState(false);
  const [cvFileName, setCvFileName] = useState('');

  const [loadingDashboard, setLoadingDashboard] = useState(true);
  const [processingUpload, setProcessingUpload] = useState(false);
  const [savingSections, setSavingSections] = useState(false);
  const [error, setError] = useState('');

  const [uploadPromptDismissed, setUploadPromptDismissed] = useState(false);

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
        setSections(normalizeSections(workspace?.sections || {}));
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

  const updatePersonalInfo = (field, value) => {
    setSections((prev) => ({
      ...prev,
      personal_info: {
        ...prev.personal_info,
        [field]: value,
      },
    }));
  };

  const updateArrayEntry = (sectionKey, index, field, value) => {
    setSections((prev) => ({
      ...prev,
      [sectionKey]: prev[sectionKey].map((entry, entryIndex) =>
        entryIndex === index ? { ...entry, [field]: value } : entry,
      ),
    }));
  };

  const addArrayEntry = (sectionKey, emptyFactory) => {
    setSections((prev) => ({
      ...prev,
      [sectionKey]: [...prev[sectionKey], emptyFactory()],
    }));
  };

  const removeArrayEntry = (sectionKey, index) => {
    setSections((prev) => ({
      ...prev,
      [sectionKey]: prev[sectionKey].filter((_, entryIndex) => entryIndex !== index),
    }));
  };

  const saveSections = async () => {
    setSavingSections(true);
    setError('');

    try {
      const workspace = await apiRequest('/api/v1/cv/workspace', {
        method: 'PUT',
        body: { sections },
      });

      setSections(normalizeSections(workspace?.sections || {}));
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

      setSections(normalizeSections(workspace?.sections || {}));
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

      setSections(normalizeSections(workspace?.sections || {}));
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
          Upload your CV to auto-populate structured sections, then edit everything before saving.
        </p>

        <div className="mt-4 flex flex-wrap gap-3 text-sm text-slate-300">
          <Link to="/cover-letter" className="rounded-full border border-white/15 px-3 py-1.5 hover:border-teal/60">
            Cover Letter
          </Link>
          <Link to="/my-jobs" className="rounded-full border border-white/15 px-3 py-1.5 hover:border-teal/60">
            My Jobs
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
            AI will extract personal info fields, employment entries, education entries, projects, and certifications.
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
              onClick={() => setUploadPromptDismissed(true)}
              className="rounded-xl border border-white/20 px-4 py-3 text-sm text-slate-200"
            >
              Skip and fill manually
            </button>
          </div>

          {processingUpload && (
            <p className="mt-4 text-sm text-teal">Processing CV and extracting structured sections with AI...</p>
          )}
        </section>
      )}

      {error && (
        <div className="rounded-2xl border border-red-500/40 bg-red-500/10 text-red-100 px-4 py-3 text-sm">
          {error}
        </div>
      )}

      <section className="glass rounded-3xl p-6 card-border">
        <div className="flex flex-wrap gap-3 items-center justify-between">
          <h2 className="text-2xl font-semibold text-white">Workspace</h2>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={saveSections}
              disabled={savingSections}
              className="rounded-xl bg-teal px-4 py-2.5 text-sm text-ink font-semibold uppercase tracking-[0.06em] disabled:opacity-60"
            >
              {savingSections ? 'Saving...' : 'Save'}
            </button>
            <input id="secondary-cv-upload" type="file" accept="application/pdf" className="hidden" onChange={handleBrowse} />
            <label
              htmlFor="secondary-cv-upload"
              className="cursor-pointer rounded-xl border border-white/20 px-4 py-2.5 text-sm text-slate-200"
            >
              Upload CV
            </label>
            {hasUploadedCv && (
              <button
                type="button"
                onClick={resetUploadedCv}
                className="rounded-xl border border-white/20 px-4 py-2.5 text-sm text-slate-200"
              >
                Reset
              </button>
            )}
          </div>
        </div>
      </section>

      <SectionCard title="Personal Info">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <input
            value={sections.personal_info.name}
            onChange={(event) => updatePersonalInfo('name', event.target.value)}
            placeholder="Name"
            className="rounded-xl bg-black/20 border border-white/15 px-4 py-3 text-slate-100"
          />
          <input
            value={sections.personal_info.phone}
            onChange={(event) => updatePersonalInfo('phone', event.target.value)}
            placeholder="Phone"
            className="rounded-xl bg-black/20 border border-white/15 px-4 py-3 text-slate-100"
          />
          <input
            value={sections.personal_info.email}
            onChange={(event) => updatePersonalInfo('email', event.target.value)}
            placeholder="Email"
            className="rounded-xl bg-black/20 border border-white/15 px-4 py-3 text-slate-100"
          />
          <input
            value={sections.personal_info.location}
            onChange={(event) => updatePersonalInfo('location', event.target.value)}
            placeholder="Location"
            className="rounded-xl bg-black/20 border border-white/15 px-4 py-3 text-slate-100"
          />
        </div>
      </SectionCard>

      <SectionCard title="Professional Summary">
        <textarea
          value={sections.professional_summary_overview}
          onChange={(event) => setSections((prev) => ({ ...prev, professional_summary_overview: event.target.value }))}
          className="w-full min-h-32 rounded-xl bg-black/20 border border-white/15 px-4 py-3 text-slate-100"
          placeholder="Professional summary"
        />
      </SectionCard>

      <SectionCard title="Skills">
        <textarea
          value={sections.skills_overview}
          onChange={(event) => setSections((prev) => ({ ...prev, skills_overview: event.target.value }))}
          className="w-full min-h-24 rounded-xl bg-black/20 border border-white/15 px-4 py-3 text-slate-100"
          placeholder="Comma-separated skills"
        />
      </SectionCard>

      <SectionCard title="Work Experience">
        <div className="flex justify-end">
          <button
            type="button"
            onClick={() => addArrayEntry('work_experience', emptyWorkExperienceEntry)}
            className="rounded-lg border border-white/20 px-3 py-1.5 text-xs text-slate-200"
          >
            Add Employment
          </button>
        </div>
        {sections.work_experience.length === 0 ? (
          <p className="text-sm text-slate-400">No employment entries yet.</p>
        ) : (
          sections.work_experience.map((entry, index) => (
            <div key={`work-${index}`} className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-3">
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => removeArrayEntry('work_experience', index)}
                  className="rounded-lg border border-red-400/40 px-3 py-1 text-xs text-red-200"
                >
                  Remove
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input value={entry.company_name} onChange={(e) => updateArrayEntry('work_experience', index, 'company_name', e.target.value)} placeholder="Company name" className="rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
                <input value={entry.location} onChange={(e) => updateArrayEntry('work_experience', index, 'location', e.target.value)} placeholder="Location" className="rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
                <input value={entry.role} onChange={(e) => updateArrayEntry('work_experience', index, 'role', e.target.value)} placeholder="Role" className="rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
                <input value={entry.start_date} onChange={(e) => updateArrayEntry('work_experience', index, 'start_date', e.target.value)} placeholder="Start date" className="rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
                <input value={entry.end_date} onChange={(e) => updateArrayEntry('work_experience', index, 'end_date', e.target.value)} placeholder="End date" className="rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
                <label className="inline-flex items-center gap-2 text-sm text-slate-200">
                  <input type="checkbox" checked={entry.currently_working} onChange={(e) => updateArrayEntry('work_experience', index, 'currently_working', e.target.checked)} />
                  Currently working
                </label>
              </div>
              <textarea value={entry.overview} onChange={(e) => updateArrayEntry('work_experience', index, 'overview', e.target.value)} placeholder="Overview" className="w-full min-h-24 rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
            </div>
          ))
        )}
      </SectionCard>

      <SectionCard title="Education">
        <div className="flex justify-end">
          <button
            type="button"
            onClick={() => addArrayEntry('education', emptyEducationEntry)}
            className="rounded-lg border border-white/20 px-3 py-1.5 text-xs text-slate-200"
          >
            Add Education
          </button>
        </div>
        {sections.education.length === 0 ? (
          <p className="text-sm text-slate-400">No education entries yet.</p>
        ) : (
          sections.education.map((entry, index) => (
            <div key={`edu-${index}`} className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-3">
              <div className="flex justify-end">
                <button type="button" onClick={() => removeArrayEntry('education', index)} className="rounded-lg border border-red-400/40 px-3 py-1 text-xs text-red-200">Remove</button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input value={entry.institution_name} onChange={(e) => updateArrayEntry('education', index, 'institution_name', e.target.value)} placeholder="Institution" className="rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
                <input value={entry.location} onChange={(e) => updateArrayEntry('education', index, 'location', e.target.value)} placeholder="Location" className="rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
                <input value={entry.degree} onChange={(e) => updateArrayEntry('education', index, 'degree', e.target.value)} placeholder="Degree" className="rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
                <input value={entry.start_date} onChange={(e) => updateArrayEntry('education', index, 'start_date', e.target.value)} placeholder="Start date" className="rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
                <input value={entry.end_date} onChange={(e) => updateArrayEntry('education', index, 'end_date', e.target.value)} placeholder="End date" className="rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
                <label className="inline-flex items-center gap-2 text-sm text-slate-200">
                  <input type="checkbox" checked={entry.currently_studying} onChange={(e) => updateArrayEntry('education', index, 'currently_studying', e.target.checked)} />
                  Currently studying
                </label>
              </div>
              <textarea value={entry.overview} onChange={(e) => updateArrayEntry('education', index, 'overview', e.target.value)} placeholder="Overview" className="w-full min-h-24 rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
            </div>
          ))
        )}
      </SectionCard>

      <SectionCard title="Projects">
        <div className="flex justify-end">
          <button type="button" onClick={() => addArrayEntry('projects', emptyProjectEntry)} className="rounded-lg border border-white/20 px-3 py-1.5 text-xs text-slate-200">Add Project</button>
        </div>
        {sections.projects.length === 0 ? (
          <p className="text-sm text-slate-400">No project entries yet.</p>
        ) : (
          sections.projects.map((entry, index) => (
            <div key={`project-${index}`} className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-3">
              <div className="flex justify-end">
                <button type="button" onClick={() => removeArrayEntry('projects', index)} className="rounded-lg border border-red-400/40 px-3 py-1 text-xs text-red-200">Remove</button>
              </div>
              <input value={entry.project_name} onChange={(e) => updateArrayEntry('projects', index, 'project_name', e.target.value)} placeholder="Project name" className="w-full rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
              <textarea value={entry.details} onChange={(e) => updateArrayEntry('projects', index, 'details', e.target.value)} placeholder="Project details" className="w-full min-h-24 rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
            </div>
          ))
        )}
      </SectionCard>

      <SectionCard title="Certifications">
        <div className="flex justify-end">
          <button type="button" onClick={() => addArrayEntry('certifications', emptyCertificationEntry)} className="rounded-lg border border-white/20 px-3 py-1.5 text-xs text-slate-200">Add Certification</button>
        </div>
        {sections.certifications.length === 0 ? (
          <p className="text-sm text-slate-400">No certification entries yet.</p>
        ) : (
          sections.certifications.map((entry, index) => (
            <div key={`cert-${index}`} className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-3">
              <div className="flex justify-end">
                <button type="button" onClick={() => removeArrayEntry('certifications', index)} className="rounded-lg border border-red-400/40 px-3 py-1 text-xs text-red-200">Remove</button>
              </div>
              <input value={entry.certification_name} onChange={(e) => updateArrayEntry('certifications', index, 'certification_name', e.target.value)} placeholder="Certification name" className="w-full rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
              <textarea value={entry.details} onChange={(e) => updateArrayEntry('certifications', index, 'details', e.target.value)} placeholder="Certification details" className="w-full min-h-24 rounded-lg bg-black/20 border border-white/15 px-3 py-2 text-slate-100" />
            </div>
          ))
        )}
      </SectionCard>

      <SectionCard title="Additional">
        <textarea
          value={sections.additional_overview}
          onChange={(event) => setSections((prev) => ({ ...prev, additional_overview: event.target.value }))}
          className="w-full min-h-32 rounded-xl bg-black/20 border border-white/15 px-4 py-3 text-slate-100"
          placeholder="Unstructured items the model could not map"
        />
      </SectionCard>
    </div>
  );
}
