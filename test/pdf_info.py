from PyPDF2 import PdfFileReader
import os

PDF_LINK = os.path.join('pdf', 'tng_ewallet_transactions.pdf')
pdf = PdfFileReader(open(PDF_LINK, 'rb'))

pdf.getDocumentInfo()['/Producer']