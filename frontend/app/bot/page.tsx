'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import api from '@/lib/api';
import toast from 'react-hot-toast';
import { Bot } from '@/types';

export default function BotManagementPage() {
  const [bots, setBots] = useState<Bot[]>([]);
  const [selectedBot, setSelectedBot] = useState<Bot | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBots();
  }, []);

  const fetchBots = async () => {
    try {
      const response = await api.get('/bots/');
      setBots(response.data.bots);
      if (response.data.bots.length > 0) {
        setSelectedBot(response.data.bots[0]);
      }
    } catch (error) {
      toast.error('Failed to load bots');
    } finally {
      setLoading(false);
    }
  };

  const updateBot = async (updates: Partial<Bot>) => {
    if (!selectedBot) return;

    try {
      const response = await api.patch(`/bots/${selectedBot.bot_id}`, updates);
      setSelectedBot(response.data);
      toast.success('Bot updated successfully');
    } catch (error) {
      toast.error('Failed to update bot');
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div>Loading...</div>
      </DashboardLayout>
    );
  }

  if (!selectedBot) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <p className="text-gray-500">No bots found. Please complete onboarding.</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div>
        <h1 className="text-3xl font-bold mb-8">Bot Management</h1>

        <div className="grid grid-cols-3 gap-8">
          {/* Appearance Settings */}
          <div className="col-span-2 space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Appearance</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Bot Name</label>
                  <input
                    type="text"
                    value={selectedBot.name}
                    onChange={(e) =>
                      setSelectedBot({ ...selectedBot, name: e.target.value })
                    }
                    onBlur={() => updateBot({ name: selectedBot.name })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Primary Color</label>
                  <input
                    type="color"
                    value={selectedBot.primary_color}
                    onChange={(e) => {
                      const color = e.target.value;
                      setSelectedBot({ ...selectedBot, primary_color: color });
                      updateBot({ primary_color: color });
                    }}
                    className="w-full h-12 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Welcome Message</label>
                  <textarea
                    value={selectedBot.welcome_message}
                    onChange={(e) =>
                      setSelectedBot({
                        ...selectedBot,
                        welcome_message: e.target.value,
                      })
                    }
                    onBlur={() =>
                      updateBot({ welcome_message: selectedBot.welcome_message })
                    }
                    className="w-full px-4 py-2 border rounded-lg"
                    rows={3}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Position</label>
                  <select
                    value={selectedBot.position}
                    onChange={(e) => {
                      const position = e.target.value as 'left' | 'right';
                      setSelectedBot({ ...selectedBot, position });
                      updateBot({ position });
                    }}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="right">Bottom Right</option>
                    <option value="left">Bottom Left</option>
                  </select>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedBot.is_online}
                    onChange={(e) => {
                      const is_online = e.target.checked;
                      setSelectedBot({ ...selectedBot, is_online });
                      updateBot({ is_online });
                    }}
                    className="mr-2"
                  />
                  <label className="text-sm font-medium">Bot is Online</label>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">AI Configuration</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Model</label>
                  <select
                    value={selectedBot.model_name}
                    onChange={(e) => {
                      const model_name = e.target.value;
                      setSelectedBot({ ...selectedBot, model_name });
                      updateBot({ model_name });
                    }}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-4-turbo">GPT-4 Turbo</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Temperature: {selectedBot.temperature}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={selectedBot.temperature}
                    onChange={(e) => {
                      const temperature = parseFloat(e.target.value);
                      setSelectedBot({ ...selectedBot, temperature });
                    }}
                    onMouseUp={() =>
                      updateBot({ temperature: selectedBot.temperature })
                    }
                    className="w-full"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Widget Preview */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Widget Preview</h2>
            <div className="bg-gray-100 rounded-lg p-4 aspect-square relative">
              <div className="absolute bottom-4 right-4">
                <div
                  className="rounded-full p-4 shadow-lg cursor-pointer"
                  style={{ backgroundColor: selectedBot.primary_color }}
                >
                  <svg
                    className="w-6 h-6 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                    />
                  </svg>
                </div>
              </div>
            </div>
            <div className="mt-4">
              <p className="text-sm text-gray-600 mb-2">Widget Code:</p>
              <button
                onClick={async () => {
                  try {
                    const response = await api.get(
                      `/bots/${selectedBot.bot_id}/widget-code`
                    );
                    navigator.clipboard.writeText(response.data.widget_script);
                    toast.success('Widget code copied!');
                  } catch (error) {
                    toast.error('Failed to get widget code');
                  }
                }}
                className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700"
              >
                Copy Widget Code
              </button>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
