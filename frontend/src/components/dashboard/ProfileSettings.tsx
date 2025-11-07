'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  User,
  Mail,
  Building2,
  Key,
  Bell,
  Download,
  CreditCard,
  BarChart3,
  Save,
  Loader,
} from 'lucide-react'
import { User as UserType } from '@/lib/types'

interface ProfileSettingsProps {
  user: UserType
  onSave?: (updates: Partial<UserType>) => Promise<void>
}

const ProfileSettings: React.FC<ProfileSettingsProps> = ({ user, onSave }) => {
  const [activeTab, setActiveTab] = useState<'profile' | 'notifications' | 'preferences' | 'billing'>('profile')
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: user.name,
    email: user.email,
    institution: user.institution || '',
  })
  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    projectCompletions: true,
    weeklyDigest: false,
    errorAlerts: true,
  })
  const [exportPreferences, setExportPreferences] = useState({
    defaultFormat: 'json' as 'json' | 'csv' | 'pdf',
    includeMetadata: true,
    compressFiles: false,
  })

  const handleSave = async () => {
    setLoading(true)
    try {
      await onSave?.(formData)
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'preferences', label: 'Preferences', icon: Download },
    { id: 'billing', label: 'Usage & Billing', icon: CreditCard },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
        <p className="text-gray-600 mt-1">Manage your account settings and preferences</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-2">
          {tabs.map((tab) => {
            const TabIcon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`
                  relative px-6 py-3 font-medium transition-all
                  ${activeTab === tab.id ? 'text-primary-600' : 'text-gray-600 hover:text-gray-900'}
                `}
              >
                <span className="flex items-center gap-2">
                  <TabIcon className="w-4 h-4" />
                  {tab.label}
                </span>
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeSettingsTab"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600"
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  />
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'profile' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Institution</label>
                  <input
                    type="text"
                    value={formData.institution}
                    onChange={(e) => setFormData({ ...formData, institution: e.target.value })}
                    className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                    placeholder="Your institution or organization"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end">
              <motion.button
                onClick={handleSave}
                disabled={loading}
                className="px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                whileHover={{ scale: loading ? 1 : 1.05 }}
                whileTap={{ scale: loading ? 1 : 0.95 }}
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <Loader className="w-5 h-5 animate-spin" />
                    Saving...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Save className="w-5 h-5" />
                    Save Changes
                  </span>
                )}
              </motion.button>
            </div>
          </motion.div>
        )}

        {activeTab === 'notifications' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h3>
            <div className="space-y-4">
              {Object.entries(notificationSettings).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">
                      {key.replace(/([A-Z])/g, ' $1').replace(/^./, (str) => str.toUpperCase())}
                    </h4>
                    <p className="text-xs text-gray-600 mt-1">
                      Receive notifications for this event
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={(e) =>
                        setNotificationSettings({ ...notificationSettings, [key]: e.target.checked })
                      }
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {activeTab === 'preferences' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Preferences</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Default Export Format</label>
                <select
                  value={exportPreferences.defaultFormat}
                  onChange={(e) =>
                    setExportPreferences({ ...exportPreferences, defaultFormat: e.target.value as any })
                  }
                  className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                >
                  <option value="json">JSON</option>
                  <option value="csv">CSV</option>
                  <option value="pdf">PDF</option>
                </select>
              </div>
              <div className="flex items-center justify-between py-3 border-b border-gray-100">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Include Metadata</h4>
                  <p className="text-xs text-gray-600 mt-1">Add project metadata to exports</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={exportPreferences.includeMetadata}
                    onChange={(e) =>
                      setExportPreferences({ ...exportPreferences, includeMetadata: e.target.checked })
                    }
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'billing' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="p-6 bg-white/60 backdrop-blur-sm border border-gray-200 rounded-2xl">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">API Usage Statistics</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 bg-blue-50 rounded-xl">
                  <div className="text-sm text-gray-600 mb-1">Projects Created</div>
                  <div className="text-2xl font-bold text-gray-900">127</div>
                </div>
                <div className="p-4 bg-green-50 rounded-xl">
                  <div className="text-sm text-gray-600 mb-1">API Calls</div>
                  <div className="text-2xl font-bold text-gray-900">8,542</div>
                </div>
                <div className="p-4 bg-purple-50 rounded-xl">
                  <div className="text-sm text-gray-600 mb-1">Storage Used</div>
                  <div className="text-2xl font-bold text-gray-900">2.4 GB</div>
                </div>
              </div>
            </div>

            <div className="p-6 bg-gradient-to-br from-primary-500/10 to-primary-600/10 backdrop-blur-sm border border-primary-200 rounded-2xl">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Current Plan: Free</h3>
              <p className="text-gray-600 mb-4">Upgrade to unlock more features and higher limits</p>
              <button className="px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 transition-all">
                Upgrade Plan
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default ProfileSettings
