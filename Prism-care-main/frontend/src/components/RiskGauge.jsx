import { AlertTriangle, CheckCircle, AlertCircle as AlertIcon } from 'lucide-react';

/**
 * Risk Level Gauge Component
 * Visual indicator for AI risk assessment
 */
export default function RiskGauge({ riskLevel = 'Moderate', confidenceScore = null }) {
    const riskConfig = {
        'Safe': {
            color: 'green',
            percentage: 10,
            icon: CheckCircle,
            bgColor: 'bg-green-50',
            barColor: 'bg-green-500',
            textColor: 'text-green-700'
        },
        'Low': {
            color: 'blue',
            percentage: 30,
            icon: AlertIcon,
            bgColor: 'bg-blue-50',
            barColor: 'bg-blue-500',
            textColor: 'text-blue-700'
        },
        'Moderate': {
            color: 'yellow',
            percentage: 50,
            icon: AlertTriangle,
            bgColor: 'bg-yellow-50',
            barColor: 'bg-yellow-500',
            textColor: 'text-yellow-700'
        },
        'High': {
            color: 'orange',
            percentage: 75,
            icon: AlertTriangle,
            bgColor: 'bg-orange-50',
            barColor: 'bg-orange-500',
            textColor: 'text-orange-700'
        },
        'Critical': {
            color: 'red',
            percentage: 95,
            icon: AlertTriangle,
            bgColor: 'bg-red-50',
            barColor: 'bg-red-500',
            textColor: 'text-red-700'
        }
    };

    const config = riskConfig[riskLevel] || riskConfig['Moderate'];
    const Icon = config.icon;

    return (
        <div className={`p-4 rounded-lg ${config.bgColor}`}>
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                    <Icon className={`w-5 h-5 ${config.textColor}`} />
                    <span className={`font-bold ${config.textColor}`}>{riskLevel} Risk</span>
                </div>
                {confidenceScore && (
                    <span className="text-xs font-medium text-slate-600">
                        {Math.round(confidenceScore * 100)}% Confidence
                    </span>
                )}
            </div>

            {/* Progress Bar */}
            <div className="relative w-full h-3 bg-white rounded-full overflow-hidden border border-slate-200">
                <div
                    className={`h-full ${config.barColor} transition-all duration-500 ease-out`}
                    style={{ width: `${config.percentage}%` }}
                >
                    <div className="h-full w-full bg-gradient-to-r from-transparent to-white/30"></div>
                </div>
            </div>

            {/* Risk Level Labels */}
            <div className="flex justify-between mt-1 text-xs text-slate-500">
                <span>Safe</span>
                <span>Low</span>
                <span>Moderate</span>
                <span>High</span>
                <span>Critical</span>
            </div>
        </div>
    );
}
