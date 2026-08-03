import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from routes import PDF_PREVIEW_ENDPOINT, PDF_PREVIEW_MODE, build_pdf_preview_url


class PdfPreviewPolicyTests(unittest.TestCase):
    def test_preview_url_uses_the_approved_flask_endpoint(self):
        self.assertEqual(PDF_PREVIEW_ENDPOINT, '/api/fetch_pdf_local')
        self.assertEqual(PDF_PREVIEW_MODE, 'iframe')
        self.assertEqual(build_pdf_preview_url('TUNI032'), '/api/fetch_pdf_local?code=TUNI032')
        self.assertEqual(build_pdf_preview_url('TUNI 032'), '/api/fetch_pdf_local?code=TUNI%20032')


if __name__ == '__main__':
    unittest.main()
