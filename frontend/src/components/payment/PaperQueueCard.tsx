import React from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  Calendar,
  User,
  CheckCircle2,
  Clock,
  UserCheck,
  UserX,
  Eye,
  Users
} from 'lucide-react';
import { PaperQueueItem } from '@/lib/payment-types';

interface PaperQueueCardProps {
  paper: PaperQueueItem;
  onView?: () => void;
  onAssignReviewers?: () => void;
  showActions?: boolean;
}

export const PaperQueueCard: React.FC<PaperQueueCardProps> = ({
  paper,
  onView,
  onAssignReviewers,
  showActions = true
}) => {
  const statusConfig = {
    pending_assignment: {
      label: 'Pending Assignment',
      color: 'bg-yellow-100 text-yellow-700 border-yellow-200',
      icon: Clock
    },
    under_review: {
      label: 'Under Review',
      color: 'bg-blue-100 text-blue-700 border-blue-200',
      icon: Clock
    },
    reviews_complete: {
      label: 'Reviews Complete',
      color: 'bg-green-100 text-green-700 border-green-200',
      icon: CheckCircle2
    },
    published: {
      label: 'Published',
      color: 'bg-gray-100 text-gray-700 border-gray-200',
      icon: CheckCircle2
    }
  };

  const config = statusConfig[paper.status];
  const StatusIcon = config.icon;

  const reviewerStatusConfig = {
    invited: { icon: Clock, color: 'text-yellow-600' },
    accepted: { icon: UserCheck, color: 'text-blue-600' },
    declined: { icon: UserX, color: 'text-red-600' },
    completed: { icon: CheckCircle2, color: 'text-green-600' }
  };

  const completionPercentage = (paper.reviewsCompleted / paper.reviewsNeeded) * 100;

  return (
    <motion.div
      className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft hover:border-purple-300 transition-all duration-300"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -2, shadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)' }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <div className="p-2.5 rounded-xl bg-purple-100 text-purple-600 flex-shrink-0">
            <FileText className="w-5 h-5" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-2">
              {paper.title}
            </h3>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4" />
                {new Date(paper.uploadDate).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric'
                })}
              </div>
              <div className="flex items-center gap-1.5">
                <User className="w-4 h-4" />
                {paper.uploadedBy}
              </div>
            </div>
          </div>
        </div>
        <div className={`px-3 py-1.5 rounded-full text-xs font-medium border whitespace-nowrap ${config.color}`}>
          <div className="flex items-center gap-1.5">
            <StatusIcon className="w-3.5 h-3.5" />
            {config.label}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-gray-600">Review Progress</span>
          <span className="font-semibold text-gray-900">
            {paper.reviewsCompleted} / {paper.reviewsNeeded} completed
          </span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-purple-500 to-purple-600"
            initial={{ width: 0 }}
            animate={{ width: `${completionPercentage}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Assigned Reviewers */}
      {paper.assignedReviewers.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
            <Users className="w-4 h-4" />
            Assigned Reviewers ({paper.assignedReviewers.length})
          </div>
          <div className="space-y-2">
            {paper.assignedReviewers.map((reviewer, index) => {
              const statusCfg = reviewerStatusConfig[reviewer.status];
              return (
                <motion.div
                  key={reviewer.id}
                  className="flex items-center justify-between p-3 rounded-xl bg-gray-50 border border-gray-200"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.05 }}
                >
                  <div className="flex items-center gap-2">
                    <div className={`${statusCfg.color}`}>
                      <statusCfg.icon className="w-4 h-4" />
                    </div>
                    <span className="text-sm font-medium text-gray-900">
                      {reviewer.name}
                    </span>
                  </div>
                  <span className={`text-xs font-medium ${statusCfg.color}`}>
                    {reviewer.status.replace('_', ' ').toUpperCase()}
                  </span>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      {/* Actions */}
      {showActions && (
        <div className="flex gap-3 pt-4 border-t border-gray-200">
          {onView && (
            <motion.button
              className="flex-1 py-2.5 px-4 rounded-xl bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onView}
            >
              <span className="flex items-center justify-center gap-2">
                <Eye className="w-4 h-4" />
                View Paper
              </span>
            </motion.button>
          )}
          {onAssignReviewers && paper.status === 'pending_assignment' && (
            <motion.button
              className="flex-1 py-2.5 px-4 rounded-xl bg-purple-600 text-white font-medium hover:bg-purple-700 transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onAssignReviewers}
            >
              <span className="flex items-center justify-center gap-2">
                <Users className="w-4 h-4" />
                Assign Reviewers
              </span>
            </motion.button>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default PaperQueueCard;
