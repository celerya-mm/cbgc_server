import base64
import os
import shutil

import qrcode
from docx import Document  # noqa
from docx.shared import Inches  # noqa
from docxtpl import DocxTemplate

# imposta path doc file's models
path = os.path.dirname(os.path.realpath(__file__))
folders_models = os.path.join(path, "certificates_model")

# imposta path work
folder_work = os.path.join(path, "certificates_work")
if not os.path.exists(folder_work):
	os.makedirs(folder_work)

# imposta path temp file
folder_temp = os.path.join(path, "temp_pdf")
if not os.path.exists(folder_temp):
	os.makedirs(folder_temp)


def generate_qr_code(_str):
	"""Genera un QR-Code da una stringa."""
	try:
		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_H,
			box_size=10,
			border=1,
		)
		qr.add_data(_str.replace("/", "_"))
		qr.make(fit=True)
		img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
		# print("")
		# print(img)
		img.save(os.path.join(folder_work, _str.replace("/", "_") + ".jpg"))
		# print("QR-Code Generated")
		return _str
	except Exception as err:
		print(err)
		return False


def doc_to_pdf(target):
	"""Converte file Word in pdf."""
	try:
		from comtypes import client
		word = client.CreateObject('Word.Application')
	except ImportError:
		from comtypes import client
		word = None

	doc = word.Documents.Open(target)
	outFile = os.path.join(target.replace("docx", "pdf"))
	print("PDF_PATH:", outFile)
	print("")
	try:
		doc.ExportAsFixedFormat(
			OutputFileName=outFile,
			ExportFormat=17,  # 17 = PDF output, 18=XPS output
			OpenAfterExport=False,
			OptimizeFor=0,  # 0=Print (higher res), 1=Screen (lower res)
			CreateBookmarks=1,  # 0=No bookmarks, 1=Heading bookmarks only, 2=bookmarks match word bookmarks
			DocStructureTags=False
		)
		print("CONVERTED")
		doc.Close()
		print("CLOSE")
		doc.Quit()
		print("QUIT")
		os.remove(target)
		print("SUCCESSFULLY CONVERTED")
		return outFile
	except Exception as err:
		os.remove(target)
		print("SUCCESS_CONVERT:", err)
		return outFile


def create_byte_certificate(data, _file, _str):
	"""Legge il modello dal file word e sostituisce le chiavi."""
	# copio il modello e lo salvo nella cartella di lavoro
	_name = data["certificate_nr"].replace("/", "_") + ".docx"
	target = os.path.join(folder_work, _name)
	source = os.path.join(folders_models, _file)
	shutil.copy(source, target)

	# inserisce QR_code
	document = Document(target)
	for para in document.paragraphs:
		if '{{QRCode}}' in para.text:
			# print("PARA_TEXT:", para.text)
			# create a new run (a new line of text)
			run = para.add_run()
			# insert the image
			_jpg = os.path.join(folder_work, _str.replace("/", "_") + ".jpg")
			run.add_picture(_jpg, width=Inches(1.1), height=Inches(1.1))
			os.remove(_jpg)

	# save the modified docx file
	document.save(target)

	# inserisce dati nel certificato
	tpl = DocxTemplate(target)  # leggi il template word
	tpl.render(data)
	# save the modified docx file
	tpl.save(target)

	# convert docx to pdf
	_pdf = doc_to_pdf(target)
	if _pdf:
		# convert pdf to byte
		with open(_pdf, "rb") as f:
			enc_string = str(base64.b64encode(f.read()), 'utf-8')
			# print(enc_string[100], type(enc_string))
			enc_string = base64.b64decode(enc_string)
		# print(enc_string[100], type(enc_string))
		if enc_string:
			os.remove(_pdf)
			return enc_string
		else:
			os.remove(_pdf)
			return False
	else:
		return False


def byte_to_pdf(byte, f_name):
	"""Ricrea il pdf da una stringa in byte."""
	# for file in folder_temp:
	for filename in os.listdir(folder_temp):
		file_path = os.path.join(folder_temp, filename)
		os.remove(file_path)

	path_file = os.path.join(folder_temp, f_name.replace("/", "_") + ".pdf")
	print("PDF_STR_TYPE:", type(byte), "LEN:", len(byte))
	# document = cert.certificate_pdf, 'utf-8')
	with open(path_file, "wb") as f:
		f.write(byte)
	return path_file
