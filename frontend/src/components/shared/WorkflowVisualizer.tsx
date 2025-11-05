import React from 'react';
import { Workflow, AgentStatus } from '@/lib/types';
import { CheckCircle2, Circle, Loader2, XCircle, Clock } from 'lucide-react';

interface WorkflowVisualizerProps {
  workflows: Workflow[];
  currentStep?: number;
}

export const WorkflowVisualizer: React.FC<WorkflowVisualizerProps> = ({
  workflows,
  currentStep = 0
}) => {
  const getStepIcon = (index: number, workflow: Workflow) => {
    if (workflow.status === 'completed') {
      return <CheckCircle2 className="w-6 h-6 text-green-500" />;
    }
    if (workflow.status === 'failed') {
      return <XCircle className="w-6 h-6 text-red-500" />;
    }
    if (workflow.status === 'in_progress') {
      return <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />;
    }
    if (index < currentStep) {
      return <CheckCircle2 className="w-6 h-6 text-green-500" />;
    }
    if (index === currentStep) {
      return <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />;
    }
    return <Circle className="w-6 h-6 text-gray-300" />;
  };

  const getStepStatus = (index: number, workflow: Workflow) => {
    if (workflow.status === 'completed') return 'Complete';
    if (workflow.status === 'failed') return 'Failed';
    if (workflow.status === 'in_progress') return 'In Progress';
    if (index < currentStep) return 'Complete';
    if (index === currentStep) return 'In Progress';
    return 'Pending';
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Workflow Pipeline</h3>

      <div className="space-y-4">
        {workflows.map((workflow, index) => (
          <div key={workflow.id} className="relative">
            {/* Connector Line */}
            {index < workflows.length - 1 && (
              <div className="absolute left-3 top-10 bottom-0 w-0.5 bg-gray-200" />
            )}

            {/* Step Card */}
            <div className="flex items-start space-x-4">
              <div className="relative z-10 flex-shrink-0">
                {getStepIcon(index, workflow)}
              </div>

              <div className="flex-1 min-w-0 bg-gray-50 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-medium text-gray-900">{workflow.agentName}</h4>
                      <span className={`
                        text-xs px-2 py-0.5 rounded-full font-medium
                        ${workflow.status === 'completed' ? 'bg-green-100 text-green-700' : ''}
                        ${workflow.status === 'in_progress' ? 'bg-blue-100 text-blue-700' : ''}
                        ${workflow.status === 'failed' ? 'bg-red-100 text-red-700' : ''}
                        ${workflow.status === 'created' || workflow.status === 'queued' ? 'bg-gray-100 text-gray-700' : ''}
                      `}>
                        {getStepStatus(index, workflow)}
                      </span>
                    </div>

                    <p className="text-sm text-gray-600">{workflow.agentRole}</p>

                    {workflow.progress !== undefined && workflow.status === 'in_progress' && (
                      <div className="mt-2">
                        <div className="flex justify-between text-xs text-gray-600 mb-1">
                          <span>Progress</span>
                          <span>{workflow.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-1.5">
                          <div
                            className="bg-blue-600 h-1.5 rounded-full transition-all"
                            style={{ width: `${workflow.progress}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {workflow.errorMessage && (
                      <div className="mt-2 text-sm text-red-600 bg-red-50 rounded px-2 py-1">
                        {workflow.errorMessage}
                      </div>
                    )}
                  </div>

                  {workflow.durationSeconds && (
                    <div className="flex items-center text-sm text-gray-500 ml-4">
                      <Clock className="w-4 h-4 mr-1" />
                      <span>{Math.round(workflow.durationSeconds)}s</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WorkflowVisualizer;
