"use client"

import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useState } from "react";
import { UploadModal } from "@/components/upload-modal";
import { AnalysisLoading } from "@/components/analysis-loading";
import { AnalysisModal } from "@/components/analysis-modal";
import { AnalysisResults } from "@/types/analysis";

export default function Home() {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [isUploaded, setIsUploaded] = useState(false);
  const [uploadedFilename, setUploadedFilename] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);
  const [showResults, setShowResults] = useState(false);

  const resetState = () => {
    setShowUploadModal(false);
    setIsUploaded(false);
    setUploadedFilename('');
    setIsAnalyzing(false);
    setAnalysisResults(null);
    setShowResults(false);
  };

  const handleFileSelect = async (file: File | null) => {
    setIsUploaded(false);
    setUploadedFilename('');

    if (!file) {
      
      return;
    }

    // Validate file type
    if (!file.type.includes('pdf')) {
      console.error('Please upload a PDF file');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', file);

      console.log(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/analyze/upload`)

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/analyze/upload`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Upload successful:', data);
      setIsUploaded(true);
      setUploadedFilename(data.filename);
      
      // TODO: Add success notification or redirect to results page
      
    } catch (error) {
      console.error('Error uploading file:', error);
      setIsUploaded(false);
    }
  }

  const handleAnalyze = async () => {
    if (!uploadedFilename) return;

    setIsAnalyzing(true);
    setShowResults(false);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/analyze/analyze/${uploadedFilename}`, {
        method: 'POST',
      });
  
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
  
      const data = await response.json();
      console.log('Analysis results:', data);
      
      // Update to handle new response structure
      setAnalysisResults({
        summary: {
          overall_score: data.final_output.summary.overall_score,
          health_status: data.final_output.summary.health_status,
          key_findings: data.final_output.summary.key_findings
        },
        detailed_analysis: {
          components: data.final_output.detailed_analysis.components,
          narrative: data.final_output.detailed_analysis.narrative
        },
        recommendations: {
          immediate_actions: data.final_output.recommendations.immediate_actions,
          flags: data.final_output.recommendations.flags
        },
        metrics: {
          income_sources: data.final_output.metrics.income_sources,
          cash_flow: data.final_output.metrics.cash_flow,
          expense_breakdown: data.final_output.metrics.expense_breakdown,
          debt_and_savings: data.final_output.metrics.debt_and_savings
        }
      });
      
      setShowResults(true);
      setIsAnalyzing(false);
      
    } catch (error) {
      console.error('Error analyzing file:', error);
      setIsAnalyzing(false);
    }
  }

  return (
    <div className="min-h-screen p-8 flex flex-col">
      {/* Background Pattern */}
    <svg 
      aria-hidden="true" 
      className="absolute inset-x-0 -top-14 -z-10 h-[1000px] w-full fill-neutral-50 stroke-neutral-950/5 [mask-image:linear-gradient(to_bottom_left,white_40%,transparent_50%)]"
    >
      <rect width="100%" height="100%" fill="url(#pattern)" strokeWidth="0"></rect>
      <svg x="50%" y="-96" strokeWidth="0" className="overflow-visible">
        <path transform="translate(64 160)" d="M45.119 4.5a11.5 11.5 0 0 0-11.277 9.245l-25.6 128C6.82 148.861 12.262 155.5 19.52 155.5h63.366a11.5 11.5 0 0 0 11.277-9.245l25.6-128c1.423-7.116-4.02-13.755-11.277-13.755H45.119Z"></path>
        <path transform="translate(128 320)" d="M45.119 4.5a11.5 11.5 0 0 0-11.277 9.245l-25.6 128C6.82 148.861 12.262 155.5 19.52 155.5h63.366a11.5 11.5 0 0 0 11.277-9.245l25.6-128c1.423-7.116-4.02-13.755-11.277-13.755H45.119Z"></path>
        <path transform="translate(288 480)" d="M45.119 4.5a11.5 11.5 0 0 0-11.277 9.245l-25.6 128C6.82 148.861 12.262 155.5 19.52 155.5h63.366a11.5 11.5 0 0 0 11.277-9.245l25.6-128c1.423-7.116-4.02-13.755-11.277-13.755H45.119Z"></path>
        <path transform="translate(512 320)" d="M45.119 4.5a11.5 11.5 0 0 0-11.277 9.245l-25.6 128C6.82 148.861 12.262 155.5 19.52 155.5h63.366a11.5 11.5 0 0 0 11.277-9.245l25.6-128c1.423-7.116-4.02-13.755-11.277-13.755H45.119Z"></path>
        <path transform="translate(544 640)" d="M45.119 4.5a11.5 11.5 0 0 0-11.277 9.245l-25.6 128C6.82 148.861 12.262 155.5 19.52 155.5h63.366a11.5 11.5 0 0 0 11.277-9.245l25.6-128c1.423-7.116-4.02-13.755-11.277-13.755H45.119Z"></path>
        <path transform="translate(320 800)" d="M45.119 4.5a11.5 11.5 0 0 0-11.277 9.245l-25.6 128C6.82 148.861 12.262 155.5 19.52 155.5h63.366a11.5 11.5 0 0 0 11.277-9.245l25.6-128c1.423-7.116-4.02-13.755-11.277-13.755H45.119Z"></path>
      </svg>
      <defs>
        <pattern id="pattern" width="96" height="480" x="50%" patternUnits="userSpaceOnUse" patternTransform="translate(0 -96)" fill="none">
          <path d="M128 0 98.572 147.138A16 16 0 0 1 82.883 160H13.117a16 16 0 0 0-15.69 12.862l-26.855 134.276A16 16 0 0 1-45.117 320H-116M64-160 34.572-12.862A16 16 0 0 1 18.883 0h-69.766a16 16 0 0 0-15.69 12.862l-26.855 134.276A16 16 0 0 1-109.117 160H-180M192 160l-29.428 147.138A15.999 15.999 0 0 1 146.883 320H77.117a16 16 0 0 0-15.69 12.862L34.573 467.138A16 16 0 0 1 18.883 480H-52M-136 480h58.883a16 16 0 0 0 15.69-12.862l26.855-134.276A16 16 0 0 1-18.883 320h69.766a16 16 0 0 0 15.69-12.862l26.855-134.276A16 16 0 0 1 109.117 160H192M-72 640h58.883a16 16 0 0 0 15.69-12.862l26.855-134.276A16 16 0 0 1 45.117 480h69.766a15.999 15.999 0 0 0 15.689-12.862l26.856-134.276A15.999 15.999 0 0 1 173.117 320H256M-200 320h58.883a15.999 15.999 0 0 0 15.689-12.862l26.856-134.276A16 16 0 0 1-82.883 160h69.766a16 16 0 0 0 15.69-12.862L29.427 12.862A16 16 0 0 1 45.117 0H128"></path>
        </pattern>
      </defs>
    </svg>

      {/* Header */}
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Steezar</h1>
        <Link href="https://www.cascading.ai/contact" target="_blank">
          <Button variant="ghost" size="sm"> 
            Contact Us
          </Button>
        </Link>
      </header>

      <div className="h-px bg-border my-4" />

      {/* Main content */}
      <main className="flex-1 flex flex-col items-center justify-center max-w-4xl mx-auto text-center gap-8">
        <h2 className="text-5xl sm:text-6xl font-bold tracking-tight">
          Bank loans made simple. 
        </h2>
        
        <p className="text-lg text-muted-foreground max-w-2xl">
          Upload your bank statements and let our AI-powered system analyze creditworthiness 
          in seconds. Make smarter lending decisions with confidence.
        </p>

        <Button 
          onClick={() => setShowUploadModal(true)}
          size="lg"
          className="text-lg px-8 py-6"
        >
          Upload Bank Statement
        </Button>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 mt-16">
          <div className="flex flex-col items-center gap-4">
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 8.688c0-.864.933-1.405 1.683-.977l7.108 4.062a1.125 1.125 0 0 1 0 1.953l-7.108 4.062A1.125 1.125 0 0 1 3 16.81V8.688ZM12.75 8.688c0-.864.933-1.405 1.683-.977l7.108 4.062a1.125 1.125 0 0 1 0 1.953l-7.108 4.062a1.125 1.125 0 0 1-1.683-.977V8.688Z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold">Easy to Use</h3>
            <p className="text-muted-foreground">
              Upload your statements and get instant results. No complex setup required.
            </p>
          </div>

          <div className="flex flex-col items-center gap-4">
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold">Powered by AI</h3>
            <p className="text-muted-foreground">
              Advanced algorithms analyze statements to provide accurate creditworthiness assessments.
            </p>
          </div>

          <div className="flex flex-col items-center gap-4">
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold">Focus on What Matters</h3>
            <p className="text-muted-foreground">
              Save time on analysis and focus on making strategic lending decisions.
            </p>
          </div>
        </div> {/*TODO: Add footer with casa information*/}
      </main>
      <UploadModal 
        isOpen={showUploadModal}
        onClose={resetState}
        onFileSelect={handleFileSelect}
        onAnalyze={handleAnalyze}
        isUploaded={isUploaded}
        isAnalyzing={isAnalyzing}
        uploadedFilename={uploadedFilename}
      />
      <AnalysisLoading isLoading={isAnalyzing} />
      {analysisResults && (
        <AnalysisModal 
          isOpen={showResults} 
          onClose={resetState} 
          results={analysisResults}
        />
      )}
    </div>
  );
}