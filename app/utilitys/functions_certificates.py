import base64
import os

import pdfkit
import qrcode
from flask import current_app as app, render_template

from .functions import token_admin_validate
from ..app import PATH_PROJECT as _path

# imposta path file's models docx (Windows)
folders_models_docx = os.path.join(_path, "utilitys", "certificates_models_docx")

# imposta path file's models .odt (Linux)
folders_models_odt = os.path.join(_path, "utilitys", "certificates_models_odt")

# imposta path qrcode
folder_temp_qrcode = os.path.join(_path, "static", "qrcode_temp")
if not os.path.exists(folder_temp_qrcode):
	os.makedirs(folder_temp_qrcode)

# imposta path temp file
folder_temp_pdf = os.path.join(_path, "utilitys", "temp_pdf")
if not os.path.exists(folder_temp_pdf):
	os.makedirs(folder_temp_pdf)


def generate_qr_code(_str, nr_cert):
	"""Genera un QR-Code da una stringa."""
	try:
		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_Q,
			box_size=15,
			border=1,
		)
		qr.add_data(_str)
		qr.make(fit=True)
		img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
		# print("")
		# print(img)
		nr_cert = nr_cert.replace("/", "_") + ".jpg"
		img.save(os.path.join(folder_temp_qrcode, nr_cert))
		# print("QR-Code Generated")
		return nr_cert
	except Exception as err:
		print(err)
		return False


def byte_to_pdf(byte, f_name):
	"""Ricrea il pdf da una stringa in byte."""
	# svuoto la cartella da file vecchio
	for filename in os.listdir(folder_temp_pdf):
		file_path = os.path.join(folder_temp_pdf, filename)
		os.remove(file_path)

	path_file = os.path.join(folder_temp_pdf, f_name.replace("/", "_") + ".pdf")
	print("PDF_STR_TYPE:", type(byte), "LEN:", len(byte))
	with open(path_file, "wb") as f:
		f.write(byte)
	return path_file


def pdf_to_byte(_pdf):
	"""Converte pdf in byte string."""
	try:
		with open(_pdf, "rb") as f:
			b_string = str(base64.b64encode(f.read()), 'utf-8')
			b_string = base64.b64decode(b_string)
		os.remove(_pdf)
		return b_string
	except FileNotFoundError as err:
		print(err)
		return False


@app.route("/cert_cons/<template>/<form>/<qrcode>/", methods=["GET", "POST"])
@token_admin_validate
def html_to_pdf(template, form, _qrcode):
	"""Genera pdf da template html."""
	_img = os.path.join(_path, "static", "qrcode_temp", _qrcode)
	logo = os.path.join(_path, "static", "Logo.png")
	# print("PATH_QRCODE:", _img)

	# PDF options
	options = {
		"orientation": "portrait",
		"page-size": "A4",
		"margin-top": "0cm",
		"margin-right": "0cm",
		"margin-bottom": "0cm",
		"margin-left": "0cm",
		"encoding": "UTF-8",
		"enable-local-file-access": ""
	}

	try:
		# Build PDF from HTML
		_file = os.path.join(folder_temp_pdf, "report.pdf")
		# print("PATH_PDF_FILE:", _file)
		html = render_template(template, form=form, qrcode=_img, logo=logo)
		# print("HTML:", html)

		_html = os.path.join(folder_temp_pdf, "temp.html")

		with open(_html, 'w') as f:
			f.write(html)

		_pdf = pdfkit.from_file(_html, False, options=options)

		with open(_file, "wb") as f:
			f.write(_pdf)

		print("PDF_GENERATED:", _file)

		# rimuovo il qrcode
		for f in os.listdir(folder_temp_qrcode):
			_f = os.path.join(folder_temp_qrcode, f)
			# print("QRCODE_REMOVE:", _f)
			os.remove(_f)

		return _file
	except Exception as err:
		print("ERRORE_CREAZIONE_PDF_DA_HTML:", err)
		return False
