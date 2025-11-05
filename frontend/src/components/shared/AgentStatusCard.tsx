import React from 'react';
import { AgentProgress, AgentStatus } from '@/lib/types';
import { getAgentStatusColor, formatDuration } from '@/lib/utils';
import { Loader2, CheckCircle2, AlertCircle, Brain, Zap } from 'lucide-react';

interface AgentStatusCardProps {
  progress: AgentProgress;
  variant?: 'compact' | 'expanded';
}

export const AgentStatusCard: React.FC<AgentStatusCardProps> = ({
  progress,
  variant = 'expanded'
}) => {
  const getStatusIcon = (status: AgentStatus) => {
    switch (status) {
      case AgentStatus.THINKING:
        return <Brain className="w-5 h-5 animate-pulse" />;
      case AgentStatus.PROCESSING:
        return <Loader2 className="w-5 h-5 animate-spin" />;
      case AgentStatus.COMPLETE:
        return <CheckCircle2 className="w-5 h-5" />;
      case AgentStatus.ERROR:
        return <AlertCircle className="w-5 h-5" />;
      default:
        return <Zap className="w-5 h-5" />;
    }
  };

  const getStatusText = (status: AgentStatus) => {
    switch (status) {
      case AgentStatus.THINKING:
        return 'Thinking...';
      case AgentStatus.PROCESSING:
        return 'Processing...';
      case AgentStatus.COMPLETE:
        return 'Complete';
      case AgentStatus.ERROR:
        return 'Error';
      default:
        return 'Idle';
    }
  };

  if (variant === 'compact') {
    return (
      <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${getAgentStatusColor(progress.status)}`}>
        {getStatusIcon(progress.status)}
        <span className="text-sm font-medium">{progress.agentName}</span>
        {progress.progress > 0 && (
          <span className="text-xs">({progress.progress}%)</span>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${getAgentStatusColor(progress.status)}`}>
            {getStatusIcon(progress.status)}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{progress.agentName}</h3>
            <p className="text-sm text-gray-600">{getStatusText(progress.status)}</p>
          </div>
        </div>
        {progress.eta && (
          <div className="text-right">
            <p className="text-xs text-gray-500">ETA</p>
            <p className="text-sm font-medium text-gray-700">{formatDuration(progress.eta)}</p>
          </div>
        )}
      </div>

      {progress.currentTask && (
        <p className="text-sm text-gray-600 mb-3">{progress.currentTask}</p>
      )}

      {progress.message && (
        <p className="text-xs text-gray-500 mb-3 italic">{progress.message}</p>
      )}

      {progress.progress > 0 && (
        <div className="space-y-1">
          <div className="flex justify-between text-xs text-gray-600">
            <span>Progress</span>
            <span className="font-medium">{progress.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress.progress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentStatusCard;
