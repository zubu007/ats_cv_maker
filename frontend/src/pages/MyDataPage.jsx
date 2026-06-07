import { useEffect, useState } from 'react';

import { apiRequest } from '../auth/api';

function formatDate(value) {
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

export default function MyDataPage() {
  const [items, setItems] = useState([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const loadItems = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await apiRequest('/api/v1/me/data');
      setItems(data.items || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadItems();
  }, []);

  const resetForm = () => {
    setTitle('');
    setContent('');
    setEditingId(null);
  };

  const submit = async (event) => {
    event.preventDefault();
    if (!title.trim() || !content.trim()) {
      setError('Title and content are required.');
      return;
    }

    setError('');

    try {
      if (editingId) {
        await apiRequest(`/api/v1/me/data/${editingId}`, {
          method: 'PUT',
          body: {
            title: title.trim(),
            content: content.trim(),
          },
        });
      } else {
        await apiRequest('/api/v1/me/data', {
          method: 'POST',
          body: {
            title: title.trim(),
            content: content.trim(),
          },
        });
      }
      resetForm();
      await loadItems();
    } catch (err) {
      setError(err.message);
    }
  };

  const startEdit = (item) => {
    setEditingId(item.id);
    setTitle(item.title);
    setContent(item.content);
  };

  const remove = async (itemId) => {
    try {
      await apiRequest(`/api/v1/me/data/${itemId}`, { method: 'DELETE' });
      await loadItems();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 grid grid-cols-1 lg:grid-cols-[1fr_1.1fr] gap-6">
      <section className="glass rounded-3xl p-6 card-border">
        <p className="text-xs uppercase tracking-[0.2em] text-teal">Personal Data</p>
        <h1 className="mt-3 text-3xl font-semibold text-white">Manage your own entries</h1>
        <p className="mt-2 text-sm text-slate-300">
          These records are private to your logged-in account.
        </p>

        <form className="mt-6 space-y-4" onSubmit={submit}>
          <label className="block">
            <span className="text-sm text-slate-300">Title</span>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="mt-1 w-full rounded-xl bg-white/5 border border-white/15 px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-teal/60"
            />
          </label>

          <label className="block">
            <span className="text-sm text-slate-300">Content</span>
            <textarea
              required
              rows={8}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="mt-1 w-full rounded-xl bg-white/5 border border-white/15 px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-teal/60"
            />
          </label>

          {error && (
            <div className="rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-100">
              {error}
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="submit"
              className="rounded-xl bg-teal px-4 py-3 text-ink font-semibold uppercase tracking-[0.08em]"
            >
              {editingId ? 'Update item' : 'Add item'}
            </button>
            {editingId && (
              <button
                type="button"
                onClick={resetForm}
                className="rounded-xl border border-white/20 px-4 py-3 text-slate-200"
              >
                Cancel edit
              </button>
            )}
          </div>
        </form>
      </section>

      <section className="glass rounded-3xl p-6 card-border">
        <h2 className="text-2xl font-semibold text-white">Your saved data</h2>
        <p className="mt-2 text-sm text-slate-300">Stored per user session and account.</p>

        {loading ? (
          <p className="mt-6 text-slate-300">Loading...</p>
        ) : items.length === 0 ? (
          <p className="mt-6 text-slate-400">No data entries yet.</p>
        ) : (
          <div className="mt-6 space-y-4">
            {items.map((item) => (
              <article key={item.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold text-white">{item.title}</h3>
                    <p className="text-xs text-slate-400 mt-1">Updated {formatDate(item.updated_at)}</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => startEdit(item)}
                      className="text-xs rounded-lg border border-white/20 px-3 py-1.5 text-slate-200"
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      onClick={() => remove(item.id)}
                      className="text-xs rounded-lg border border-red-400/40 px-3 py-1.5 text-red-200"
                    >
                      Delete
                    </button>
                  </div>
                </div>
                <p className="mt-3 text-sm text-slate-200 whitespace-pre-wrap">{item.content}</p>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
