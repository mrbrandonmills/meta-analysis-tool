import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Activity,
  UserPlus,
  FileText,
  DollarSign,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Clock,
  Filter,
  RefreshCw
} from 'lucide-react';
import { formatRelativeTime } from '@/lib/utils';

interface ActivityItem {
  id: string;
  timestamp: string;
  type: 'signup' | 'review_submitted' | 'payout_processed' | 'subscription' | 'paper_uploaded' | 'review_approved' | 'system';
  description: string;
  metadata?: {
    userId?: string;
    userName?: string;
    amount?: number;
    reviewId?: string;
    paperId?: string;
  };
}

interface ActivityFeedProps {
  activities?: ActivityItem[];
  onRefresh?: () => void;
  refreshing?: boolean;
  autoRefresh?: boolean;
  autoRefreshInterval?: number; // in seconds
}

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'signup':
      return <UserPlus className="w-4 h-4" />;
    case 'review_submitted':
      return <FileText className="w-4 h-4" />;
    case 'payout_processed':
      return <DollarSign className="w-4 h-4" />;
    case 'subscription':
      return <TrendingUp className="w-4 h-4" />;
    case 'paper_uploaded':
      return <FileText className="w-4 h-4" />;
    case 'review_approved':
      return <CheckCircle2 className="w-4 h-4" />;
    case 'system':
      return <AlertCircle className="w-4 h-4" />;
    default:
      return <Activity className="w-4 h-4" />;
  }
};

const getActivityColor = (type: string) => {
  switch (type) {
    case 'signup':
      return 'bg-green-100 text-green-600 border-green-200';
    case 'review_submitted':
      return 'bg-blue-100 text-blue-600 border-blue-200';
    case 'payout_processed':
      return 'bg-purple-100 text-purple-600 border-purple-200';
    case 'subscription':
      return 'bg-orange-100 text-orange-600 border-orange-200';
    case 'paper_uploaded':
      return 'bg-indigo-100 text-indigo-600 border-indigo-200';
    case 'review_approved':
      return 'bg-emerald-100 text-emerald-600 border-emerald-200';
    case 'system':
      return 'bg-gray-100 text-gray-600 border-gray-200';
    default:
      return 'bg-gray-100 text-gray-600 border-gray-200';
  }
};

// Generate mock activities for demonstration
const generateMockActivities = (): ActivityItem[] => {
  const now = new Date();
  const activities: ActivityItem[] = [];

  const templates = [
    { type: 'signup' as const, desc: (name: string) => `${name} joined the platform` },
    { type: 'review_submitted' as const, desc: (name: string) => `${name} submitted a review` },
    { type: 'payout_processed' as const, desc: (name: string, amount: number) => `Processed $${amount.toFixed(2)} payout to ${name}` },
    { type: 'subscription' as const, desc: (name: string) => `${name} upgraded to Premium` },
    { type: 'paper_uploaded' as const, desc: (name: string) => `${name} uploaded a new paper` },
    { type: 'review_approved' as const, desc: (name: string) => `Review by ${name} was approved` },
  ];

  const names = [
    'Dr. Sarah Johnson', 'Prof. Michael Chen', 'Dr. Emily Rodriguez',
    'Dr. James Wilson', 'Prof. Anna Kowalski', 'Dr. Robert Taylor',
    'Dr. Maria Garcia', 'Prof. David Kim', 'Dr. Lisa Anderson'
  ];

  for (let i = 0; i < 20; i++) {
    const template = templates[Math.floor(Math.random() * templates.length)];
    const name = names[Math.floor(Math.random() * names.length)];
    const amount = 50 + Math.random() * 200;
    const minutesAgo = i * 5 + Math.floor(Math.random() * 5);
    const timestamp = new Date(now.getTime() - minutesAgo * 60000);

    activities.push({
      id: `activity-${i}`,
      timestamp: timestamp.toISOString(),
      type: template.type,
      description: template.type === 'payout_processed'
        ? template.desc(name, amount)
        : template.desc(name),
      metadata: {
        userName: name,
        ...(template.type === 'payout_processed' && { amount })
      }
    });
  }

  return activities;
};

export const ActivityFeed: React.FC<ActivityFeedProps> = ({
  activities: providedActivities,
  onRefresh,
  refreshing = false,
  autoRefresh = false,
  autoRefreshInterval = 30
}) => {
  const [activities, setActivities] = useState<ActivityItem[]>(
    providedActivities || generateMockActivities()
  );
  const [filter, setFilter] = useState<string>('all');
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Auto-refresh functionality
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        if (onRefresh) {
          onRefresh();
        }
        setLastUpdate(new Date());
      }, autoRefreshInterval * 1000);

      return () => clearInterval(interval);
    }
  }, [autoRefresh, autoRefreshInterval, onRefresh]);

  // Update activities when provided activities change
  useEffect(() => {
    if (providedActivities) {
      setActivities(providedActivities);
    }
  }, [providedActivities]);

  const filteredActivities = filter === 'all'
    ? activities
    : activities.filter(a => a.type === filter);

  const activityTypes = [
    { value: 'all', label: 'All Activity' },
    { value: 'signup', label: 'Signups' },
    { value: 'review_submitted', label: 'Reviews' },
    { value: 'payout_processed', label: 'Payouts' },
    { value: 'subscription', label: 'Subscriptions' },
  ];

  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh();
    } else {
      // Generate new mock data
      setActivities(generateMockActivities());
    }
    setLastUpdate(new Date());
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-blue-100 text-blue-600">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">Activity Feed</h3>
            <p className="text-sm text-gray-600">
              Real-time platform activity
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Clock className="w-4 h-4" />
            <span>Updated {formatRelativeTime(lastUpdate)}</span>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className={`p-2 rounded-lg border-2 border-gray-300 hover:bg-gray-50 transition-colors ${
              refreshing ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            aria-label="Refresh activity feed"
          >
            <RefreshCw className={`w-5 h-5 text-gray-600 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="w-4 h-4 text-gray-600" />
        {activityTypes.map((type) => (
          <button
            key={type.value}
            onClick={() => setFilter(type.value)}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              filter === type.value
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-white border-2 border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            {type.label}
            {type.value !== 'all' && (
              <span className="ml-2 px-2 py-0.5 rounded-full bg-white bg-opacity-20 text-xs">
                {activities.filter(a => a.type === type.value).length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Activity List */}
      <div className="bg-white rounded-2xl border-2 border-gray-200 overflow-hidden">
        <div className="max-h-[600px] overflow-y-auto">
          <AnimatePresence mode="popLayout">
            {filteredActivities.length === 0 ? (
              <motion.div
                className="p-12 text-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <div className="p-4 rounded-full bg-gray-100 text-gray-400 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                  <Activity className="w-8 h-8" />
                </div>
                <p className="text-gray-600 font-medium">No activities found</p>
                <p className="text-sm text-gray-500 mt-1">
                  Try adjusting your filters
                </p>
              </motion.div>
            ) : (
              filteredActivities.map((activity, index) => (
                <motion.div
                  key={activity.id}
                  className="p-4 border-b border-gray-200 last:border-b-0 hover:bg-gray-50 transition-colors"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.2, delay: index * 0.02 }}
                  layout
                >
                  <div className="flex items-start gap-4">
                    <div className={`p-3 rounded-xl border-2 ${getActivityColor(activity.type)}`}>
                      {getActivityIcon(activity.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900 font-medium">
                        {activity.description}
                      </p>
                      <div className="flex items-center gap-4 mt-1">
                        <p className="text-xs text-gray-500">
                          {formatRelativeTime(activity.timestamp)}
                        </p>
                        {activity.metadata?.amount && (
                          <span className="text-xs font-semibold text-green-600">
                            ${activity.metadata.amount.toFixed(2)}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex-shrink-0">
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getActivityColor(activity.type)}`}>
                        {activity.type.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {activityTypes.slice(1).map((type, index) => {
          const count = activities.filter(a => a.type === type.value).length;
          return (
            <motion.div
              key={type.value}
              className="bg-white rounded-xl border-2 border-gray-200 p-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className={`inline-flex p-2 rounded-lg mb-2 ${getActivityColor(type.value)}`}>
                {getActivityIcon(type.value)}
              </div>
              <p className="text-2xl font-bold text-gray-900">{count}</p>
              <p className="text-xs text-gray-600">{type.label}</p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default ActivityFeed;
