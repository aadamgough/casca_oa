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
}

export function UploadModal({
  isOpen,
  onClose,
  onFileSelect,
  onAnalyze,
  isUploaded,
  isAnalyzing
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
        
        <FileUpload onFileSelect={onFileSelect} />
        
        {/* TODO: add visual of what file was uploaded like before */}
        {isUploaded && (
          <div className="mt-6 flex flex-col items-center gap-4">
            <p className="text-green-600 font-medium"> 
              File uploaded successfully!
            </p>
            <Button 
              onClick={() => {
                onAnalyze();
              }}
              className="w-full"
            >
              Analyze Statement
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}