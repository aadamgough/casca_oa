from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
from ...services.preprocessor import PreprocessingService
from ...services.textract_service import TextractService
from ...services.llama_classifier import LlamaClassifier
from ...services.scorer import ScoringService
import os

router = APIRouter()
textract_service = TextractService()
preprocessor = PreprocessingService()
llama_classifier = LlamaClassifier()
scorer = ScoringService()
UPLOAD_DIR = "app/uploads"  # Create this directory in your backend

@router.post("/upload")  #@router.post("/upload", response_model=List[Transaction])
async def upload_statement(file: UploadFile = File(...)):
    """
    Upload a bank statement file and save it temporarily
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported at this time"
        )
    
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Save the file with a unique name
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            contents = await file.read()
            buffer.write(contents)
        
        return {
            "message": "PDF uploaded successfully",
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while uploading the file: {str(e)}"
        )

@router.post("/analyze/{filename}")
async def analyze_statement(filename: str):
    """
    Analyze an uploaded PDF using Textract
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="File not found. Please upload the file first."
        )
    
    try:
        # Start the Textract job
        print(f"Starting Textract job for file: {file_path}")
        job_id, s3_file_name = await textract_service.start_document_analysis(file_path)
        
        # Get the results
        textract_results = await textract_service.get_document_analysis(job_id)

        # Process the results
        transactions = preprocessor.process_textract_blocks(textract_results)
        
        # Get Llama analysis
        initial_analysis = await llama_classifier.analyze_transactions(transactions)

        # Get scoring and generate final prompt
        scoring_result = scorer.calculate_score(initial_analysis)
        
        # Get the final output to the user
        final_analysis = await llama_classifier.get_final_analysis(scoring_result)

        # Clean up the files
        os.remove(file_path)  # Remove local file
        
        return {
            "textract_results": textract_results,
            "message": "Analysis completed for preprocessing",
            "results": transactions,
            "final_output": final_analysis,
        }
        
    except Exception as e:
        # Log the full error for debugging
        print(f"Error during analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )