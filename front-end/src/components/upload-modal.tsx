"use client"

import { Button } from "@/components/ui/button";
import { FileUpload } from "@/components/file_upload";

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onFileSelect: (file: File | null) => void;
  onAnalyze: () => void;
  isUploaded: boolean;
  isAnalyzing: boolean;
  uploadedFilename?: string;
}

export function UploadModal({
  isOpen,
  onClose,
  onFileSelect,
  onAnalyze,
  isUploaded,
  isAnalyzing,
  uploadedFilename
}: UploadModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-background p-8 rounded-lg shadow-lg max-w-xl w-full mx-4">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold">Upload Bank Statement</h3>
          <button 
            onClick={() => {
              if (!isAnalyzing) onClose();
            }}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {!isUploaded ? (
          <FileUpload onFileSelect={onFileSelect} />
        ) : (
          <div className="space-y-4">
            <div className="p-4 bg-muted rounded-lg flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="font-medium truncate max-w-[200px]">
                  {uploadedFilename}
                </span>
              </div>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => onFileSelect(null)}
                disabled={isAnalyzing}
              >
                Change File
              </Button>
            </div>

            <div className="flex flex-col items-center gap-4">
              <p className="text-green-600 font-medium">
                File uploaded successfully!
              </p>
              <Button 
                onClick={onAnalyze}
                className="w-full"
                disabled={isAnalyzing}
              >
                Analyze Statement
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}