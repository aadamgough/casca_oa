"use client"

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

interface FileUploadProps {
  onFileSelect: (file: File | null) => void;
}

export function FileUpload({ onFileSelect }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
      setIsDragging(false); // move this here for consistent cleanup
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
    },
    maxFiles: 1,
    multiple: false,
    onDragEnter: () => setIsDragging(true),
    onDragLeave: () => setIsDragging(false),
    onDragOver: () => setIsDragging(true),
  });

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-12
        transition-all duration-200 ease-in-out
        cursor-pointer text-center
        ${isDragActive 
          ? 'border-primary bg-primary/5 scale-102' 
          : 'border-gray-300 hover:border-primary'
        }
      `}
    >
      <input {...getInputProps() as any} />
      <div className="flex flex-col items-center gap-4">
        <div className={`
          p-4 rounded-full bg-primary/10
          transition-transform duration-200
          ${isDragActive ? 'scale-110' : ''}
        `}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={`
              h-8 w-8
              transition-colors duration-200
              ${isDragActive ? 'text-primary' : 'text-gray-400'}
            `}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
        </div>

        <div className="space-y-2">
          <p className="text-lg font-medium">
            {isDragActive 
              ? "Drop your file here" 
              : "Drag & drop your bank statement"
            }
          </p>
          <p className="text-sm text-muted-foreground">
            or click to browse
          </p>
        </div>

        <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>Supports PDF files only</span>
        </div>
      </div>
    </div>
  );
}