import React, { useState } from 'react'
import { motion } from 'framer-motion'
import Layout from '@/components/layout/Layout'
import { useAppStore } from '@/stores/useAppStore'
import {
  User,
  Mail,
  Key,
  Bell,
  Settings as SettingsIcon,
  Trash2,
  Eye,
  EyeOff,
  Save,
  Upload,
  CheckCircle2,
  AlertCircle,
  Shield,
  Sparkles,
  Moon,
  Sun,
  Microscope,
  Users,
  FileText,
  Lightbulb
} from 'lucide-react'

interface SettingsFormData {
  name: string
  email: string
  institution: string
  avatar?: string
  anthropicApiKey: string
  openaiApiKey: string
  emailNotifications: {
    projectUpdates: boolean
    workflowComplete: boolean
    weeklyDigest: boolean
    systemUpdates: boolean
  }
  preferences: {
    defaultTool: string
    autoSave: boolean
    theme: 'light' | 'dark' | 'system'
  }
}

const SettingsPage: React.FC = () => {
  const { user, darkMode, toggleDarkMode } = useAppStore()

  const [formData, setFormData] = useState<SettingsFormData>({
    name: user?.name || '',
    email: user?.email || '',
    institution: user?.institution || '',
    anthropicApiKey: '',
    openaiApiKey: '',
    emailNotifications: {
      projectUpdates: true,
      workflowComplete: true,
      weeklyDigest: false,
      systemUpdates: true
    },
    preferences: {
      defaultTool: 'meta_analysis',
      autoSave: true,
      theme: darkMode ? 'dark' : 'light'
    }
  })

  const [showKeys, setShowKeys] = useState({
    anthropic: false,
    openai: false
  })

  const [saveSuccess, setSaveSuccess] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleNestedChange = (parent: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [parent]: {
        ...(prev[parent as keyof SettingsFormData] as any),
        [field]: value
      }
    }))
  }

  const handleSaveSettings = async () => {
    setSaveSuccess(false)
    setSaveError(null)

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))

      // In a real app, save to backend here
      setSaveSuccess(true)

      setTimeout(() => setSaveSuccess(false), 3000)
    } catch (error) {
      setSaveError('Failed to save settings. Please try again.')
    }
  }

  const handleDeleteAccount = () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      // In a real app, call API to delete account
      console.log('Account deletion requested')
    }
  }

  const maskApiKey = (key: string) => {
    if (!key || key.length < 8) return '••••••••••••••••'
    return key.slice(0, 4) + '••••••••••••' + key.slice(-4)
  }

  const toolOptions = [
    { value: 'meta_analysis', label: 'Meta-Analysis', icon: Microscope, color: 'blue' },
    { value: 'reviewer_matcher', label: 'Reviewer Matcher', icon: Users, color: 'green' },
    { value: 'peer_review', label: 'Peer Review', icon: FileText, color: 'purple' },
    { value: 'research_direction', label: 'Research Direction', icon: Lightbulb, color: 'yellow' }
  ]

  return (
    <Layout title="Settings">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 text-white shadow-glow-primary">
              <SettingsIcon className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
              <p className="text-gray-600">Manage your account and preferences</p>
            </div>
          </div>
        </motion.div>

        {/* Save Success/Error Messages */}
        {saveSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 rounded-xl bg-green-50 border border-green-200 flex items-center gap-3"
          >
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            <span className="text-green-800 font-medium">Settings saved successfully!</span>
          </motion.div>
        )}

        {saveError && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 rounded-xl bg-red-50 border border-red-200 flex items-center gap-3"
          >
            <AlertCircle className="w-5 h-5 text-red-600" />
            <span className="text-red-800 font-medium">{saveError}</span>
          </motion.div>
        )}

        {/* Profile Section */}
        <motion.div
          className="bg-white/60 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-soft overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-primary-50 to-accent-50">
            <div className="flex items-center gap-3">
              <User className="w-5 h-5 text-primary-600" />
              <h2 className="text-xl font-semibold text-gray-900">Profile</h2>
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* Avatar Section */}
            <div className="flex items-start gap-6">
              <div className="relative">
                <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-3xl font-bold shadow-lg">
                  {formData.name.charAt(0).toUpperCase() || 'U'}
                </div>
                <button className="absolute -bottom-2 -right-2 p-2 rounded-lg bg-white border-2 border-gray-200 hover:border-primary-500 transition-colors shadow-md">
                  <Upload className="w-4 h-4 text-gray-600" />
                </button>
              </div>
              <div className="flex-1 space-y-1">
                <h3 className="text-sm font-medium text-gray-900">Profile Picture</h3>
                <p className="text-sm text-gray-600">Upload a profile picture to personalize your account</p>
                <p className="text-xs text-gray-500">JPG, PNG or GIF. Max size 2MB.</p>
              </div>
            </div>

            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                placeholder="Enter your full name"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                placeholder="your.email@example.com"
              />
            </div>

            {/* Institution */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Institution
              </label>
              <input
                type="text"
                value={formData.institution}
                onChange={(e) => handleInputChange('institution', e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                placeholder="Your university or organization"
              />
            </div>
          </div>
        </motion.div>

        {/* API Keys Section */}
        <motion.div
          className="bg-white/60 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-soft overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-purple-50 to-pink-50">
            <div className="flex items-center gap-3">
              <Key className="w-5 h-5 text-purple-600" />
              <div className="flex-1">
                <h2 className="text-xl font-semibold text-gray-900">API Keys</h2>
                <p className="text-sm text-gray-600 mt-1">Manage your AI provider API keys</p>
              </div>
              <Shield className="w-5 h-5 text-purple-400" />
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* Anthropic API Key */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Anthropic API Key
              </label>
              <div className="relative">
                <input
                  type={showKeys.anthropic ? 'text' : 'password'}
                  value={formData.anthropicApiKey || ''}
                  onChange={(e) => handleInputChange('anthropicApiKey', e.target.value)}
                  className="w-full px-4 py-3 pr-12 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all font-mono text-sm"
                  placeholder={showKeys.anthropic ? 'sk-ant-...' : maskApiKey('')}
                />
                <button
                  onClick={() => setShowKeys(prev => ({ ...prev, anthropic: !prev.anthropic }))}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  {showKeys.anthropic ? (
                    <EyeOff className="w-4 h-4 text-gray-500" />
                  ) : (
                    <Eye className="w-4 h-4 text-gray-500" />
                  )}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Required for using Claude AI models. Get your key from{' '}
                <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
                  console.anthropic.com
                </a>
              </p>
            </div>

            {/* OpenAI API Key */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OpenAI API Key
              </label>
              <div className="relative">
                <input
                  type={showKeys.openai ? 'text' : 'password'}
                  value={formData.openaiApiKey || ''}
                  onChange={(e) => handleInputChange('openaiApiKey', e.target.value)}
                  className="w-full px-4 py-3 pr-12 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all font-mono text-sm"
                  placeholder={showKeys.openai ? 'sk-...' : maskApiKey('')}
                />
                <button
                  onClick={() => setShowKeys(prev => ({ ...prev, openai: !prev.openai }))}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  {showKeys.openai ? (
                    <EyeOff className="w-4 h-4 text-gray-500" />
                  ) : (
                    <Eye className="w-4 h-4 text-gray-500" />
                  )}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Optional. Get your key from{' '}
                <a href="https://platform.openai.com" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
                  platform.openai.com
                </a>
              </p>
            </div>

            <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 flex gap-3">
              <Shield className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-blue-900 mb-1">Your API keys are secure</p>
                <p className="text-blue-700">
                  Keys are encrypted and stored securely. They are never shared with third parties.
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Notifications Section */}
        <motion.div
          className="bg-white/60 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-soft overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-green-50 to-teal-50">
            <div className="flex items-center gap-3">
              <Bell className="w-5 h-5 text-green-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Notifications</h2>
                <p className="text-sm text-gray-600 mt-1">Choose what updates you want to receive</p>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-4">
            {[
              {
                key: 'projectUpdates',
                label: 'Project Updates',
                description: 'Get notified when your projects have important updates'
              },
              {
                key: 'workflowComplete',
                label: 'Workflow Completion',
                description: 'Receive alerts when AI workflows finish processing'
              },
              {
                key: 'weeklyDigest',
                label: 'Weekly Digest',
                description: 'A summary of your activity and insights every Monday'
              },
              {
                key: 'systemUpdates',
                label: 'System Updates',
                description: 'Important announcements and new feature releases'
              }
            ].map((notification) => (
              <div
                key={notification.key}
                className="flex items-start gap-4 p-4 rounded-xl hover:bg-gray-50 transition-colors"
              >
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-gray-900">{notification.label}</h4>
                  <p className="text-sm text-gray-600 mt-0.5">{notification.description}</p>
                </div>
                <button
                  onClick={() => handleNestedChange('emailNotifications', notification.key, !formData.emailNotifications[notification.key as keyof typeof formData.emailNotifications])}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    formData.emailNotifications[notification.key as keyof typeof formData.emailNotifications]
                      ? 'bg-primary-600'
                      : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      formData.emailNotifications[notification.key as keyof typeof formData.emailNotifications]
                        ? 'translate-x-6'
                        : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Preferences Section */}
        <motion.div
          className="bg-white/60 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-soft overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-amber-50 to-orange-50">
            <div className="flex items-center gap-3">
              <Sparkles className="w-5 h-5 text-amber-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Preferences</h2>
                <p className="text-sm text-gray-600 mt-1">Customize your research experience</p>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-6">
            {/* Default Tool */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Default Tool
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {toolOptions.map((tool) => {
                  const Icon = tool.icon
                  const isSelected = formData.preferences.defaultTool === tool.value
                  return (
                    <button
                      key={tool.value}
                      onClick={() => handleNestedChange('preferences', 'defaultTool', tool.value)}
                      className={`p-4 rounded-xl border-2 transition-all text-left ${
                        isSelected
                          ? `border-${tool.color}-500 bg-${tool.color}-50`
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${isSelected ? `bg-${tool.color}-100` : 'bg-gray-100'}`}>
                          <Icon className={`w-5 h-5 ${isSelected ? `text-${tool.color}-600` : 'text-gray-600'}`} />
                        </div>
                        <span className={`font-medium ${isSelected ? `text-${tool.color}-900` : 'text-gray-900'}`}>
                          {tool.label}
                        </span>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Auto-save */}
            <div className="flex items-start gap-4 p-4 rounded-xl hover:bg-gray-50 transition-colors">
              <div className="flex-1">
                <h4 className="text-sm font-medium text-gray-900">Auto-save</h4>
                <p className="text-sm text-gray-600 mt-0.5">
                  Automatically save your work as you go
                </p>
              </div>
              <button
                onClick={() => handleNestedChange('preferences', 'autoSave', !formData.preferences.autoSave)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  formData.preferences.autoSave ? 'bg-primary-600' : 'bg-gray-300'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    formData.preferences.autoSave ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            {/* Theme */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Theme
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { value: 'light', label: 'Light', icon: Sun },
                  { value: 'dark', label: 'Dark', icon: Moon },
                  { value: 'system', label: 'System', icon: SettingsIcon }
                ].map((theme) => {
                  const Icon = theme.icon
                  const isSelected = formData.preferences.theme === theme.value
                  return (
                    <button
                      key={theme.value}
                      onClick={() => handleNestedChange('preferences', 'theme', theme.value)}
                      className={`p-4 rounded-xl border-2 transition-all ${
                        isSelected
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <Icon className={`w-5 h-5 mx-auto mb-2 ${isSelected ? 'text-primary-600' : 'text-gray-600'}`} />
                      <span className={`text-sm font-medium block ${isSelected ? 'text-primary-900' : 'text-gray-900'}`}>
                        {theme.label}
                      </span>
                    </button>
                  )
                })}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Danger Zone */}
        <motion.div
          className="bg-white/60 backdrop-blur-sm rounded-2xl border-2 border-red-200 shadow-soft overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <div className="p-6 border-b border-red-200 bg-gradient-to-r from-red-50 to-pink-50">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Danger Zone</h2>
                <p className="text-sm text-gray-600 mt-1">Irreversible account actions</p>
              </div>
            </div>
          </div>

          <div className="p-6">
            <div className="p-4 rounded-xl border-2 border-red-200 bg-red-50">
              <div className="flex items-start gap-4">
                <Trash2 className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h4 className="text-sm font-semibold text-red-900 mb-1">Delete Account</h4>
                  <p className="text-sm text-red-700 mb-4">
                    Once you delete your account, there is no going back. All your projects, data, and settings will be permanently deleted.
                  </p>
                  <button
                    onClick={handleDeleteAccount}
                    className="px-4 py-2 rounded-lg bg-red-600 text-white font-medium hover:bg-red-700 transition-colors text-sm"
                  >
                    Delete Account
                  </button>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Save Button */}
        <motion.div
          className="sticky bottom-6 flex justify-end"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <button
            onClick={handleSaveSettings}
            className="group px-8 py-4 rounded-xl bg-gradient-to-r from-primary-600 to-accent-600 text-white font-semibold shadow-lg hover:shadow-glow-primary transition-all duration-300 flex items-center gap-3"
          >
            <Save className="w-5 h-5 group-hover:scale-110 transition-transform" />
            Save All Changes
          </button>
        </motion.div>
      </div>
    </Layout>
  )
}

export default SettingsPage
