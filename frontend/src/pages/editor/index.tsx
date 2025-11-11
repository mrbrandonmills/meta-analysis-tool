import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/router';
import Layout from '@/components/layout/Layout';
import ReviewApprovalCard from '@/components/payment/ReviewApprovalCard';
import PaperQueueCard from '@/components/payment/PaperQueueCard';
import { useReviewApproval } from '@/hooks/useReviewApproval';
import { canAccessEditor } from '@/lib/rbac';
import { useAppStore } from '@/stores/useAppStore';
import {
  FileText,
  Upload,
  CheckCircle2,
  Clock,
  Users,
  Sparkles
} from 'lucide-react';
import { PaperQueueItem } from '@/lib/payment-types';

const EditorDashboardPage: React.FC = () => {
  const router = useRouter();
  const { user } = useAppStore();
  const { pendingReviews, loading, error, fetchPendingReviews, approveReview, rejectReview } = useReviewApproval();
  const [selectedTab, setSelectedTab] = useState<'pending' | 'papers'>('pending');

  // Mock paper queue data (replace with actual API call)
  const [papers] = useState<PaperQueueItem[]>([
    {
      id: '1',
      title: 'The Role of Dopamine in Learning and Memory Consolidation',
      uploadDate: '2025-11-05T10:30:00Z',
      uploadedBy: 'Dr. Sarah Johnson',
      status: 'under_review',
      assignedReviewers: [
        { id: '1', name: 'Dr. Michael Chen', status: 'completed' },
        { id: '2', name: 'Dr. Emily Rodriguez', status: 'accepted' },
        { id: '3', name: 'Dr. James Wilson', status: 'invited' }
      ],
      reviewsCompleted: 1,
      reviewsNeeded: 3
    }
  ]);

  // Check access
  useEffect(() => {
    if (!canAccessEditor(user)) {
      router.push('/dashboard-new');
    }
  }, [user, router]);

  // Fetch data on mount
  useEffect(() => {
    if (canAccessEditor(user)) {
      fetchPendingReviews();
    }
  }, [user]);

  if (!canAccessEditor(user)) {
    return null;
  }

  const handleApprove = async (reviewId: string, notes: string, qualityScore: number) => {
    try {
      await approveReview(reviewId, {
        approved: true,
        qualityScore,
        approvalNotes: notes,
        eligibleForPayout: true
      });
      alert('Review approved successfully!');
    } catch (err) {
      alert('Failed to approve review');
    }
  };

  const handleReject = async (reviewId: string, reason: string) => {
    try {
      await rejectReview(reviewId, reason);
      alert('Review rejected');
    } catch (err) {
      alert('Failed to reject review');
    }
  };

  if (loading && pendingReviews.length === 0) {
    return (
      <Layout title="Editor Dashboard">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Editor Dashboard">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Hero Section */}
        <motion.div
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800 p-8 md:p-12 text-white"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        >
          <motion.div
            className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3]
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
          />

          <div className="relative z-10">
            <div className="flex items-start justify-between flex-wrap gap-6">
              <div className="flex-1 min-w-0">
                <motion.div
                  className="inline-flex items-center gap-3 mb-4"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                >
                  <div className="p-3 rounded-2xl bg-white/20 backdrop-blur-sm">
                    <FileText className="w-8 h-8" />
                  </div>
                  <div>
                    <h1 className="text-4xl md:text-5xl font-bold">
                      Editor Dashboard
                    </h1>
                    <div className="flex items-center gap-2 mt-1">
                      <Sparkles className="w-4 h-4 text-purple-200" />
                      <span className="text-sm text-purple-100 font-medium">
                        Review Management & Quality Control
                      </span>
                    </div>
                  </div>
                </motion.div>

                <motion.p
                  className="text-lg text-purple-100 max-w-2xl leading-relaxed"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  Approve peer reviews, manage paper queue, and assign reviewers to maintain quality standards
                </motion.p>
              </div>

              <motion.button
                className="group px-6 py-3 bg-white text-purple-600 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.5 }}
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/editor/upload')}
              >
                <span className="flex items-center gap-2">
                  <Upload className="w-5 h-5" />
                  Upload Paper
                </span>
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <motion.div
            className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-xl bg-yellow-100 text-yellow-600">
                <Clock className="w-5 h-5" />
              </div>
              <span className="text-sm text-gray-600">Pending Reviews</span>
            </div>
            <div className="text-3xl font-bold text-gray-900">
              {pendingReviews.length}
            </div>
          </motion.div>

          <motion.div
            className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-xl bg-blue-100 text-blue-600">
                <FileText className="w-5 h-5" />
              </div>
              <span className="text-sm text-gray-600">Active Papers</span>
            </div>
            <div className="text-3xl font-bold text-gray-900">
              {papers.length}
            </div>
          </motion.div>

          <motion.div
            className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-xl bg-green-100 text-green-600">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <span className="text-sm text-gray-600">Approved Today</span>
            </div>
            <div className="text-3xl font-bold text-green-600">
              5
            </div>
          </motion.div>

          <motion.div
            className="p-6 rounded-2xl bg-white border-2 border-gray-200 shadow-soft"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-xl bg-purple-100 text-purple-600">
                <Users className="w-5 h-5" />
              </div>
              <span className="text-sm text-gray-600">Active Reviewers</span>
            </div>
            <div className="text-3xl font-bold text-purple-600">
              25
            </div>
          </motion.div>
        </div>

        {/* Tabs */}
        <div>
          <div className="flex gap-2 mb-6 border-b border-gray-200">
            {['pending', 'papers'].map((tab) => (
              <button
                key={tab}
                className={`px-6 py-3 font-semibold transition-colors border-b-2 ${
                  selectedTab === tab
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
                onClick={() => setSelectedTab(tab as any)}
              >
                {tab === 'pending' ? 'Pending Approvals' : 'Paper Queue'}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {selectedTab === 'pending' && (
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                Reviews Awaiting Approval ({pendingReviews.length})
              </h3>
              {pendingReviews.length === 0 ? (
                <div className="p-12 rounded-2xl bg-white border-2 border-gray-200 text-center">
                  <CheckCircle2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    All caught up!
                  </h3>
                  <p className="text-gray-600">
                    No reviews awaiting approval at the moment.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {pendingReviews.map((review, index) => (
                    <ReviewApprovalCard
                      key={review.reviewId}
                      review={review}
                      onApprove={(notes, qualityScore) => handleApprove(review.reviewId, notes, qualityScore)}
                      onReject={(reason) => handleReject(review.reviewId, reason)}
                      onViewFull={() => router.push(`/editor/review/${review.reviewId}`)}
                      estimatedPayout={20}
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          {selectedTab === 'papers' && (
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                Paper Queue ({papers.length})
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {papers.map((paper) => (
                  <PaperQueueCard
                    key={paper.id}
                    paper={paper}
                    onView={() => router.push(`/editor/paper/${paper.id}`)}
                    onAssignReviewers={() => router.push(`/editor/paper/${paper.id}/assign`)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default EditorDashboardPage;
