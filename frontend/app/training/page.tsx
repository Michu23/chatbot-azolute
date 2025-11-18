'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import api from '@/lib/api';
import toast from 'react-hot-toast';
import { KnowledgeSource, Bot } from '@/types';
import { FileText, Link as LinkIcon, Upload } from 'lucide-react';

export default function TrainingPage() {
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [bots, setBots] = useState<Bot[]>([]);
  const [selectedBotId, setSelectedBotId] = useState<number | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newSource, setNewSource] = useState({
    type: 'url' as 'url' | 'text',
    name: '',
    url: '',
    content: '',
  });

  useEffect(() => {
    fetchBots();
  }, []);

  useEffect(() => {
    if (selectedBotId) {
      fetchSources();
    }
  }, [selectedBotId]);

  const fetchBots = async () => {
    try {
      const response = await api.get('/bots/');
      setBots(response.data.bots);
      if (response.data.bots.length > 0) {
        setSelectedBotId(response.data.bots[0].id);
      }
    } catch (error) {
      toast.error('Failed to load bots');
    }
  };

  const fetchSources = async () => {
    try {
      const response = await api.get(`/knowledge/bot/${selectedBotId}`);
      setSources(response.data.sources);
    } catch (error) {
      toast.error('Failed to load knowledge sources');
    }
  };

  const handleAddSource = async () => {
    if (!selectedBotId) return;

    try {
      await api.post('/knowledge/', {
        bot_id: selectedBotId,
        source_type: newSource.type,
        name: newSource.name,
        url: newSource.type === 'url' ? newSource.url : null,
        content: newSource.type === 'text' ? newSource.content : null,
      });

      toast.success('Knowledge source added successfully');
      setShowAddModal(false);
      setNewSource({ type: 'url', name: '', url: '', content: '' });
      fetchSources();
    } catch (error) {
      toast.error('Failed to add knowledge source');
    }
  };

  return (
    <DashboardLayout>
      <div>
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Knowledge Base</h1>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Add Source
          </button>
        </div>

        {bots.length > 0 && (
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Select Bot</label>
            <select
              value={selectedBotId || ''}
              onChange={(e) => setSelectedBotId(parseInt(e.target.value))}
              className="px-4 py-2 border rounded-lg"
            >
              {bots.map((bot) => (
                <option key={bot.id} value={bot.id}>
                  {bot.name}
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sources.map((source) => (
            <div key={source.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  {source.source_type === 'url' ? (
                    <LinkIcon className="w-5 h-5 text-indigo-600 mr-2" />
                  ) : (
                    <FileText className="w-5 h-5 text-indigo-600 mr-2" />
                  )}
                  <h3 className="font-semibold">{source.name}</h3>
                </div>
                <span
                  className={`px-2 py-1 text-xs rounded ${
                    source.status === 'completed'
                      ? 'bg-green-100 text-green-700'
                      : source.status === 'processing'
                      ? 'bg-yellow-100 text-yellow-700'
                      : source.status === 'failed'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {source.status}
                </span>
              </div>
              {source.url && (
                <p className="text-sm text-gray-600 truncate mb-2">
                  {source.url}
                </p>
              )}
              <p className="text-sm text-gray-500">
                {source.total_chunks} chunks indexed
              </p>
            </div>
          ))}
        </div>

        {showAddModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold mb-4">Add Knowledge Source</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Type</label>
                  <select
                    value={newSource.type}
                    onChange={(e) =>
                      setNewSource({
                        ...newSource,
                        type: e.target.value as 'url' | 'text',
                      })
                    }
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="url">Website URL</option>
                    <option value="text">Text/FAQ</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Name</label>
                  <input
                    type="text"
                    value={newSource.name}
                    onChange={(e) =>
                      setNewSource({ ...newSource, name: e.target.value })
                    }
                    className="w-full px-4 py-2 border rounded-lg"
                    placeholder="e.g., About Page"
                  />
                </div>

                {newSource.type === 'url' ? (
                  <div>
                    <label className="block text-sm font-medium mb-2">URL</label>
                    <input
                      type="url"
                      value={newSource.url}
                      onChange={(e) =>
                        setNewSource({ ...newSource, url: e.target.value })
                      }
                      className="w-full px-4 py-2 border rounded-lg"
                      placeholder="https://example.com/about"
                    />
                  </div>
                ) : (
                  <div>
                    <label className="block text-sm font-medium mb-2">Content</label>
                    <textarea
                      value={newSource.content}
                      onChange={(e) =>
                        setNewSource({ ...newSource, content: e.target.value })
                      }
                      className="w-full px-4 py-2 border rounded-lg"
                      rows={6}
                      placeholder="Enter your content here..."
                    />
                  </div>
                )}
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddSource}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Add Source
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
