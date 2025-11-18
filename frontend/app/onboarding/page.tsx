'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import toast from 'react-hot-toast';

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    personality: 'friendly',
    custom_persona: '',
    business_name: '',
    website_domain: '',
    primary_color: '#6366f1',
    bot_name: 'AI Assistant',
    welcome_message: 'Hello! How can I help you today?',
    urls: '',
    faqs: '',
  });

  const handleComplete = async () => {
    setLoading(true);
    try {
      const response = await api.post('/organizations/onboarding', {
        step1: {
          personality: formData.personality,
          custom_persona: formData.custom_persona || null,
        },
        step2: {
          business_name: formData.business_name,
          website_domain: formData.website_domain || null,
          primary_color: formData.primary_color,
          bot_name: formData.bot_name,
          welcome_message: formData.welcome_message,
        },
        step3: {
          urls: formData.urls ? formData.urls.split('\n').filter(u => u.trim()) : [],
          faqs: [],
        },
      });

      toast.success('Setup complete!');
      router.push('/dashboard');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Onboarding failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Welcome to Azolute AI!</h1>
          <p className="text-gray-600 mt-2">Let's set up your chatbot in 3 easy steps</p>
        </div>

        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={`flex-1 h-2 mx-1 rounded ${
                  s <= step ? 'bg-indigo-600' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
          <div className="text-center text-sm text-gray-600">
            Step {step} of 3
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-8">
          {step === 1 && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Choose Bot Personality</h2>
              <div className="space-y-4">
                {[
                  { value: 'friendly', label: 'Friendly', desc: 'Warm and approachable' },
                  { value: 'professional', label: 'Professional', desc: 'Formal and business-like' },
                  { value: 'sales_focused', label: 'Sales-Focused', desc: 'Persuasive and conversion-oriented' },
                  { value: 'custom', label: 'Custom', desc: 'Define your own personality' },
                ].map((option) => (
                  <label
                    key={option.value}
                    className={`block p-4 border-2 rounded-lg cursor-pointer transition ${
                      formData.personality === option.value
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="personality"
                      value={option.value}
                      checked={formData.personality === option.value}
                      onChange={(e) =>
                        setFormData({ ...formData, personality: e.target.value })
                      }
                      className="mr-3"
                    />
                    <span className="font-medium">{option.label}</span>
                    <p className="text-sm text-gray-600 ml-6">{option.desc}</p>
                  </label>
                ))}
              </div>
              {formData.personality === 'custom' && (
                <textarea
                  value={formData.custom_persona}
                  onChange={(e) =>
                    setFormData({ ...formData, custom_persona: e.target.value })
                  }
                  className="w-full mt-4 px-4 py-2 border rounded-lg"
                  rows={4}
                  placeholder="Describe your bot's personality..."
                />
              )}
            </div>
          )}

          {step === 2 && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Basic Setup</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Business Name *</label>
                  <input
                    type="text"
                    value={formData.business_name}
                    onChange={(e) =>
                      setFormData({ ...formData, business_name: e.target.value })
                    }
                    className="w-full px-4 py-2 border rounded-lg"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Website Domain</label>
                  <input
                    type="text"
                    value={formData.website_domain}
                    onChange={(e) =>
                      setFormData({ ...formData, website_domain: e.target.value })
                    }
                    className="w-full px-4 py-2 border rounded-lg"
                    placeholder="example.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Primary Brand Color</label>
                  <input
                    type="color"
                    value={formData.primary_color}
                    onChange={(e) =>
                      setFormData({ ...formData, primary_color: e.target.value })
                    }
                    className="w-full h-12 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Bot Name</label>
                  <input
                    type="text"
                    value={formData.bot_name}
                    onChange={(e) =>
                      setFormData({ ...formData, bot_name: e.target.value })
                    }
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Welcome Message</label>
                  <textarea
                    value={formData.welcome_message}
                    onChange={(e) =>
                      setFormData({ ...formData, welcome_message: e.target.value })
                    }
                    className="w-full px-4 py-2 border rounded-lg"
                    rows={3}
                  />
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Knowledge Upload (Optional)</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Website URLs (one per line)
                  </label>
                  <textarea
                    value={formData.urls}
                    onChange={(e) =>
                      setFormData({ ...formData, urls: e.target.value })
                    }
                    className="w-full px-4 py-2 border rounded-lg"
                    rows={5}
                    placeholder="https://example.com/about&#10;https://example.com/faq"
                  />
                </div>
                <p className="text-sm text-gray-500">
                  You can add more knowledge sources later from the Training page
                </p>
              </div>
            </div>
          )}

          <div className="flex justify-between mt-8">
            <button
              onClick={() => setStep(Math.max(1, step - 1))}
              disabled={step === 1}
              className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Back
            </button>
            {step < 3 ? (
              <button
                onClick={() => setStep(step + 1)}
                disabled={step === 2 && !formData.business_name}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleComplete}
                disabled={loading}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {loading ? 'Completing...' : 'Complete Setup'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
