import React from 'react';
import { useRouter } from 'next/router';
import { motion } from 'framer-motion';
import Layout from '@/components/layout/Layout';
import { Card, CardHeader, CardContent } from '@/components/shared/Card';
import Button from '@/components/shared/Button';
import Badge from '@/components/shared/Badge';
import { useProjects } from '@/hooks/useProjects';
import { useAuth } from '@/hooks/useAuth';
import { ToolType, ProjectStatus } from '@/lib/types';
import { formatRelativeTime } from '@/lib/utils';
import {
  Microscope,
  Users,
  FileText,
  Lightbulb,
  Plus,
  TrendingUp,
  Clock,
  CheckCircle2,
  ArrowRight,
  Loader2
} from 'lucide-react';

const toolCards = [
  {
    type: ToolType.META_ANALYSIS,
    title: 'Meta-Analysis',
    description: 'Conduct systematic reviews with AI-powered literature search and analysis',
    icon: Microscope,
    color: 'blue',
    href: '/tools/meta-analysis',
    features: ['Literature Search', 'Study Screening', 'Statistical Analysis', 'PRISMA Reports']
  },
  {
    type: ToolType.REVIEWER_MATCHER,
    title: 'Reviewer Matcher',
    description: 'Find expert reviewers in minutes with AI-powered expertise matching',
    icon: Users,
    color: 'green',
    href: '/tools/reviewer-matcher',
    features: ['Expertise Analysis', 'Conflict Detection', 'Availability Prediction', 'Match Ranking']
  },
  {
    type: ToolType.PEER_REVIEW,
    title: 'Peer Review Assistant',
    description: 'Generate high-quality peer reviews with constructive AI assistance',
    icon: FileText,
    color: 'purple',
    href: '/tools/peer-review',
    features: ['Quality Assessment', 'Review Generation', 'Editor Synthesis', 'Bias Detection']
  },
  {
    type: ToolType.RESEARCH_DIRECTION,
    title: 'Research Direction',
    description: 'Discover research gaps and generate novel research proposals',
    icon: Lightbulb,
    color: 'yellow',
    href: '/tools/research-direction',
    features: ['Gap Analysis', 'Trend Detection', 'Method Innovation', 'Proposal Generation']
  }
];

const DashboardPage: React.FC = () => {
  const router = useRouter();
  const { user, isLoading: isLoadingAuth } = useAuth();
  const { data: projectsData, isLoading: isLoadingProjects } = useProjects();

  const projects = projectsData?.items || [];

  const stats = {
    total: projects.length,
    active: projects.filter((p: any) => p.status === ProjectStatus.IN_PROGRESS).length,
    completed: projects.filter((p: any) => p.status === ProjectStatus.COMPLETED).length,
    byTool: {
      [ToolType.META_ANALYSIS]: projects.filter((p: any) => p.toolType === ToolType.META_ANALYSIS).length,
      [ToolType.REVIEWER_MATCHER]: projects.filter((p: any) => p.toolType === ToolType.REVIEWER_MATCHER).length,
      [ToolType.PEER_REVIEW]: projects.filter((p: any) => p.toolType === ToolType.PEER_REVIEW).length,
      [ToolType.RESEARCH_DIRECTION]: projects.filter((p: any) => p.toolType === ToolType.RESEARCH_DIRECTION).length
    }
  };

  const recentProjects = [...projects]
    .sort((a: any, b: any) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 5);

  const isLoading = isLoadingAuth || isLoadingProjects;

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  if (isLoading) {
    return (
      <Layout title="Dashboard">
        <div className="flex items-center justify-center h-96">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Dashboard">
      <motion.div
        className="space-y-6"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        {/* Welcome Section */}
        <motion.div
          variants={itemVariants}
          className="bg-gradient-to-r from-primary-600 to-indigo-700 rounded-xl p-8 text-white shadow-medium"
        >
          <h1 className="text-3xl font-bold mb-2">
            Welcome back{user?.name ? `, ${user.name}` : ''}!
          </h1>
          <p className="text-blue-100 text-lg">
            Your AI-powered academic research platform
          </p>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          variants={itemVariants}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <motion.div whileHover={{ scale: 1.02 }} transition={{ type: "spring", stiffness: 300 }}>
            <Card variant="bordered" className="shadow-soft hover:shadow-medium transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Projects</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total}</p>
                </div>
                <div className="p-3 bg-primary-100 rounded-lg">
                  <TrendingUp className="w-8 h-8 text-primary-600" />
                </div>
              </div>
            </Card>
          </motion.div>

          <motion.div whileHover={{ scale: 1.02 }} transition={{ type: "spring", stiffness: 300 }}>
            <Card variant="bordered" className="shadow-soft hover:shadow-medium transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">In Progress</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stats.active}</p>
                </div>
                <div className="p-3 bg-yellow-100 rounded-lg">
                  <Clock className="w-8 h-8 text-yellow-600" />
                </div>
              </div>
            </Card>
          </motion.div>

          <motion.div whileHover={{ scale: 1.02 }} transition={{ type: "spring", stiffness: 300 }}>
            <Card variant="bordered" className="shadow-soft hover:shadow-medium transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Completed</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stats.completed}</p>
                </div>
                <div className="p-3 bg-green-100 rounded-lg">
                  <CheckCircle2 className="w-8 h-8 text-green-600" />
                </div>
              </div>
            </Card>
          </motion.div>
        </motion.div>

        {/* Tools Grid */}
        <motion.div variants={itemVariants}>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Research Tools</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {toolCards.map((tool) => {
              const Icon = tool.icon;
              const projectCount = stats.byTool[tool.type];

              return (
                <motion.div
                  key={tool.type}
                  whileHover={{ scale: 1.02, y: -4 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <Card
                    variant="bordered"
                    className="cursor-pointer shadow-soft hover:shadow-medium transition-shadow h-full"
                    onClick={() => router.push(tool.href)}
                  >
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 bg-${tool.color}-100 rounded-lg`}>
                      <Icon className={`w-8 h-8 text-${tool.color}-600`} />
                    </div>
                    <Badge variant="info">{projectCount} projects</Badge>
                  </div>

                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{tool.title}</h3>
                  <p className="text-gray-600 mb-4">{tool.description}</p>

                  <div className="space-y-2 mb-4">
                    {tool.features.map((feature, idx) => (
                      <div key={idx} className="flex items-center text-sm text-gray-600">
                        <CheckCircle2 className="w-4 h-4 mr-2 text-green-500" />
                        {feature}
                      </div>
                    ))}
                  </div>

                  <Button
                    variant="outline"
                    fullWidth
                    icon={<Plus className="w-4 h-4" />}
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`${tool.href}/new`);
                    }}
                  >
                    Start New Project
                  </Button>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Recent Projects */}
        <motion.div variants={itemVariants}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Recent Projects</h2>
            <Button
              variant="ghost"
              size="sm"
              icon={<ArrowRight className="w-4 h-4" />}
              onClick={() => router.push('/projects')}
            >
              View All
            </Button>
          </div>

          {recentProjects.length === 0 ? (
            <Card variant="bordered">
              <div className="text-center py-12">
                <p className="text-gray-500 mb-4">No projects yet</p>
                <Button
                  variant="primary"
                  icon={<Plus className="w-4 h-4" />}
                  onClick={() => router.push('/tools/meta-analysis/new')}
                >
                  Create Your First Project
                </Button>
              </div>
            </Card>
          ) : (
            <Card variant="bordered" padding="none">
              <div className="divide-y divide-gray-200">
                {recentProjects.map((project) => {
                  const toolCard = toolCards.find(t => t.type === project.toolType);
                  const Icon = toolCard?.icon || Microscope;

                  return (
                    <div
                      key={project.id}
                      className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => router.push(`/projects/${project.id}`)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3 flex-1">
                          <div className={`p-2 bg-${toolCard?.color}-100 rounded-lg`}>
                            <Icon className={`w-5 h-5 text-${toolCard?.color}-600`} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <h4 className="font-medium text-gray-900 truncate">{project.title}</h4>
                            {project.description && (
                              <p className="text-sm text-gray-600 line-clamp-2">{project.description}</p>
                            )}
                            <div className="flex items-center space-x-3 mt-2">
                              <Badge
                                variant={
                                  project.status === ProjectStatus.COMPLETED ? 'success' :
                                  project.status === ProjectStatus.IN_PROGRESS ? 'info' :
                                  project.status === ProjectStatus.FAILED ? 'danger' : 'default'
                                }
                                size="sm"
                              >
                                {project.status}
                              </Badge>
                              <span className="text-xs text-gray-500">
                                Updated {formatRelativeTime(project.updatedAt)}
                              </span>
                            </div>
                          </div>
                        </div>
                        <ArrowRight className="w-5 h-5 text-gray-400 flex-shrink-0 ml-4" />
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          )}
        </motion.div>
      </motion.div>
    </Layout>
  );
};

export default DashboardPage;
