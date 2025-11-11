import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  User,
  Calendar,
  CheckCircle2,
  X,
  Star,
  MessageSquare,
  Eye,
  ThumbsUp,
  ThumbsDown,
  DollarSign
} from 'lucide-react';
import { PendingReview } from '@/lib/payment-types';

interface ReviewApprovalCardProps {
  review: PendingReview;
  onApprove?: (notes: string, qualityScore: number) => void;
  onReject?: (reason: string) => void;
  onViewFull?: () => void;
  estimatedPayout?: number;
}

export const ReviewApprovalCard: React.FC<ReviewApprovalCardProps> = ({
  review,
  onApprove,
  onReject,
  onViewFull,
  estimatedPayout = 20
}) => {
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [approvalNotes, setApprovalNotes] = useState('');
  const [qualityScore, setQualityScore] = useState(4);
  const [rejectionReason, setRejectionReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleApprove = async () => {
    if (!onApprove) return;
    setIsSubmitting(true);
    try {
      await onApprove(approvalNotes, qualityScore);
      setShowApprovalModal(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (!rejectionReason.trim() || !onReject) return;
    setIsSubmitting(true);
    try {
      await onReject(rejectionReason);
      setShowRejectModal(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const daysSinceSubmission = Math.floor(
    (new Date().getTime() - new Date(review.submittedAt).getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <>
      <motion.div
        className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft hover:border-blue-300 transition-all duration-300"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {/* Header */}
        <div className="flex items-start gap-4 mb-4">
          <div className="p-3 rounded-xl bg-blue-100 text-blue-600">
            <FileText className="w-6 h-6" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-2">
              {review.manuscriptTitle}
            </h3>
            <div className="flex items-center gap-4 text-sm text-gray-600 flex-wrap">
              <div className="flex items-center gap-1.5">
                <User className="w-4 h-4" />
                {review.reviewerName}
              </div>
              <div className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4" />
                {new Date(review.submittedAt).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric'
                })}
              </div>
              {daysSinceSubmission > 0 && (
                <div className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                  daysSinceSubmission <= 2
                    ? 'bg-green-100 text-green-700'
                    : daysSinceSubmission <= 5
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-red-100 text-red-700'
                }`}>
                  {daysSinceSubmission}d ago
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quality Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div className="p-3 rounded-xl bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
            <div className="flex items-center gap-2 mb-1">
              <Star className="w-4 h-4 text-blue-600" />
              <span className="text-xs font-medium text-blue-900">Overall Score</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">
              {review.reviewQualityPreview.overallScore.toFixed(1)}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
            <div className="flex items-center gap-2 mb-1">
              <ThumbsUp className="w-4 h-4 text-green-600" />
              <span className="text-xs font-medium text-green-900">Strengths</span>
            </div>
            <div className="text-2xl font-bold text-green-600">
              {review.reviewQualityPreview.strengthsCount}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
            <div className="flex items-center gap-2 mb-1">
              <ThumbsDown className="w-4 h-4 text-orange-600" />
              <span className="text-xs font-medium text-orange-900">Weaknesses</span>
            </div>
            <div className="text-2xl font-bold text-orange-600">
              {review.reviewQualityPreview.weaknessesCount}
            </div>
          </div>
          <div className="p-3 rounded-xl bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
            <div className="flex items-center gap-2 mb-1">
              <MessageSquare className="w-4 h-4 text-purple-600" />
              <span className="text-xs font-medium text-purple-900">Word Count</span>
            </div>
            <div className="text-2xl font-bold text-purple-600">
              {review.reviewQualityPreview.wordCount}
            </div>
          </div>
        </div>

        {/* Estimated Payout */}
        <div className="p-4 rounded-xl bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium text-green-900">
                Estimated Payout if Approved
              </span>
            </div>
            <div className="text-2xl font-bold text-green-600">
              ${estimatedPayout.toFixed(2)}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          {onViewFull && (
            <motion.button
              className="flex-1 py-2.5 px-4 rounded-xl bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onViewFull}
            >
              <span className="flex items-center justify-center gap-2">
                <Eye className="w-4 h-4" />
                View Full
              </span>
            </motion.button>
          )}
          {onReject && (
            <motion.button
              className="flex-1 py-2.5 px-4 rounded-xl bg-red-100 text-red-700 font-medium hover:bg-red-200 transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowRejectModal(true)}
            >
              <span className="flex items-center justify-center gap-2">
                <X className="w-4 h-4" />
                Reject
              </span>
            </motion.button>
          )}
          {onApprove && (
            <motion.button
              className="flex-1 py-2.5 px-4 rounded-xl bg-green-600 text-white font-medium hover:bg-green-700 transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowApprovalModal(true)}
            >
              <span className="flex items-center justify-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                Approve
              </span>
            </motion.button>
          )}
        </div>
      </motion.div>

      {/* Approval Modal */}
      {showApprovalModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6"
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 rounded-xl bg-green-100 text-green-600">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-1">
                  Approve Review
                </h3>
                <p className="text-sm text-gray-600">
                  This review will be eligible for payout
                </p>
              </div>
            </div>

            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quality Score (1-5)
                </label>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map((score) => (
                    <button
                      key={score}
                      className={`flex-1 py-3 rounded-lg border-2 font-semibold transition-all ${
                        qualityScore === score
                          ? 'border-green-500 bg-green-50 text-green-700'
                          : 'border-gray-300 text-gray-600 hover:border-gray-400'
                      }`}
                      onClick={() => setQualityScore(score)}
                    >
                      {score}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Approval Notes (optional)
                </label>
                <textarea
                  className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all resize-none"
                  rows={3}
                  placeholder="Internal notes about this approval..."
                  value={approvalNotes}
                  onChange={(e) => setApprovalNotes(e.target.value)}
                />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                className="flex-1 py-2.5 px-4 rounded-xl bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition-colors disabled:opacity-50"
                onClick={() => setShowApprovalModal(false)}
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                className="flex-1 py-2.5 px-4 rounded-xl bg-green-600 text-white font-medium hover:bg-green-700 transition-colors disabled:opacity-50"
                onClick={handleApprove}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Approving...' : 'Confirm Approval'}
              </button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6"
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="flex items-start gap-4 mb-6">
              <div className="p-3 rounded-xl bg-red-100 text-red-600">
                <X className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-1">
                  Reject Review
                </h3>
                <p className="text-sm text-gray-600">
                  This review will not be eligible for payout
                </p>
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rejection Reason (required)
              </label>
              <textarea
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-red-500 focus:ring-2 focus:ring-red-200 outline-none transition-all resize-none"
                rows={4}
                placeholder="Please explain why this review doesn't meet quality standards..."
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
              />
            </div>

            <div className="flex gap-3">
              <button
                className="flex-1 py-2.5 px-4 rounded-xl bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition-colors disabled:opacity-50"
                onClick={() => setShowRejectModal(false)}
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                className="flex-1 py-2.5 px-4 rounded-xl bg-red-600 text-white font-medium hover:bg-red-700 transition-colors disabled:opacity-50"
                onClick={handleReject}
                disabled={isSubmitting || !rejectionReason.trim()}
              >
                {isSubmitting ? 'Rejecting...' : 'Confirm Rejection'}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </>
  );
};

export default ReviewApprovalCard;
