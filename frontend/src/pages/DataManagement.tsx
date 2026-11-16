import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Upload, 
  CheckCircle2, 
  AlertCircle, 
  FileSpreadsheet, 
  Clock, 
  RefreshCw,
  Table,
  Filter,
  Download
} from 'lucide-react';
import { api } from '../services/api';
import { DatasetSummary, HistoricalRunningRecord } from '../types';

export const DataManagement: React.FC = () => {
  const [datasets, setDatasets] = useState<DatasetSummary[]>([]);
  const [records, setRecords] = useState<HistoricalRunningRecord[]>([]);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadSuccess, setUploadSuccess] = useState<DatasetSummary | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const dsList = await api.getDatasets();
      setDatasets(Array.isArray(dsList) ? dsList : []);
      if (Array.isArray(dsList) && dsList.length > 0) {
        // Load preview records from first dataset
        await api.getPredictionHistory(undefined, 25);
      }
      // Also fetch some running records for preview
      await api.getActualVsPredicted(25);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const result = await api.uploadDataset(file);
      setUploadSuccess(result);
      loadData();
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || 'Failed to process dataset file.');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div>
        <span className="text-xs uppercase font-bold tracking-widest text-railway-blue">Data Operations & Pipelines</span>
        <h2 className="text-2xl font-black text-slate-900 tracking-tight">Historical Railway Dataset Management</h2>
        <p className="text-sm text-slate-600">
          Ingest, sanitize, validate, and preview train delay records in CSV, Excel (.xlsx/.xls) or JSON formats.
        </p>
      </div>

      {/* Upload Zone & Preprocessing Highlights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Upload Card */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900">Upload Railway Run Dataset</h3>
              <p className="text-xs text-slate-500">Supports CSV, Excel (.xlsx/.xls) and JSON files</p>
            </div>
            <span className="text-xs bg-blue-50 text-blue-700 font-semibold px-2.5 py-1 rounded-md border border-blue-200">
              Automated Cleaning Active
            </span>
          </div>

          {/* Drag & Drop or Click to Select File */}
          <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center bg-slate-50/50 hover:bg-slate-50 transition-colors">
            <Upload className="w-10 h-10 text-slate-400 mx-auto mb-2" />
            <span className="text-sm font-bold text-slate-800 block">Click to upload or drag and drop</span>
            <span className="text-xs text-slate-500 block mt-1">
              Required fields: train_number, station_code, journey_date
            </span>
            <input
              type="file"
              accept=".csv,.xlsx,.xls,.json"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
              id="dataset-upload-input"
            />
            <label
              htmlFor="dataset-upload-input"
              className="inline-block mt-4 px-4 py-2 bg-railway-navy hover:bg-railway-blue text-white font-bold text-xs rounded-lg cursor-pointer transition-colors shadow-sm"
            >
              {uploading ? 'Validating & Ingesting...' : 'Browse Railway Data File'}
            </label>
          </div>

          {/* Success Banner with Cleaning Report */}
          {uploadSuccess && (
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-2">
              <div className="flex items-center space-x-2 text-emerald-800 font-bold text-xs">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Dataset Successfully Ingested: {uploadSuccess.dataset_name}</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs text-slate-700 pt-1 border-t border-emerald-200/60">
                <div>
                  <span className="text-slate-500 block text-[10px]">TOTAL ROWS</span>
                  <span className="font-bold">{uploadSuccess.total_records}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">CLEAN ROWS</span>
                  <span className="font-bold text-emerald-700">{uploadSuccess.valid_records}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">INVALID DROPPED</span>
                  <span className="font-bold text-red-600">{uploadSuccess.invalid_records}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">STATUS</span>
                  <span className="font-bold uppercase text-emerald-700">{uploadSuccess.status}</span>
                </div>
              </div>
            </div>
          )}

          {uploadError && (
            <div className="p-4 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}

        </div>

        {/* Cleaning Pipeline Specs */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-slate-800">
            <RefreshCw className="w-4 h-4 text-railway-blue" />
            <span>Automated Cleaning Rules</span>
          </div>
          
          <div className="space-y-3 text-xs text-slate-600">
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="font-bold text-slate-800 block">Deduplication:</span>
              <span>Identifies and eliminates redundant records with matching train, station, and date.</span>
            </div>

            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="font-bold text-slate-800 block">Outlier Capping:</span>
              <span>Caps unrealistic delay values (&lt; -30m early or &gt; 1440m delay) to prevent skewing gradient boosting splits.</span>
            </div>

            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
              <span className="font-bold text-slate-800 block">Feature Engineering:</span>
              <span>Extracts cyclical day-of-week, hour-of-departure, lag previous delay, and corridor congestion score.</span>
            </div>
          </div>
        </div>

      </div>

      {/* Imported Datasets Table */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">Imported Railway Datasets</h3>
            <p className="text-xs text-slate-500">History of data imports preserved for retraining</p>
          </div>
          <button
            onClick={loadData}
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-lg transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Dataset Name</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4 text-right">Total Rows</th>
                <th className="py-3 px-4 text-right">Valid Rows</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4">Imported At</th>
                <th className="py-3 px-4">Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(Array.isArray(datasets) ? datasets : []).map((ds) => (
                <tr key={ds.id} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-bold text-slate-900 flex items-center gap-2">
                    <FileSpreadsheet className="w-4 h-4 text-railway-blue" />
                    <span>{ds.dataset_name}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="uppercase font-mono font-bold text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                      {ds.file_type}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-medium text-slate-700">
                    {ds.total_records.toLocaleString()}
                  </td>
                  <td className="py-3 px-4 text-right font-bold text-emerald-700">
                    {ds.valid_records.toLocaleString()}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700">
                      {ds.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-500">
                    {new Date(ds.upload_timestamp).toLocaleDateString()} {new Date(ds.upload_timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </td>
                  <td className="py-3 px-4 text-slate-500 max-w-xs truncate">
                    {ds.notes || 'Standard Operational Records'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
