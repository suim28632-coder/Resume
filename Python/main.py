from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import fitz  # 导入 PyMuPDF 库，专门用于极速解析 PDF
import io

# 建立一个 FastAPI 应用
app = FastAPI(
    title="我的专属PDF简历解析器", 
    description="用于接收PDF文件并返回纯文本的API",
    version="1.0.0"
)

@app.post("/extract_resume")
async def extract_text(file: UploadFile = File(...)):
    # 1. 拦截非 PDF 文件
    if not file.filename.lower().endswith('.pdf'):
        return JSONResponse(status_code=400, content={"error": "请上传 PDF 格式的简历文件。"})
    
    try:
        # 2. 读取文件内容到内存
        content = await file.read()
        pdf_document = fitz.open(stream=content, filetype="pdf")
        
        extracted_text = ""
        
        # 3. 逐页提取文字
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            extracted_text += page.get_text()
            
        pdf_document.close()
        
        # 4. 返回 Coze 容易读取的 JSON 格式
        return {
            "success": True,
            "markdown": extracted_text, # 这里的 markdown 字段可以直接连给大模型
            "message": "解析成功！"
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"解析失败: {str(e)}"})