# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
#                <contact@eficent.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0

import logging
from odoo.addons.l10n_es_aeat.tests.test_l10n_es_aeat_mod_base import \
    TestL10nEsAeatModBase

_logger = logging.getLogger('aeat.303')


class TestL10nEsAeatVatBook(TestL10nEsAeatModBase):

    debug = False
    taxes_sale = {
        # tax code: (base, tax_amount)
        'S_IVA21S': (1500, 315),
    }
    taxes_purchase = {
        # tax code: (base, tax_amount)
        'P_IVA21_SC': (230, 48.3),
    }

    def test_model_vat_book(self):
        # Purchase invoices
        purchase = self._invoice_purchase_create('2017-01-01')
        self._invoice_refund(purchase, '2017-01-18')

        # Sale invoices
        sale = self._invoice_sale_create('2017-01-13')
        self._invoice_refund(sale, '2017-01-14')
        # Create model
        self.company.vat = 'ES12345678Z'
        vat_book = self.env['l10n.es.vat.book'].create({
            'name': 'Test VAT Book',
            'company_id': self.company.id,
            'company_vat': '1234567890',
            'contact_name': 'Test owner',
            'type': 'N',
            'support_type': 'T',
            'contact_phone': '911234455',
            'year': 2017,
            'period_type': '1T',
            'date_start': '2017-01-01',
            'date_end': '2017-03-31',
        })
        _logger.debug('Calculate VAT Book 1T 2017')
        vat_book.button_calculate()
        # Check issued invoices
        for line in vat_book.issued_line_ids:
            self.assertEqual(line.invoice_date, '2017-01-13')
            self.assertEqual(line.partner_id, self.customer)
            for tax_line in line.tax_line_ids:
                self.assertEqual(tax_line.base_amount, 1500)
                self.assertEqual(tax_line.tax_amount, 315)
        # Check issued rectification invoices
        for line in vat_book.rectification_issued_line_ids:
            self.assertEqual(line.invoice_date, '2017-01-14')
            self.assertEqual(line.partner_id, self.customer)
            for tax_line in line.tax_line_ids:
                self.assertEqual(tax_line.base_amount, -1500)
                self.assertEqual(tax_line.tax_amount, -315)
        # Check tax summary for issued invoices
        for line in vat_book.issued_tax_summary_ids:
            self.assertEqual(line.base_amount, 0.0)
            self.assertEqual(line.tax_amount, 0.0)
