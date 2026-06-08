import { useEffect, useState } from 'react';

import { apiRequest } from '../auth/api';

const MIN_ROWS = 4;
const STATUS_OPTIONS = ['Applied', 'Interview', 'Rejected'];

let tempRowCounter = 0;

function createEmptyRow() {
  tempRowCounter += 1;
  return {
    id: null,
    client_id: `tmp-${tempRowCounter}`,
    application_date: '',
    company_name: '',
    position: '',
    status: 'Applied',
  };
}

function normalizeRows(rows) {
  const mapped = rows.map((row) => ({
    id: typeof row.id === 'number' ? row.id : null,
    client_id: typeof row.id === 'number' ? `db-${row.id}` : createEmptyRow().client_id,
    application_date: String(row.application_date || ''),
    company_name: String(row.company_name || ''),
    position: String(row.position || ''),
    status: STATUS_OPTIONS.includes(String(row.status || '')) ? String(row.status) : 'Applied',
  }));

  while (mapped.length < MIN_ROWS) {
    mapped.push(createEmptyRow());
  }

  return mapped;
}

export default function MyJobsPage() {
  const [rows, setRows] = useState(normalizeRows([]));
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const loadRows = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await apiRequest('/api/v1/jobs');
      setRows(normalizeRows(response?.items || []));
    } catch (err) {
      setError(err.message || 'Could not load jobs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRows();
  }, []);

  const updateRow = (index, field, value) => {
    setRows((prev) =>
      prev.map((row, rowIndex) => {
        if (rowIndex !== index) {
          return row;
        }
        return {
          ...row,
          [field]: value,
        };
      }),
    );
  };

  const addRow = () => {
    setRows((prev) => [...prev, createEmptyRow()]);
  };

  const saveRows = async () => {
    setSaving(true);
    setError('');
    setMessage('');

    try {
      const payloadItems = rows.map((row, index) => ({
        id: row.id,
        application_date: row.application_date,
        company_name: row.company_name,
        position: row.position,
        status: row.status,
        sort_order: index,
      }));

      const response = await apiRequest('/api/v1/jobs', {
        method: 'PUT',
        body: { items: payloadItems },
      });

      setRows(normalizeRows(response?.items || []));
      setMessage('Saved your jobs table.');
    } catch (err) {
      setError(err.message || 'Could not save jobs table.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 space-y-6">
      <header className="glass rounded-3xl p-6 card-border">
        <p className="text-xs uppercase tracking-[0.2em] text-teal">My Jobs</p>
        <h1 className="mt-3 text-3xl md:text-4xl font-semibold text-white">Track job applications</h1>
        <p className="mt-2 text-slate-300">
          Keep your applications in one editable table and update status as your process moves forward.
        </p>
      </header>

      <section className="glass rounded-3xl p-6 card-border space-y-4">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-2xl font-semibold text-white">Applications</h2>
          <button
            type="button"
            onClick={saveRows}
            disabled={saving || loading}
            className="rounded-xl bg-teal px-4 py-2.5 text-ink text-sm font-semibold uppercase tracking-[0.06em] disabled:opacity-60"
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>

        {message && <p className="text-sm text-teal">{message}</p>}
        {error && (
          <div className="rounded-2xl border border-red-500/40 bg-red-500/10 text-red-100 px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {loading ? (
          <p className="text-slate-300">Loading jobs...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm text-slate-200 border-collapse">
              <thead>
                <tr className="border-b border-white/15">
                  <th className="text-left font-semibold py-2 pr-3">No.</th>
                  <th className="text-left font-semibold py-2 pr-3">Date</th>
                  <th className="text-left font-semibold py-2 pr-3">Company name</th>
                  <th className="text-left font-semibold py-2 pr-3">Position</th>
                  <th className="text-left font-semibold py-2 pr-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, index) => (
                  <tr key={row.id ?? row.client_id} className="border-b border-white/5">
                    <td className="py-2 pr-3 align-top">{index + 1}</td>
                    <td className="py-2 pr-3 align-top">
                      <input
                        type="date"
                        value={row.application_date}
                        onChange={(event) => updateRow(index, 'application_date', event.target.value)}
                        className="w-36 rounded-lg bg-black/20 border border-white/15 px-2 py-1.5 text-slate-100"
                      />
                    </td>
                    <td className="py-2 pr-3 align-top">
                      <input
                        type="text"
                        value={row.company_name}
                        onChange={(event) => updateRow(index, 'company_name', event.target.value)}
                        placeholder="Company"
                        className="w-full min-w-56 rounded-lg bg-black/20 border border-white/15 px-2 py-1.5 text-slate-100"
                      />
                    </td>
                    <td className="py-2 pr-3 align-top">
                      <input
                        type="text"
                        value={row.position}
                        onChange={(event) => updateRow(index, 'position', event.target.value)}
                        placeholder="Position"
                        className="w-full min-w-56 rounded-lg bg-black/20 border border-white/15 px-2 py-1.5 text-slate-100"
                      />
                    </td>
                    <td className="py-2 pr-3 align-top">
                      <select
                        value={row.status}
                        onChange={(event) => updateRow(index, 'status', event.target.value)}
                        className="w-32 rounded-lg bg-black/20 border border-white/15 px-2 py-1.5 text-slate-100"
                      >
                        {STATUS_OPTIONS.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="pt-4 flex justify-center">
              <button
                type="button"
                onClick={addRow}
                className="h-9 w-9 rounded-full border border-white/25 text-lg leading-none text-slate-100 hover:border-teal/60"
                title="Add one more row"
                aria-label="Add one more row"
              >
                +
              </button>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
