'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import api from '@/lib/api';
import { DashboardAnalytics } from '@/types';
import { MessageSquare, Users, Mail, TrendingUp } from 'lucide-react';

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/dashboard/stats?days=7');
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading...</div>
        </div>
      </DashboardLayout>
    );
  }

  const stats = analytics?.stats;

  return (
    <DashboardLayout>
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Conversations"
            value={stats?.total_conversations || 0}
            icon={MessageSquare}
            color="bg-blue-500"
          />
          <StatCard
            title="Total Users"
            value={stats?.total_users || 0}
            icon={Users}
            color="bg-green-500"
          />
          <StatCard
            title="Messages"
            value={stats?.total_messages || 0}
            icon={TrendingUp}
            color="bg-purple-500"
          />
          <StatCard
            title="Leads Collected"
            value={stats?.leads_collected || 0}
            icon={Mail}
            color="bg-orange-500"
          />
        </div>

        {/* Conversation Trends */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">
            Last 7 Days Conversations
          </h2>
          <div className="h-64 flex items-end justify-between space-x-2">
            {analytics?.conversation_trends.map((trend, index) => {
              const maxCount = Math.max(
                ...analytics.conversation_trends.map((t) => t.count)
              );
              const height = maxCount > 0 ? (trend.count / maxCount) * 100 : 0;

              return (
                <div key={index} className="flex-1 flex flex-col items-center">
                  <div
                    className="w-full bg-indigo-500 rounded-t"
                    style={{ height: `${height}%`, minHeight: '4px' }}
                  />
                  <div className="text-xs text-gray-500 mt-2">
                    {new Date(trend.date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                    })}
                  </div>
                  <div className="text-sm font-medium">{trend.count}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Top Pages */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Top Pages</h2>
          {analytics?.top_pages && analytics.top_pages.length > 0 ? (
            <div className="space-y-3">
              {analytics.top_pages.map((page, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded"
                >
                  <div className="flex-1 truncate">
                    <div className="text-sm font-medium text-gray-900 truncate">
                      {page.url || 'Unknown'}
                    </div>
                  </div>
                  <div className="ml-4 text-sm font-semibold text-indigo-600">
                    {page.count} visits
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No data available</p>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  color,
}: {
  title: string;
  value: number;
  icon: any;
  color: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        <div className={`${color} p-3 rounded-lg`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );
}
