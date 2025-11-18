'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import api from '@/lib/api';
import { Lead } from '@/types';
import { formatDate } from '@/lib/utils';
import { Download, Mail, Phone, Building } from 'lucide-react';
import toast from 'react-hot-toast';

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const response = await api.get('/leads/');
      setLeads(response.data.leads);
    } catch (error) {
      console.error('Error fetching leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      const response = await api.get('/leads/export/csv', {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `leads_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Leads exported successfully');
    } catch (error) {
      toast.error('Failed to export leads');
    }
  };

  return (
    <DashboardLayout>
      <div>
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Leads</h1>
          <button
            onClick={handleExportCSV}
            className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </button>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Contact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Source
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">
                      {lead.name || 'N/A'}
                    </div>
                    {lead.company && (
                      <div className="flex items-center text-sm text-gray-500 mt-1">
                        <Building className="w-3 h-3 mr-1" />
                        {lead.company}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    {lead.email && (
                      <div className="flex items-center text-sm text-gray-900 mb-1">
                        <Mail className="w-3 h-3 mr-2" />
                        {lead.email}
                      </div>
                    )}
                    {lead.phone && (
                      <div className="flex items-center text-sm text-gray-500">
                        <Phone className="w-3 h-3 mr-2" />
                        {lead.phone}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    <div className="truncate max-w-xs">
                      {lead.source_url || 'N/A'}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {formatDate(lead.created_at)}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2">
                      {lead.is_qualified && (
                        <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded">
                          Qualified
                        </span>
                      )}
                      {lead.is_contacted && (
                        <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
                          Contacted
                        </span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {leads.length === 0 && !loading && (
            <div className="text-center py-12 text-gray-500">
              No leads yet
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
