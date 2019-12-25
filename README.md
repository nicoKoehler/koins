# cs50: Final Project >  Koins.me

## Summary
_Koins.me_ is a web-app that allows for Upload of pictures of shopping receipts, reads it out via an OCR API, and allows the user to modify the results and ultimately download them. 

### Purpose
While lots of banks alright provide insights into high level spending categories, these categories may not be broad enough, and, for the case of whole-salers, cannot be accurate. Therefore _Koins.me_ provides the possibility to read out and analyze more detailed information about one's own purchasing habits information. 

### Data privacy 
No Information is stored on the server. The file uploads maybe buffered in order to stream the file to the API, but no file is permanently stored.
As purchasin and receipt information are amongst the most volatile, I made an effort not to store any data, require logons, or even have a database backend that could persist any information, so to protect the user. 

### Process
1. Upload receipt in form of .jpg --> Select a language for word processing
2. Send .jpg to public OCR API https://api.ocr.space/ with own API key
3. receive results in form of JSON
4. parse JSON via custom logic to identify totals and potentially relevant line items
5. display results in form of editable table 
6. Provide user with high level ISO standardized goods taxonomy - ignore lines that are not goods, will be excluded in export
7. Allow user to export results as .csv file

### Potential future development
* deeper taxonomy with cascaded drop down lists
* smarter automatic recognition of lines 
* anonymized hub that stores history and automtically analyzes spending for user
* machine learning to automatically assign/suggest categories