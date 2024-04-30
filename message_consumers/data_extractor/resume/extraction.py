import PyPDF2
import io
import boto3
import os


class ResumeExtractor:
    @staticmethod
    def extract_text_from_pdf(path):
        # Use PyPDF2 to extract info from PDF
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("REGION_NAME")
        )
        s3 = session.client('s3')
        bucket, key = path.replace("s3://", "").split("/", 1)
        file = io.BytesIO()
        s3.download_fileobj(bucket, key, file)
        file.seek(0)  # move the cursor to the beginning of the file
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
        return text
