from fastapi import FastAPI
from pydantic import BaseModel
import fitz  # PyMuPDF 用于处理 PDF
import docx  # python-docx 用于处理 docx
import requests
import io
import os
from urllib.parse import urlparse

app = FastAPI()

class FileRequest(BaseModel):
    file: str  

@app.post("/extract")
async def extract_resume(request_data: FileRequest):
    try:
        file_url = request_data.file
        
        # 1. 从链接中提取文件的后缀名 (比如 .pdf, .docx)
        parsed_url = urlparse(file_url)
        # 有些链接带有参数，我们需要拿到最干净的文件路径
        clean_path = parsed_url.path
        file_ext = os.path.splitext(clean_path)[1].lower()
        
        # 2. 下载文件到内存中
        response = requests.get(file_url)
        if response.status_code != 200:
            return {"success": False, "message": "哎呀，文件下载失败了，请稍后再试。"}
        
        # 将下载的二进制数据放进内存流
        file_stream = io.BytesIO(response.content)
        extracted_text = ""

        # 3. 智能分发：根据不同后缀使用不同的解析工具
        if file_ext == '.pdf':
            # 解析 PDF
            doc = fitz.open(stream=file_stream, filetype="pdf")
            for page in doc:
                extracted_text += page.get_text()
            doc.close()
            
        elif file_ext == '.docx':
            # 解析 DOCX
            doc = docx.Document(file_stream)
            for para in doc.paragraphs:
                extracted_text += para.text + "\n"
                
        elif file_ext == '.doc':
            # 优雅地拦截老旧的 DOC 格式
            return {
                "success": False, 
                "message": "抱歉，由于系统升级，暂不支持老旧的 .doc 格式。为了保证您的简历信息提取准确，请将简历『另存为』PDF 或 .docx 格式后重新发给我哦！"
            }
            
        else:
            # 拦截完全不相关的格式（比如图片、压缩包）
            return {
                "success": False, 
                "message": f"不支持解析 {file_ext} 格式的文件，请上传 PDF 或 Word(docx) 格式的简历。"
            }

        # 4. 返回提取的文本
        return {
            "success": True,
            "markdown": extracted_text
        }
        
    except Exception as e:
        return {"success": False, "message": f"解析过程中出现小状况: {str(e)}"}
