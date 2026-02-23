from fastapi import FastAPI
from pydantic import BaseModel
import fitz  # PyMuPDF
import docx  # python-docx
import requests
import io

app = FastAPI()

class FileRequest(BaseModel):
    file: str  

@app.post("/extract")
async def extract_resume(request_data: FileRequest):
    try:
        # 1. 不管三七二十一，先把文件下载到内存里
        response = requests.get(request_data.file)
        file_bytes = response.content
        file_stream = io.BytesIO(file_bytes)
        
        extracted_text = ""
        is_success = False

        # 2. 霸道解析方案 A：先把它当 PDF 试着打开
        try:
            # 强制按 PDF 打开
            doc = fitz.open(stream=file_stream, filetype="pdf")
            for page in doc:
                extracted_text += page.get_text()
            doc.close()
            is_success = True
        except:
            # 3. 霸道解析方案 B：如果不是 PDF，重置流，尝试按 Word 打开
            try:
                file_stream.seek(0) # 倒带回到文件开头
                doc = docx.Document(file_stream)
                for para in doc.paragraphs:
                    extracted_text += para.text + "\n"
                is_success = True
            except:
                # 实在解不开
                return {"success": False, "message": "文件格式不支持，请上传 PDF 或 Word。"}

        # 4. 只要提取到了文字（或者解析成功），就返回
        return {
            "success": True,
            "markdown": extracted_text if extracted_text else "解析成功，但文档内似乎没有可提取的文字（可能是纯图片扫描件）。"
        }
        
    except Exception as e:
        return {"success": False, "message": f"服务器报错: {str(e)}"}
