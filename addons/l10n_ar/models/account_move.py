# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from lxml import etree
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):

    _inherit = 'account.move'

    @staticmethod
    def _l10n_ar_get_document_number_parts(document_number, document_type_code):
        # import shipments
        if document_type_code in ['66', '67']:
            pos = invoice_number = '0'
        else:
            pos, invoice_number = document_number.split('-')
        return {'invoice_number': int(invoice_number), 'point_of_sale': int(pos)}

    l10n_ar_afip_responsibility_type_id = fields.Many2one(
        'l10n_ar.afip.responsibility.type', string='AFIP Responsibility Type', help='Defined by AFIP to'
        ' identify the type of responsibilities that a person or a legal entity could have and that impacts in the'
        ' type of operations and requirements they need.')

    # TODO make it editable, we have to change move creation method
    l10n_ar_currency_rate = fields.Float(copy=False, digits=(16, 4), readonly=True, string="Currency Rate")

    # Mostly used on reports
    l10n_ar_afip_concept = fields.Selection(
        compute='_compute_l10n_ar_afip_concept', selection='get_afip_invoice_concepts', string="AFIP Concept",
        help="A concept is suggested regarding the type of the products on the invoice but it is allowed to force a"
        " different type if required.")
    l10n_ar_afip_service_start = fields.Date(string='AFIP Service Start Date', readonly=True, states={'draft': [('readonly', False)]})
    l10n_ar_afip_service_end = fields.Date(string='AFIP Service End Date', readonly=True, states={'draft': [('readonly', False)]})

    def get_afip_invoice_concepts(self):
        """ Return the list of values of the selection field. """
        return [('1', 'Products / Definitive export of goods'), ('2', 'Services'), ('3', 'Products and Services'),
                ('4', '4-Other (export)')]

    @api.depends('invoice_line_ids', 'invoice_line_ids.product_id', 'invoice_line_ids.product_id.type', 'journal_id')
    def _compute_l10n_ar_afip_concept(self):
        for rec in self.filtered(lambda x: x.company_id.country_id == self.env.ref('base.ar') and x.l10n_latam_use_documents):
            rec.l10n_ar_afip_concept = rec._get_concept()

    def _get_concept(self):
        """ Method to get the concept of the invoice considering the type of the products on the invoice """
        self.ensure_one()
        invoice_lines = self.invoice_line_ids
        product_types = set([x.product_id.type for x in invoice_lines if x.product_id])
        consumable = set(['consu', 'product'])
        service = set(['service'])
        mixed = set(['consu', 'service', 'product'])
        # Default value "product"
        afip_concept = '1'
        if product_types.issubset(mixed):
            afip_concept = '3'
        if product_types.issubset(service):
            afip_concept = '2'
        if product_types.issubset(consumable):
            afip_concept = '1'
        # on expo invoice you can mix services and products
        if self.l10n_latam_document_type_id.code in ['19', '20', '21'] and afip_concept == '3':
            afip_concept = '1'
        return afip_concept

    def _get_l10n_latam_documents_domain(self):
        self.ensure_one()
        domain = super()._get_l10n_latam_documents_domain()
        if self.journal_id.company_id.country_id == self.env.ref('base.ar'):
            letters = self.journal_id.get_journal_letter(counterpart_partner=self.partner_id.commercial_partner_id)
            domain += ['|', ('l10n_ar_letter', '=', False), ('l10n_ar_letter', 'in', letters)]
            codes = self.journal_id.get_journal_codes()
            if codes:
                domain.append(('code', 'in', codes))
        return domain

    def check_argentinian_invoice_taxes(self):
        _logger.info('Running checks related to argentinian documents')

        # check vat on companies thats has it (Responsable inscripto)
        for inv in self.filtered(lambda x: x.company_id.l10n_ar_company_requires_vat):
            purchase_aliquots = 'not_zero'
            # we require a single vat on each invoice line except from some purchase documents
            if inv.type in ['in_invoice', 'in_refund'] and inv.l10n_latam_document_type_id.purchase_aliquots == 'zero':
                purchase_aliquots = 'zero'
            for line in inv.mapped('invoice_line_ids').filtered(lambda x: x.display_type not in ('line_section', 'line_note')):
                vat_taxes = line.tax_ids.filtered(lambda x: x.tax_group_id.l10n_ar_vat_afip_code)
                if len(vat_taxes) != 1:
                    raise UserError(_('There must be one and only one VAT tax per line. Check line "%s"') % line.name)
                elif purchase_aliquots == 'zero' and vat_taxes.tax_group_id.l10n_ar_vat_afip_code != '0':
                    raise UserError(_('On invoice id "%s" you must use VAT Not Applicable on every line.')  % inv.id)
                elif purchase_aliquots == 'not_zero' and vat_taxes.tax_group_id.l10n_ar_vat_afip_code == '0':
                    raise UserError(_('On invoice id "%s" you must use VAT taxes different than VAT Not Applicable.')  % inv.id)

    @api.model
    def create(self, values):
        if 'partner_id' in values and 'journal_id' not in values:
            values.update(self._prepare_add_missing_fields(values))
        return super().create(values)

    def write(self, values):
        if 'invoice_date' in values:
            for rec in self:
                values.update(self._prepare_add_missing_fields(values))
                super(AccountMove, rec).write(values)
            return True
        else:
            return super().write(values)

    @api.model
    def _prepare_add_missing_fields(self, values):
        """ Deduce missing fields from onchange """
        res = {}
        new_values = self.copy_data()[0] if self else {}
        new_values.update(values)

        # set afip service star/end date if not set
        onchange_fields = ['l10n_ar_afip_service_start', 'l10n_ar_afip_service_end']
        if new_values.get('l10n_ar_afip_concept') and new_values.get('invoice_date') and any(f not in values for f in onchange_fields):
            move = self.new(new_values)
            move.onchange_afip_service_dates()
            for field in onchange_fields:
                if not new_values.get(field):
                    res[field] = move._fields[field].convert_to_write(move[field], move)

        # set proper journal when invoice is created from sale or subscription
        onchange_fields = ['journal_id']
        if new_values.get('partner_id') and not new_values.get('journal_id'):
            move = self.new(new_values)
            move._onchange_partner_journal()
            for field in onchange_fields:
                res[field] = move._fields[field].convert_to_write(move[field], move)
        return res

    @api.onchange('l10n_ar_afip_concept', 'invoice_date')
    def onchange_afip_service_dates(self):
        """ Proper populate service_start_date and service_end_date when needed depending on the invoice_date """
        if self.l10n_ar_afip_concept in ['2', '3', '4']:
            if self.invoice_date:
                if not self.l10n_ar_afip_service_start:
                    self.l10n_ar_afip_service_start = self.invoice_date + relativedelta(day=1)
                if not self.l10n_ar_afip_service_end:
                    self.l10n_ar_afip_service_end = self.invoice_date + relativedelta(day=1, days=-1, months=+1)

    @api.onchange('partner_id')
    def check_afip_responsibility(self):
        if self.company_id.country_id == self.env.ref('base.ar') and self.l10n_latam_use_documents and self.partner_id \
           and not self.partner_id.l10n_ar_afip_responsibility_type_id:
            return {'warning': {
                'title': 'Missing Partner Configuration',
                'message': 'Please configure the AFIP Responsibility for "%s" in order to continue' % (
                    self.partner_id.name)}}

    def get_document_type_sequence(self):
        """ Return the match sequences for the given journal and invoice """
        self.ensure_one()
        if self.journal_id.l10n_latam_use_documents and self.l10n_latam_country_code == 'AR':
            if self.journal_id.l10n_ar_share_sequences:
                return self.journal_id.l10n_ar_sequence_ids.filtered(
                    lambda x: x.l10n_ar_letter == self.l10n_latam_document_type_id.l10n_ar_letter)
            res = self.journal_id.l10n_ar_sequence_ids.filtered(
                lambda x: x.l10n_latam_document_type_id == self.l10n_latam_document_type_id)
            return res
        return super().get_document_type_sequence()

    @api.onchange('partner_id')
    def _onchange_partner_journal(self):
        """ This method is used when the invoice is created from the sale or subscription """
        expo_journals = ['FEERCEL', 'FEEWS', 'FEERCELP']
        for rec in self.filtered(lambda x: x.company_id.country_id == self.env.ref('base.ar') and x.journal_id.type == 'sale'
                                 and x.l10n_latam_use_documents and x.partner_id.l10n_ar_afip_responsibility_type_id):
            res_code = rec.partner_id.l10n_ar_afip_responsibility_type_id.code
            domain = [('company_id', '=', rec.company_id.id), ('l10n_latam_use_documents', '=', True), ('type', '=', 'sale')]
            journal = self.env['account.journal']
            if res_code in ['8', '9', '10'] and rec.journal_id.l10n_ar_afip_pos_system not in expo_journals:
                # if partner is foregin and journal is not of expo, we try to change to expo journal
                journal = journal.search(domain + [('l10n_ar_afip_pos_system', 'in', expo_journals)], limit=1)
            elif res_code not in ['8', '9', '10'] and rec.journal_id.l10n_ar_afip_pos_system in expo_journals:
                # if partner is NOT foregin and journal is for expo, we try to change to local journal
                journal = journal.search(domain + [('l10n_ar_afip_pos_system', 'not in', expo_journals)], limit=1)
            if journal:
                rec.journal_id = journal.id

    def post(self):
        ar_invoices = self.filtered(lambda x: x.company_id.country_id == self.env.ref('base.ar') and x.l10n_latam_use_documents)
        for rec in ar_invoices:
            rec.l10n_ar_afip_responsibility_type_id = rec.commercial_partner_id.l10n_ar_afip_responsibility_type_id.id
            if rec.company_id.currency_id == rec.currency_id:
                l10n_ar_currency_rate = 1.0
            else:
                l10n_ar_currency_rate = rec.currency_id._convert(
                    1.0, rec.company_id.currency_id, rec.company_id, rec.invoice_date or fields.Date.today(), round=False)
            rec.l10n_ar_currency_rate = l10n_ar_currency_rate

        # We make validations here and not with a constraint because we want validaiton before sending electronic
        # data on l10n_ar_edi
        ar_invoices.check_argentinian_invoice_taxes()
        return super().post()

    def _reverse_moves(self, default_values_list=None, cancel=False):
        if not default_values_list:
            default_values_list = [{} for move in self]
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                # TODO enable when we make l10n_ar_currency_rate editable
                # 'l10n_ar_currency_rate': move.l10n_ar_currency_rate,
                'l10n_ar_afip_service_start': move.l10n_ar_afip_service_start,
                'l10n_ar_afip_service_end': move.l10n_ar_afip_service_end,
            })
        return super()._reverse_moves(default_values_list=default_values_list, cancel=cancel)
