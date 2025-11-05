import React, { useState } from 'react';
import Layout from '@/components/layout/Layout';
import Button from '@/components/shared/Button';
import { Card, CardHeader, CardContent } from '@/components/shared/Card';
import Badge from '@/components/shared/Badge';
import AgentStatusCard from '@/components/shared/AgentStatusCard';
import WorkflowVisualizer from '@/components/shared/WorkflowVisualizer';
import ProgressIndicator from '@/components/shared/ProgressIndicator';
import DataTable from '@/components/shared/DataTable';
import { AgentStatus, AgentProgress, Workflow, WorkflowStatus, CredibilityLevel } from '@/lib/types';
import { getCredibilityColor, getCredibilityBadgeColor, getCredibilityIcon } from '@/lib/utils';
import { Plus, Download, Trash2 } from 'lucide-react';

const DesignSystemPage: React.FC = () => {
  const [loading, setLoading] = useState(false);

  // Example data
  const exampleProgress: AgentProgress = {
    agentName: 'Search Agent',
    status: AgentStatus.PROCESSING,
    currentTask: 'Searching PubMed database for relevant studies...',
    progress: 67,
    eta: 120,
    message: 'Found 234 papers so far'
  };

  const exampleWorkflows: Workflow[] = [
    {
      id: '1',
      projectId: 'proj-1',
      agentName: 'Coordinator Agent',
      agentRole: 'Workflow Orchestration',
      inputData: {},
      outputData: {},
      decisions: [],
      status: WorkflowStatus.COMPLETED,
      startedAt: new Date(),
      completedAt: new Date(),
      durationSeconds: 5,
      progress: 100
    },
    {
      id: '2',
      projectId: 'proj-1',
      agentName: 'Search Agent',
      agentRole: 'Literature Search',
      inputData: {},
      decisions: [],
      status: WorkflowStatus.IN_PROGRESS,
      startedAt: new Date(),
      progress: 67
    },
    {
      id: '3',
      projectId: 'proj-1',
      agentName: 'Screening Agent',
      agentRole: 'Study Screening',
      inputData: {},
      decisions: [],
      status: WorkflowStatus.QUEUED,
      startedAt: new Date()
    }
  ];

  const tableData = [
    { id: 1, title: 'Study on Mindfulness', year: 2023, status: 'included' },
    { id: 2, title: 'Anxiety Research Paper', year: 2022, status: 'excluded' },
    { id: 3, title: 'Meta-Analysis Review', year: 2024, status: 'included' }
  ];

  const tableColumns = [
    { key: 'title', title: 'Title', sortable: true },
    { key: 'year', title: 'Year', sortable: true, width: '100px' },
    {
      key: 'status',
      title: 'Status',
      render: (value: string) => (
        <Badge variant={value === 'included' ? 'success' : 'danger'}>
          {value}
        </Badge>
      )
    }
  ];

  return (
    <Layout breadcrumbs={[{ label: 'Design System' }]}>
      <div className="space-y-12">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Design System</h1>
          <p className="text-lg text-gray-600">
            Component library for the Academic Research Platform
          </p>
        </div>

        {/* Color System */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Color System</h2>

          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Primary Colors</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {['blue', 'gray', 'green', 'red', 'yellow', 'purple', 'orange', 'indigo'].map((color) => (
                  <div key={color} className="space-y-2">
                    <div className={`h-20 rounded-lg bg-${color}-500`} />
                    <p className="text-sm font-medium text-gray-900 capitalize">{color}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Credibility Levels</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {[CredibilityLevel.HIGH, CredibilityLevel.MEDIUM, CredibilityLevel.LOW, CredibilityLevel.VERY_LOW].map((level) => (
                  <div key={level} className={`p-4 rounded-lg border-2 ${getCredibilityColor(level)}`}>
                    <div className="text-2xl mb-2">{getCredibilityIcon(level)}</div>
                    <p className="font-semibold">{level}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Typography */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Typography</h2>
          <Card variant="bordered">
            <CardContent>
              <div className="space-y-4">
                <div>
                  <p className="text-4xl font-bold text-gray-900">Heading 1 - 36px Bold</p>
                  <p className="text-sm text-gray-500 mt-1">text-4xl font-bold</p>
                </div>
                <div>
                  <p className="text-3xl font-bold text-gray-900">Heading 2 - 30px Bold</p>
                  <p className="text-sm text-gray-500 mt-1">text-3xl font-bold</p>
                </div>
                <div>
                  <p className="text-2xl font-semibold text-gray-900">Heading 3 - 24px Semibold</p>
                  <p className="text-sm text-gray-500 mt-1">text-2xl font-semibold</p>
                </div>
                <div>
                  <p className="text-xl font-semibold text-gray-900">Heading 4 - 20px Semibold</p>
                  <p className="text-sm text-gray-500 mt-1">text-xl font-semibold</p>
                </div>
                <div>
                  <p className="text-base text-gray-700">Body Text - 16px Normal</p>
                  <p className="text-sm text-gray-500 mt-1">text-base</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Small Text - 14px</p>
                  <p className="text-xs text-gray-500 mt-1">text-sm</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Caption - 12px</p>
                  <p className="text-xs text-gray-400 mt-1">text-xs</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Buttons */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Buttons</h2>
          <Card variant="bordered">
            <CardContent>
              <div className="space-y-6">
                {/* Variants */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Variants</h3>
                  <div className="flex flex-wrap gap-3">
                    <Button variant="primary">Primary</Button>
                    <Button variant="secondary">Secondary</Button>
                    <Button variant="outline">Outline</Button>
                    <Button variant="ghost">Ghost</Button>
                    <Button variant="danger">Danger</Button>
                  </div>
                </div>

                {/* Sizes */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Sizes</h3>
                  <div className="flex flex-wrap items-center gap-3">
                    <Button size="sm">Small</Button>
                    <Button size="md">Medium</Button>
                    <Button size="lg">Large</Button>
                  </div>
                </div>

                {/* States */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">States</h3>
                  <div className="flex flex-wrap gap-3">
                    <Button>Normal</Button>
                    <Button loading>Loading</Button>
                    <Button disabled>Disabled</Button>
                    <Button icon={<Plus className="w-4 h-4" />}>With Icon</Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Badges */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Badges</h2>
          <Card variant="bordered">
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Variants</h3>
                  <div className="flex flex-wrap gap-3">
                    <Badge variant="default">Default</Badge>
                    <Badge variant="success">Success</Badge>
                    <Badge variant="warning">Warning</Badge>
                    <Badge variant="danger">Danger</Badge>
                    <Badge variant="info">Info</Badge>
                    <Badge variant="purple">Purple</Badge>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">With Dot</h3>
                  <div className="flex flex-wrap gap-3">
                    <Badge variant="success" dot>Active</Badge>
                    <Badge variant="warning" dot>Pending</Badge>
                    <Badge variant="danger" dot>Error</Badge>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Sizes</h3>
                  <div className="flex flex-wrap items-center gap-3">
                    <Badge size="sm">Small</Badge>
                    <Badge size="md">Medium</Badge>
                    <Badge size="lg">Large</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Agent Status Card */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Agent Status Card</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <AgentStatusCard progress={exampleProgress} variant="expanded" />
            <AgentStatusCard progress={{
              ...exampleProgress,
              status: AgentStatus.COMPLETE,
              progress: 100
            }} variant="expanded" />
          </div>
        </section>

        {/* Workflow Visualizer */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Workflow Visualizer</h2>
          <WorkflowVisualizer workflows={exampleWorkflows} currentStep={1} />
        </section>

        {/* Progress Indicators */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Progress Indicators</h2>
          <Card variant="bordered">
            <CardContent>
              <div className="space-y-8">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Progress Bars</h3>
                  <div className="space-y-4">
                    <ProgressIndicator progress={25} label="Starting..." variant="bar" />
                    <ProgressIndicator progress={50} label="Half way" variant="bar" color="green" />
                    <ProgressIndicator progress={75} label="Almost done" variant="bar" color="purple" />
                    <ProgressIndicator progress={100} label="Complete" variant="bar" color="green" />
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Circular Progress</h3>
                  <div className="flex justify-around">
                    <ProgressIndicator progress={33} label="Processing" variant="circular" size="sm" />
                    <ProgressIndicator progress={66} label="Analyzing" variant="circular" size="md" />
                    <ProgressIndicator progress={100} label="Done" variant="circular" size="lg" />
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Loading Dots</h3>
                  <ProgressIndicator progress={0} label="Loading" variant="dots" />
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Data Table */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Data Table</h2>
          <DataTable
            data={tableData}
            columns={tableColumns}
            searchable
            searchPlaceholder="Search studies..."
          />
        </section>

        {/* Cards */}
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Cards</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card variant="default">
              <CardHeader title="Default Card" subtitle="No border, no shadow" />
              <CardContent>
                <p className="text-gray-600">Content goes here...</p>
              </CardContent>
            </Card>

            <Card variant="bordered">
              <CardHeader title="Bordered Card" subtitle="With border" />
              <CardContent>
                <p className="text-gray-600">Content goes here...</p>
              </CardContent>
            </Card>

            <Card variant="elevated" hover>
              <CardHeader title="Elevated Card" subtitle="With shadow" />
              <CardContent>
                <p className="text-gray-600">Hover over me!</p>
              </CardContent>
            </Card>
          </div>
        </section>
      </div>
    </Layout>
  );
};

export default DesignSystemPage;
