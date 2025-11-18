'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import api from '@/lib/api';
import toast from 'react-hot-toast';
import { User } from '@/types';

export default function SettingsPage() {
  const [user, setUser] = useState<User | null>(null);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    current_password: '',
    new_password: '',
  });

  useEffect(() => {
    fetchUser();
  }, []);

  const fetchUser = async () => {
    try {
      const response = await api.get('/users/me');
      setUser(response.data);
      setFormData({
        ...formData,
        full_name: response.data.full_name || '',
        email: response.data.email,
      });
    } catch (error) {
      console.error('Error fetching user:', error);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.patch('/users/me', {
        full_name: formData.full_name,
        email: formData.email,
      });
      toast.success('Profile updated successfully');
      fetchUser();
    } catch (error) {
      toast.error('Failed to update profile');
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.new_password) {
      toast.error('Please enter a new password');
      return;
    }
    try {
      await api.patch('/users/me', {
        password: formData.new_password,
      });
      toast.success('Password changed successfully');
      setFormData({ ...formData, current_password: '', new_password: '' });
    } catch (error) {
      toast.error('Failed to change password');
    }
  };

  return (
    <DashboardLayout>
      <div>
        <h1 className="text-3xl font-bold mb-8">Settings</h1>

        <div className="max-w-2xl space-y-6">
          {/* Profile Settings */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Profile Settings</h2>
            <form onSubmit={handleUpdateProfile} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) =>
                    setFormData({ ...formData, full_name: e.target.value })
                  }
                  className="w-full px-4 py-2 border rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  className="w-full px-4 py-2 border rounded-lg"
                />
              </div>
              <button
                type="submit"
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Update Profile
              </button>
            </form>
          </div>

          {/* Password Change */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Change Password</h2>
            <form onSubmit={handleChangePassword} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  New Password
                </label>
                <input
                  type="password"
                  value={formData.new_password}
                  onChange={(e) =>
                    setFormData({ ...formData, new_password: e.target.value })
                  }
                  className="w-full px-4 py-2 border rounded-lg"
                  minLength={8}
                />
              </div>
              <button
                type="submit"
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Change Password
              </button>
            </form>
          </div>

          {/* Account Info */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Account Information</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Account Status:</span>
                <span className="font-medium">
                  {user?.is_verified ? 'Verified' : 'Not Verified'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Member Since:</span>
                <span className="font-medium">
                  {user?.created_at
                    ? new Date(user.created_at).toLocaleDateString()
                    : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
