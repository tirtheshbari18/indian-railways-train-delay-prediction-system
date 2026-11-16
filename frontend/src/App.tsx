import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar, NavTab } from './components/Sidebar';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Dashboard } from './pages/Dashboard';
import { TrainDelayPrediction } from './pages/TrainDelayPrediction';
import { RouteAnalysis } from './pages/RouteAnalysis';
import { DelayAnalytics } from './pages/DelayAnalytics';
import { DataManagement } from './pages/DataManagement';
import { ModelManagement } from './pages/ModelManagement';
import { PredictionHistory } from './pages/PredictionHistory';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavTab>('dashboard');

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        {/* Left Sidebar */}
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        {/* Main Content Area */}
        <main className="flex-1 p-6 md:p-8 overflow-y-auto">
          <ErrorBoundary key={currentTab}>
            {currentTab === 'dashboard' && <Dashboard onNavigateTab={setCurrentTab} />}
            {currentTab === 'predict' && <TrainDelayPrediction />}
            {currentTab === 'route' && <RouteAnalysis />}
            {currentTab === 'analytics' && <DelayAnalytics />}
            {currentTab === 'datasets' && <DataManagement />}
            {currentTab === 'models' && <ModelManagement />}
            {currentTab === 'history' && <PredictionHistory />}
          </ErrorBoundary>
        </main>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>
            © 2026 Indian Railways AI Operations Support System • CRIS / Ministry of Railways
          </span>
          <span className="text-[11px] text-slate-400">
            Machine Learning Engine: XGBoost & Gradient Boosting Regression
          </span>
        </div>
      </footer>
    </div>
  );
};

export default App;
