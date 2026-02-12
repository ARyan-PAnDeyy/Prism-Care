import { useState, useEffect } from 'react';
import { TrendingUp, AlertTriangle, Users, Activity } from 'lucide-react';
import axios from 'axios';
import Card from '../components/Card';
import LoadingSpinner from '../components/LoadingSpinner';

export default function AdminDashboard() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const response = await axios.get('/api/admin/stats');
            setStats(response.data);
        } catch (error) {
            console.error('Failed to fetch stats');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <LoadingSpinner size="lg" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>

                {/* KPI Cards */}
                <div className="grid md:grid-cols-4 gap-6 mb-8">
                    <Card>
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm text-slate-600 mb-1">Total Validations</p>
                                <p className="text-3xl font-bold">{stats?.total_validations || 0}</p>
                            </div>
                            <Activity className="h-8 w-8 text-primary" />
                        </div>
                    </Card>

                    <Card>
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm text-slate-600 mb-1">Risk Detections</p>
                                <p className="text-3xl font-bold text-danger">{stats?.risky_detections || 0}</p>
                                <p className="text-xs text-slate-500">{stats?.risk_percentage}%</p>
                            </div>
                            <AlertTriangle className="h-8 w-8 text-danger" />
                        </div>
                    </Card>

                    <Card>
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm text-slate-600 mb-1">Doctor Overrides</p>
                                <p className="text-3xl font-bold text-warning">{stats?.total_overrides || 0}</p>
                                <p className="text-xs text-slate-500">{stats?.override_rate}% of risks</p>
                            </div>
                            <Users className="h-8 w-8 text-warning" />
                        </div>
                    </Card>

                    <Card>
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm text-slate-600 mb-1">System Uptime</p>
                                <p className="text-3xl font-bold text-accent">{stats?.system_uptime}</p>
                            </div>
                            <TrendingUp className="h-8 w-8 text-accent" />
                        </div>
                    </Card>
                </div>

                {/* Override Log Table */}
                <Card>
                    <h2 className="text-xl font-bold mb-4">Recent Overrides</h2>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-slate-50">
                                <tr>
                                    <th className="px-4 py-3 text-left text-sm font-semibold">Timestamp</th>
                                    <th className="px-4 py-3 text-left text-sm font-semibold">Doctor</th>
                                    <th className="px-4 py-3 text-left text-sm font-semibold">Patient ID</th>
                                    <th className="px-4 py-3 text-left text-sm font-semibold">Drug</th>
                                    <th className="px-4 py-3 text-left text-sm font-semibold">Risk Level</th>
                                    <th className="px-4 py-3 text-left text-sm font-semibold">Reason</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y">
                                {stats?.recent_overrides?.length > 0 ? (
                                    stats.recent_overrides.map((override) => (
                                        <tr key={override.id} className="hover:bg-slate-50">
                                            <td className="px-4 py-3 text-sm">
                                                {new Date(override.timestamp).toLocaleString()}
                                            </td>
                                            <td className="px-4 py-3 text-sm">{override.doctor_name}</td>
                                            <td className="px-4 py-3 text-sm">{override.patient_id}</td>
                                            <td className="px-4 py-3 text-sm font-medium">{override.drug}</td>
                                            <td className="px-4 py-3 text-sm">
                                                <span className={`px-2 py-1 rounded-full text-xs ${override.risk_level === 'High' ? 'bg-danger/10 text-danger' : 'bg-warning/10 text-warning'
                                                    }`}>
                                                    {override.risk_level}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 text-sm text-slate-600">{override.reason}</td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan="6" className="px-4 py-8 text-center text-slate-500">
                                            No overrides recorded yet
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </Card>
            </div>
        </div>
    );
}
