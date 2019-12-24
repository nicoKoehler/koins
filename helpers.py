import requests

def allowedExtensions(p_fileName):
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

    if "." not in p_fileName:
        return False

    if p_fileName.split(".",1)[1].lower() in ALLOWED_EXTENSIONS:
        return True
    else: 
        return False

def getFileExt(p_fileName):
    return p_fileName.split(".",1)[1].lower()

def OCRpost(p_file, p_fileName, p_key, p_lang, p_fileType):
    """
    usage: OCRpost(p_file, p_fileName, p_key, p_lang, p_fileType)
    """

    payload = {
        "apikey": p_key,
        "language": p_lang,
        "filetype": p_fileType,
        "scale": True,
        "isTable": True,
        "OCREngine": 2,
        }

    #with open(p_filePath, "rb") as f:
    ocr = requests.post("https://api.ocr.space/parse/image", files={p_fileName: p_file}, data=payload)           
    print(ocr.json())
    return ocr.json()
