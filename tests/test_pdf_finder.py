import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pdf_finder import find_pdf_path


class PdfFinderTests(unittest.TestCase):
    def test_preserves_digits_in_study_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            study_dir = os.path.join(tmpdir, 'T2D6', 'T2D6018')
            os.makedirs(study_dir, exist_ok=True)
            pdf_path = os.path.join(study_dir, 'T2D6018.PDF')
            with open(pdf_path, 'w', encoding='utf-8') as handle:
                handle.write('dummy')

            resolved_path, error = find_pdf_path('T2D6018', tmpdir)

            self.assertIsNone(error)
            self.assertEqual(resolved_path, pdf_path)

    def test_finds_pdf_in_flat_direct_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            direct_dir = os.path.join(tmpdir, 'T2D6018')
            os.makedirs(direct_dir, exist_ok=True)
            pdf_path = os.path.join(direct_dir, 'T2D6018.PDF')
            with open(pdf_path, 'w', encoding='utf-8') as handle:
                handle.write('dummy')

            resolved_path, error = find_pdf_path('T2D6018', tmpdir)

            self.assertIsNone(error)
            self.assertEqual(resolved_path, pdf_path)

    def test_finds_pdf_in_family_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            family_dir = os.path.join(tmpdir, 'TUNI', 'TUNI032')
            os.makedirs(family_dir, exist_ok=True)
            pdf_path = os.path.join(family_dir, 'TUNI032.PDF')
            with open(pdf_path, 'w', encoding='utf-8') as handle:
                handle.write('dummy')

            resolved_path, error = find_pdf_path('TUNI032', tmpdir)

            self.assertIsNone(error)
            self.assertEqual(resolved_path, pdf_path)


if __name__ == '__main__':
    unittest.main()
