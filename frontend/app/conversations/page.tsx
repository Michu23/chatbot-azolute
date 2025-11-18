'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import api from '@/lib/api';
import { ChatSession, ChatMessage } from '@/types';
import { formatRelativeTime } from '@/lib/utils';

export default function ConversationsPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<ChatSession | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await api.get('/chat/sessions');
      setSessions(response.data);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSession = async (sessionId: string) => {
    try {
      const response = await api.get(`/chat/sessions/${sessionId}`);
      setSelectedSession(response.data);
    } catch (error) {
      console.error('Error loading session:', error);
    }
  };

  return (
    <DashboardLayout>
      <h1 className="text-3xl font-bold mb-8">Conversations</h1>

      <div className="grid grid-cols-12 gap-6">
        {/* Sessions List */}
        <div className="col-span-4 bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="font-semibold">All Conversations</h2>
          </div>
          <div className="overflow-y-auto max-h-[calc(100vh-16rem)]">
            {sessions.map((session) => (
              <div
                key={session.id}
                onClick={() => loadSession(session.session_id)}
                className={`p-4 border-b cursor-pointer hover:bg-gray-50 ${
                  selectedSession?.id === session.id ? 'bg-indigo-50' : ''
                }`}
              >
                <div className="flex justify-between items-start mb-1">
                  <div className="font-medium truncate">
                    {session.visitor_name || session.visitor_email || 'Anonymous'}
                  </div>
                  <div className="text-xs text-gray-500">
                    {formatRelativeTime(session.created_at)}
                  </div>
                </div>
                <div className="text-sm text-gray-600 truncate">
                  {session.source_url || 'No source'}
                </div>
                {session.is_lead && (
                  <span className="inline-block mt-1 px-2 py-1 text-xs bg-green-100 text-green-700 rounded">
                    Lead
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Messages Panel */}
        <div className="col-span-8 bg-white rounded-lg shadow">
          {selectedSession ? (
            <>
              <div className="p-4 border-b">
                <h2 className="font-semibold">
                  {selectedSession.visitor_name ||
                    selectedSession.visitor_email ||
                    'Anonymous User'}
                </h2>
                <p className="text-sm text-gray-600">
                  {selectedSession.source_url}
                </p>
              </div>
              <div className="p-4 space-y-4 overflow-y-auto max-h-[calc(100vh-20rem)]">
                {selectedSession.messages?.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-[70%] rounded-lg p-3 ${
                        message.role === 'user'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      <p className="text-xs mt-1 opacity-70">
                        {formatRelativeTime(message.created_at)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
              Select a conversation to view messages
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
